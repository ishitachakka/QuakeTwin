"""
Policies and PPO training for QuakeTwin.

QRLActor: classical linear encoder -> angle encoding (RY) on n qubits ->
          L variational layers of trainable RX, RY per qubit + CNOT chain ->
          <Z> on every qubit -> linear head -> softmax over 3 actions.
MLPActor: classical baseline. `hidden` picks the size; hidden=4 roughly
          matches the QRL actor's parameter count, hidden=64 is a standard PPO.
Both share the same classical critic and the same PPO update, so the only
difference between QRL and PPO runs is the actor.
"""
from __future__ import annotations

import math

import numpy as np
import pennylane as qml
import torch
import torch.nn as nn

from qt_env import RecoveryEnv

N_ACTIONS = 3


def make_qnode(n_qubits: int, n_layers: int):
    dev = qml.device("default.qubit", wires=n_qubits)

    @qml.qnode(dev, interface="torch", diff_method="backprop")
    def circuit(angles, weights):
        # angles: (batch, n_qubits) data-encoding angles (not trainable)
        for q in range(n_qubits):
            qml.RY(angles[:, q], wires=q)
        for l in range(n_layers):
            for q in range(n_qubits):
                qml.RX(weights[l, q, 0], wires=q)
                qml.RY(weights[l, q, 1], wires=q)
            for q in range(n_qubits - 1):
                qml.CNOT(wires=[q, q + 1])
        return [qml.expval(qml.PauliZ(q)) for q in range(n_qubits)]

    return circuit


class QRLActor(nn.Module):
    def __init__(self, obs_dim, n_qubits=2, n_layers=2):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers
        self.encoder = nn.Linear(obs_dim, n_qubits)
        self.weights = nn.Parameter(0.1 * torch.randn(n_layers, n_qubits, 2))
        self.head = nn.Linear(n_qubits, N_ACTIONS)
        self.circuit = make_qnode(n_qubits, n_layers)

    def forward(self, x):
        angles = math.pi * torch.tanh(self.encoder(x))
        z = self.circuit(angles, self.weights)
        z = torch.stack(list(z), dim=-1).float() if isinstance(z, (list, tuple)) else z.float()
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return self.head(z)

    def param_report(self):
        enc = sum(p.numel() for p in self.encoder.parameters())
        circ = self.weights.numel()
        head = sum(p.numel() for p in self.head.parameters())
        return dict(encoder=enc, circuit=circ, head=head, total=enc + circ + head)


class MLPActor(nn.Module):
    def __init__(self, obs_dim, hidden=4):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(), nn.Linear(hidden, N_ACTIONS))

    def forward(self, x):
        return self.net(x)

    def param_report(self):
        t = sum(p.numel() for p in self.parameters())
        return dict(total=t)


