"""
Key-exchange and authentication cost: classical, PQC, hybrid, and QKD-key options
(R1 comment 4.3; Table ``Cost of One Key Exchange and One Authentication'' in the paper).

For each step, timing is "both sides included": the sum of the initiating side's
crypto op and the responding side's crypto op for one exchange or one
authentication, not a network round trip. Bytes sent is what crosses the wire for
that one step (public keys, ciphertext, signature, or MAC tag), not anything
assumed to be known out of band.

  Key exchange:
    * X25519 (classical ECDH)              -- two public keys exchanged
    * ML-KEM-768 (PQC KEM)                  -- public key + ciphertext
    * X25519 + ML-KEM-768 via HKDF (hybrid) -- both of the above, combined
  Authentication:
    * Ed25519 (classical)                        -- signature + public key
    * ML-DSA-65 (PQC)                            -- signature + public key
    * HMAC-SHA256, QKD-derived key (symmetric)   -- tag only, used as a stand-in
      for the MAC QuakeTwin keys from QKD key material on later rounds
      (Section V-C); no public-key material is needed.

Uses pyca/cryptography (OpenSSL backend).
"""
import json, os, platform, statistics
from pathlib import Path

from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey
from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

try:
    from time import perf_counter_ns
except ImportError:  # pragma: no cover
    from time import time as _t
    perf_counter_ns = lambda: int(_t() * 1e9)

N = 3000
RAW = serialization.Encoding.Raw
RAWFMT = serialization.PublicFormat.Raw


def _stats(ns, bytes_sent):
    us = sorted(x / 1000 for x in ns)
    return dict(mean_us=round(statistics.mean(us), 1),
                p99_us=round(us[int(0.99 * len(us))], 1),
                bytes_sent=bytes_sent)


def bench_x25519():
    """Classical ECDH: both sides exchange public keys, then each derives the shared secret."""
    ns, nbytes = [], None
    for _ in range(N):
        a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
        pa, pb = a.public_key(), b.public_key()
        pab, pbb = pa.public_bytes(RAW, RAWFMT), pb.public_bytes(RAW, RAWFMT)
        t0 = perf_counter_ns()
        ssa = a.exchange(pb)
        ssb = b.exchange(pa)
        ns.append(perf_counter_ns() - t0)
        assert ssa == ssb
        nbytes = len(pab) + len(pbb)
    return _stats(ns, nbytes), ssa


def bench_mlkem768():
    """PQC KEM: the initiator encapsulates against the receiver's public key, the
    receiver decapsulates the ciphertext. The receiver's long-term keypair is not
    timed, matching how often it is reused across many exchanges."""
    sk = MLKEM768PrivateKey.generate()
    pk = sk.public_key()
    pkb = pk.public_bytes_raw()
    ns, ct_len = [], None
    for _ in range(N):
        t0 = perf_counter_ns()
        ss, ct = pk.encapsulate()
        ss2 = sk.decapsulate(ct)
        ns.append(perf_counter_ns() - t0)
        assert ss == ss2
        ct_len = len(ct)
    return _stats(ns, len(pkb) + ct_len), ss


def bench_hybrid(x_stats, x_ss, k_stats, mlkem_ss):
    """X25519 + ML-KEM-768, combined with HKDF, as used on QuakeTwin's QKD-capable
    hops (there, the QKD part replaces the X25519 part; see Section V-C). mean_us
    and p99_us are each the SUM of the two exchanges' own mean/p99 (already
    measured for the classical/PQC rows) plus HKDF's mean -- not an end-to-end
    timing of the two run back to back, so the reported p99 is not itself a
    99th-percentile of any single run. HKDF's own cost is negligible next to
    either exchange, so this mostly affects the label, not the magnitude."""
    ns = []
    for _ in range(N):
        t0 = perf_counter_ns()
        HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
             info=b"quaketwin-hybrid").derive(x_ss + mlkem_ss)
        ns.append(perf_counter_ns() - t0)
    hkdf_mean_us = statistics.mean(x / 1000 for x in ns)
    return dict(mean_us=round(x_stats["mean_us"] + k_stats["mean_us"] + hkdf_mean_us, 1),
                p99_us=round(x_stats["p99_us"] + k_stats["p99_us"] + hkdf_mean_us, 1),
                bytes_sent=x_stats["bytes_sent"] + k_stats["bytes_sent"])


def bench_ed25519():
    """Classical signature: signer signs, verifier verifies. The signer's public
    key is sent along with the signature (first contact), as for ML-DSA below."""
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    pkb = pk.public_bytes(RAW, RAWFMT)
    msg = os.urandom(64)
    ns, sig_len = [], None
    for _ in range(N):
        t0 = perf_counter_ns()
        sig = sk.sign(msg)
        pk.verify(sig, msg)
        ns.append(perf_counter_ns() - t0)
        sig_len = len(sig)
    return _stats(ns, len(pkb) + sig_len)


def bench_mldsa65():
    """PQC signature (FIPS 204), used for QuakeTwin's first-round and join
    authentication (Section V-C)."""
    sk = MLDSA65PrivateKey.generate()
    pk = sk.public_key()
    pkb = pk.public_bytes_raw()
    msg = os.urandom(64)
    ns, sig_len = [], None
    for _ in range(N):
        t0 = perf_counter_ns()
        sig = sk.sign(msg)
        pk.verify(sig, msg)
        ns.append(perf_counter_ns() - t0)
        sig_len = len(sig)
    return _stats(ns, len(pkb) + sig_len)


def bench_mac_qkd():
    """Symmetric MAC keyed with QKD-derived key material, used on QuakeTwin's
    QKD-capable hops after the first round (Section V-C). HMAC-SHA256 is a
    stand-in: no real QKD key-exchange device is in this benchmark. No public
    key crosses the wire, only the tag."""
    key = os.urandom(32)
    msg = os.urandom(64)
    ns, tag_len = [], None
    for _ in range(N):
        t0 = perf_counter_ns()
        h = hmac.HMAC(key, hashes.SHA256()); h.update(msg); tag = h.finalize()
        v = hmac.HMAC(key, hashes.SHA256()); v.update(msg); v.verify(tag)
        ns.append(perf_counter_ns() - t0)
        tag_len = len(tag)
    return _stats(ns, tag_len)


def main():
    out = dict(platform=platform.platform(), machine=platform.machine(),
                cpus=os.cpu_count(), n_runs=N, kex={}, auth={})

    x_stats, x_ss = bench_x25519()
    k_stats, k_ss = bench_mlkem768()
    out["kex"]["x25519"] = dict(type="Classical", **x_stats)
    out["kex"]["mlkem768"] = dict(type="PQC", **k_stats)
    out["kex"]["hybrid_x25519_mlkem768"] = dict(
        type="Hybrid", note="mean_us/p99_us are each the sum of the x25519 and mlkem768 "
        "rows' own mean/p99 (plus negligible HKDF), not an end-to-end timing",
        **bench_hybrid(x_stats, x_ss, k_stats, k_ss))

    out["auth"]["ed25519"] = dict(type="Classical", **bench_ed25519())
    out["auth"]["mldsa65"] = dict(type="PQC", **bench_mldsa65())
    out["auth"]["mac_qkd_derived"] = dict(
        type="Symmetric", note="HMAC-SHA256 stand-in for a MAC keyed with QKD key material",
        **bench_mac_qkd())

    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "kex_auth_bench.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
