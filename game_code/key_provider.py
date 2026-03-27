import hashlib, platform, uuid

_A = [184, 53, 108, 225]
_B = [151, 145, 94, 22]
_C = [155, 93, 155, 125]
_D = [180, 173, 31, 252]
_M = [220, 165, 50, 37, 214, 157, 42, 252, 184, 53, 108, 225, 155, 93, 155, 125]

def _k() -> bytes:
    _t = []
    _t += [b ^ _M[0 + j] for j, b in enumerate(_B)]
    _t += [b ^ _M[4 + j] for j, b in enumerate(_D)]
    _t += [b ^ _M[8 + j] for j, b in enumerate(_A)]
    _t += [b ^ _M[12 + j] for j, b in enumerate(_C)]
    return bytes(_t)

def _s() -> bytes:
    return hashlib.sha256(str(uuid.getnode()).encode() + platform.node().encode()).digest()[:8]

def get_key(machine_bound: bool = True) -> bytes:
    k = bytearray(_k())
    if machine_bound:
        s = _s()
        for i in range(8): k[i] ^= s[i]
    return bytes(k)
