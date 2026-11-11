"""
AES-256-GCM cost and key consumption for QuakeTwin (R1 comment 4.3).

Measures encrypt+decrypt time for DT synchronization-sized messages and
reports how much key material each scheme consumes:
  * AES-256-GCM session keys refreshed every 50 messages (QuakeTwin design)
  * one-time pad (key material = message size)
Also times ML-KEM-768 key establishment if the installed `cryptography`
build provides it.
"""
import json, os, platform, statistics, time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SIZES = [256, 1024, 4096]          # bytes per DT sync message
N = 20000
REFRESH = 50                       # messages per 256-bit session key
out = dict(platform=platform.platform(), machine=platform.machine(), cpus=os.cpu_count(), n_messages=N, results=[])

for size in SIZES:
    key = AESGCM.generate_key(bit_length=256)
    aead = AESGCM(key)
    msg = os.urandom(size)
    lat = []
    for i in range(N):
        nonce = os.urandom(12)
        t = time.perf_counter_ns()
        ct = aead.encrypt(nonce, msg, b"dt-sync")
        pt = aead.decrypt(nonce, ct, b"dt-sync")
        lat.append(time.perf_counter_ns() - t)
        assert pt == msg
    lat_us = [x / 1000 for x in lat]
    mean = statistics.mean(lat_us)
    out["results"].append(dict(
        message_bytes=size,
        enc_dec_mean_us=round(mean, 2),
        enc_dec_p99_us=round(sorted(lat_us)[int(0.99 * N)], 2),
        throughput_MBps=round(size / mean, 1),            # bytes per microsecond == MB/s
        key_bits_per_msg_aes=256 / REFRESH,
        key_bits_per_msg_otp=size * 8,
    ))

try:
    from cryptography.hazmat.primitives.asymmetric import mlkem  # noqa
    from cryptography.hazmat.primitives.asymmetric.mlkem import MLKEM768PrivateKey
    sk = MLKEM768PrivateKey.generate(); pk = sk.public_key()
    t = []
    for _ in range(2000):
        t0 = time.perf_counter_ns(); ss, ct = pk.encapsulate(); ss2 = sk.decapsulate(ct); t.append(time.perf_counter_ns() - t0)
        assert ss == ss2
    out["mlkem768_encap_decap_mean_us"] = round(statistics.mean(t) / 1000, 2)
except Exception as e:  # not available in this build
    out["mlkem768_encap_decap_mean_us"] = None
    out["mlkem_note"] = f"ML-KEM not available in installed cryptography: {type(e).__name__}"

os.makedirs("results", exist_ok=True)
with open("results/aes_bench.json", "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