class Critic(nn.Module):
    def __init__(self, obs_dim, hidden=32):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(obs_dim, hidden), nn.Tanh(), nn.Linear(hidden, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


def make_envs(n_envs, seed, cond_sampler, **env_kw):
    envs = []
    for k in range(n_envs):
        rng = np.random.default_rng(seed * 1000 + k)
        envs.append(RecoveryEnv(rng=rng, **env_kw, **cond_sampler(rng)))
    return envs


def train_ppo(actor, obs_dim, env_kw, cond_sampler, seed, episodes=400, n_envs=8,
              lr_actor=5e-3, lr_critic=5e-3, gamma=0.99, gae_lam=0.95, clip=0.2,
              epochs=4, minibatch=512, ent_coef=0.01, log_every=None):
    """Train with PPO. Each iteration runs n_envs episodes in parallel.

    One shared policy decides for every road segment, so each segment of
    each episode is a separate trajectory ("lane") for GAE. The
    communication condition of every episode is drawn from `cond_sampler`,
    so the policy is trained across degradation levels.
    Returns the per-episode training curve (mean return per segment, accuracy).
    """
    torch.manual_seed(seed)
    rng_mb = np.random.default_rng(seed)
    critic = Critic(obs_dim)
    opt_a = torch.optim.Adam(actor.parameters(), lr=lr_actor)
    opt_c = torch.optim.Adam(critic.parameters(), lr=lr_critic)
    curve = []
    iters = max(1, episodes // n_envs)
    for it in range(iters):
        envs = make_envs(n_envs, seed * 7919 + it, cond_sampler, **env_kw)
        obs = np.concatenate([e.reset() for e in envs])          # (L, d)
        n = envs[0].n
        buf_o, buf_a, buf_lp, buf_r, buf_v = [], [], [], [], []
        ep_ret = np.zeros(n_envs); ep_cor = np.zeros(n_envs)
        T = envs[0].T
        for t in range(T):
            o = torch.tensor(obs)
            with torch.no_grad():
                dist = torch.distributions.Categorical(logits=actor(o))
                a = dist.sample(); lp = dist.log_prob(a); v = critic(o)
            nxt, rews = [], []
            for k, e in enumerate(envs):
                o2, r, done, info = e.step(a[k * n:(k + 1) * n].numpy())
                nxt.append(o2); rews.append(r)
                ep_ret[k] += r.sum(); ep_cor[k] += info["correct"]
            buf_o.append(o); buf_a.append(a); buf_lp.append(lp)
            buf_r.append(torch.tensor(np.concatenate(rews))); buf_v.append(v)
            obs = np.concatenate(nxt)
        rews = torch.stack(buf_r); vals = torch.stack(buf_v)          # (T, L)
        adv = torch.zeros_like(rews); last = torch.zeros(rews.shape[1])
        for t in reversed(range(T)):
            nv = vals[t + 1] if t + 1 < T else torch.zeros(rews.shape[1])
            delta = rews[t] + gamma * nv - vals[t]
            last = delta + gamma * gae_lam * last
            adv[t] = last
        ret = adv + vals
        O = torch.cat(buf_o); A = torch.cat(buf_a); LP = torch.cat(buf_lp)
        ADV = adv.flatten(); RET = ret.flatten()
        ADV = (ADV - ADV.mean()) / (ADV.std() + 1e-8)
        N = len(A)
        for _ in range(epochs):
            perm = rng_mb.permutation(N)
            for st in range(0, N, minibatch):
                idx = torch.tensor(perm[st:st + minibatch])
                dist = torch.distributions.Categorical(logits=actor(O[idx]))
                ratio = torch.exp(dist.log_prob(A[idx]) - LP[idx])
                pl = -torch.min(ratio * ADV[idx], torch.clamp(ratio, 1 - clip, 1 + clip) * ADV[idx]).mean()
                loss_a = pl - ent_coef * dist.entropy().mean()
                opt_a.zero_grad(); loss_a.backward(); opt_a.step()
                loss_c = ((critic(O[idx]) - RET[idx]) ** 2).mean()
                opt_c.zero_grad(); loss_c.backward(); opt_c.step()
        for k in range(n_envs):
            curve.append((float(ep_ret[k] / n), float(ep_cor[k] / (n * T))))
        if log_every and (it + 1) % log_every == 0:
            r = np.mean([c[0] for c in curve[-n_envs:]]); acc = np.mean([c[1] for c in curve[-n_envs:]])
            print(f"  iter {it+1}/{iters} return/seg={r:.2f} acc={acc:.3f}", flush=True)
    return curve


@torch.no_grad()
def evaluate(actor, env_kw, cond, seeds, episodes_per_seed=1):
    """Greedy evaluation on fixed seeds under one fixed communication condition.

    accuracy = share of all (segment, step) decisions that match the
    severity rule applied to the TRUE condition.
    """
    acc, ret, health, access, cost = [], [], [], [], []
    for s in seeds:
        for ep in range(episodes_per_seed):
            rng = np.random.default_rng(10_000 + s * 100 + ep)
            env = RecoveryEnv(rng=rng, **env_kw, **cond)
            o = env.reset(); R = 0.0; C = 0
            while True:
                a = torch.argmax(actor(torch.tensor(o)), dim=-1).numpy()
                o, r, done, info = env.step(a)
                R += float(r.sum()); C += info["correct"]
                if done:
                    break
            acc.append(C / (env.n * env.T)); ret.append(R / env.n)
            health.append(info["health"]); access.append(info["accessible"]); cost.append(info["cost"])
    return dict(accuracy=float(np.mean(acc)), accuracy_std=float(np.std(acc)),
                ret=float(np.mean(ret)), health=float(np.mean(health)),
                accessible=float(np.mean(access)), cost=float(np.mean(cost)),
                n=len(acc))
