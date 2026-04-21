# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT


def _rev8(x):
    x &= 0xFF
    x = ((x & 0xF0) >> 4) | ((x & 0x0F) << 4)
    x = ((x & 0xCC) >> 2) | ((x & 0x33) << 2)
    x = ((x & 0xAA) >> 1) | ((x & 0x55) << 1)
    return x


def _rev16(x):
    x &= 0xFFFF
    x = ((x & 0xFF00) >> 8) | ((x & 0x00FF) << 8)
    x = ((x & 0xF0F0) >> 4) | ((x & 0x0F0F) << 4)
    x = ((x & 0xCCCC) >> 2) | ((x & 0x3333) << 2)
    x = ((x & 0xAAAA) >> 1) | ((x & 0x5555) << 1)
    return x


def crc16_iso14443a(data):
    crc = 0xC6C6
    for b in data:
        e = _rev8(b)
        crc ^= e << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) & 0xFFFF) ^ 0x1021
            else:
                crc = (crc << 1) & 0xFFFF
    return _rev16(crc) & 0xFFFF


def key_to_u48(key6):
    k = bytes(key6)
    if len(k) != 6:
        raise ValueError("classic key must be 6 bytes")
    return (k[0] << 40) | (k[1] << 32) | (k[2] << 24) | (k[3] << 16) | (k[4] << 8) | k[5]


def uid_tail_u32_be(uid):
    """Last 4 UID bytes as big-endian uint32 (``PICC::tail4`` + ``array_to32``)."""
    u = bytes(uid)
    if len(u) < 4:
        raise ValueError("uid too short")
    t = u[-4:]
    return (t[0] << 24) | (t[1] << 16) | (t[2] << 8) | t[3]


def nt_from_rb(rb4):
    """``array_to32`` on PICC challenge bytes."""
    if len(rb4) < 4:
        raise ValueError("RB")
    return (rb4[0] << 24) | (rb4[1] << 16) | (rb4[2] << 8) | rb4[3]


def byteswap_u32(x):
    x &= 0xFFFFFFFF
    return ((x & 0xFF) << 24) | ((x & 0xFF00) << 8) | ((x >> 8) & 0xFF00) | ((x >> 24) & 0xFF)


def suc_23(nt_swapped_u32):
    """FibonacciLFSR_Right<32,16,14,13,11> × 2 + ``next32`` ×2 → (Ar, suc3)."""
    s = nt_swapped_u32 & 0xFFFFFFFF

    def step():
        nonlocal s
        out = s & 1
        fb = 0
        for bi in (16, 18, 19, 21):
            fb ^= (s >> bi) & 1
        s = (s >> 1) | (fb << 31)
        return out

    def next32():
        v = 0
        for i in range(32):
            v |= step() << i
        return v & 0xFFFFFFFF

    next32()
    next32()
    ar = next32()
    suc3 = next32()
    return ar, suc3


def oddparity8(x):
    x &= 0xFF
    p = 0
    while x:
        p ^= x & 1
        x >>= 1
    return p ^ 1


def append_parity_bitstream(enc_plain, parity_bits):
    """
    Pack ``enc_plain`` bytes with one odd-parity bit after each byte (LSB-first stream).
    ``parity_bits``: low nibble per byte for first 4 bytes, then bits 4..7 for next 4 — same layout as M5 ``encrypt`` return.
    """
    out_len = (len(enc_plain) * 9 + 7) // 8
    buf = bytearray(out_len)
    bitpos = 0
    for i, v in enumerate(enc_plain):
        for k in range(8):
            b = (v >> k) & 1
            if b:
                buf[bitpos >> 3] |= 1 << (bitpos & 7)
            bitpos += 1
        pb = (parity_bits >> i) & 1
        if pb:
            buf[bitpos >> 3] |= 1 << (bitpos & 7)
        bitpos += 1
    return bytes(buf)


# Crypto1: FibonacciLFSR_Left taps from ``MLFSR48<48,5,6,...>`` → 0-based indices
_CRYPTO1_TAPS = (4, 5, 6, 8, 12, 18, 20, 22, 23, 28, 30, 32, 33, 35, 37, 38, 42, 47)


class Crypto1:
    def __init__(self):
        self.st = [0] * 48

    def init(self, key48):
        self.st = [0] * 48
        for i in range(48):
            bi = i >> 3
            bj = i & 7
            rev_i = (bi << 3) + (bj ^ 7)
            bit = (key48 >> rev_i) & 1
            self.st[i] = bit

    @staticmethod
    def _fa(a, b, c, d):
        return (((a or b) ^ (a and d)) ^ (c and ((a ^ b) or d))) & 1

    @staticmethod
    def _fb(a, b, c, d):
        return (((a and b) or c) ^ ((a ^ b) and (c or d))) & 1

    @staticmethod
    def _fc(a, b, c, d, e):
        return ((a or ((b or e) and (d ^ e))) ^ ((a ^ (b and d)) and ((c ^ d) or (b and e)))) & 1

    def filter(self):
        s = self.st
        b5 = self._fb(s[6], s[4], s[2], s[0])
        a4 = self._fa(s[14], s[12], s[10], s[8])
        b3 = self._fb(s[22], s[20], s[18], s[16])
        b2 = self._fb(s[30], s[28], s[26], s[24])
        a1 = self._fa(s[38], s[36], s[34], s[32])
        return self._fc(a1, b2, b3, a4, b5)

    def step(self):
        out = self.st[47]
        fb = 0
        for i in _CRYPTO1_TAPS:
            fb ^= self.st[i]
        new = [0] * 48
        new[0] = fb
        for k in range(1, 48):
            new[k] = self.st[k - 1]
        self.st = new
        return out

    def step_with(self, bit_in, enc=False):
        z = self.filter()
        self.step()
        ext = bit_in ^ (z if enc else 0)
        self.st[0] ^= ext
        return z

    def step8(self, val, enc=False):
        v = 0
        for i in range(8):
            t = self.step_with((val >> i) & 1, enc)
            v |= t << i
        return v

    def step32_in(self, val, enc=False):
        v = 0
        for i in range(32):
            t = self.step_with((val >> (i ^ 24)) & 1, enc)
            v |= t << (24 ^ i)
        return v

    def inject(self, uid_u32, nt_u32, enc=False):
        return self.step32_in(uid_u32 ^ nt_u32, enc)

    def encrypt_stream(self, plain):
        """M5 ``encrypt(out, in, in_len)`` for parity TX: keystream + per-byte odd parity bits."""
        enc = bytearray(len(plain))
        parity = 0
        for i in range(len(plain)):
            ks = self.step8(0)
            enc[i] = plain[i] ^ ks
            z = self.filter()
            parity |= ((z ^ oddparity8(plain[i])) & 1) << i
        return bytes(enc), parity

    def encrypt_ab(self, nr, ar):
        """Second auth phase 8-byte stream; returns parity byte (nibbles) per M5 ``encrypt(buf, Nr, Ar)``."""
        buf = bytearray(8)
        parity = 0
        for i in range(4):
            v = (nr >> ((i ^ 0x03) << 3)) & 0xFF
            buf[i] = self.step8(v) ^ v
            z = self.filter()
            parity |= ((z ^ oddparity8(v)) & 1) << i
        for pos in range(4, 8):
            i = pos - 4
            v = (ar >> (i << 3)) & 0xFF
            ks = self.step8(0x00)
            buf[pos] = ks ^ v
            z = self.filter()
            parity |= ((z ^ oddparity8(v)) & 1) << pos
        return bytes(buf), parity
