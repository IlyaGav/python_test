from typing import List, Tuple

ZERO = 0
MINUS_ONE = -1
ONE = 1

# MASKS: number[] = new Array(33).fill(0).map((_, i) => Math.pow(2, i) - 1)

MASKS = [0] * 33

for i in range(33):
    MASKS[i] = pow(2, i) - 1


class ZCurve:
    def __init__(self, dim, bits, order=None):
        assert dim >= 2, "unsupported dimensions"
        assert 1 <= bits <= 32, "unsupported bits per component"
        self.dim = dim
        self.bits = bits
        self.order = order or list(range(dim))
        self.masks = []
        self.wipe_masks = []
        self.init_masks()

    @staticmethod
    def encode_component(x, bits, dims, offset, out=ZERO):
        for j in range(bits - 1, -1, -1):
            if (x >> j) & ONE:
                out |= ONE << (j * dims + offset)
        return out

    @staticmethod
    def decode_component(z, bits, dims, offset):
        res = 0
        for j in range(bits - 1, -1, -1):
            if (z >> (j * dims + offset)) & ONE:
                res |= 1 << j
        return res

    def init_masks(self):
        for i in range(self.dim):
            self.masks.append(
                self.encode_component(MASKS[self.bits], self.bits, self.dim, self.order[i])
            )

        full_mask = (ONE << (self.dim * self.bits)) - ONE
        for i in range(self.dim * self.bits):
            self.wipe_masks.append(
                self.encode_component(
                    MASKS[self.bits] >> (self.bits - (((i // self.dim) | 0) + 1)),
                    self.bits,
                    self.dim,
                    i % self.dim
                ) ^ full_mask
            )

    def encode(self, p):
        res = ZERO
        for i in range(self.dim):
            res = self.encode_component(p[i], self.bits, self.dim, self.order[i], res)
        return res

    def decode(self, z, out=None):
        out = out or [0] * self.dim
        for i in range(self.dim):
            out[i] = self.decode_component(z, self.bits, self.dim, self.order[i])
        return out

    def split(self, z):
        return [z & mask for mask in self.masks]

    def merge(self, zparts):
        return sum(zparts)

    def range(self, rmin, rmax):
        zmin = self.encode(rmin)
        zmax = self.encode(rmax)
        p = [0] * self.dim
        xd = zmin
        while xd != MINUS_ONE:
            self.decode(xd, p)
            if self.point_in_box(p, rmin, rmax):
                yield xd
                xd += 1
            else:
                xd = self.big_min(xd, zmin, zmax)

    def big_min(self, zcurr, zmin, zmax):
        dim = self.dim
        bigmin = MINUS_ONE
        bit_pos = dim * self.bits - 1
        mask = ONE << bit_pos
        while mask:
            zmin_bit = zmin & mask
            zmax_bit = zmax & mask
            curr_bit = zcurr & mask
            bit_mask = 1 << (bit_pos // dim)

            if not curr_bit:
                if not zmin_bit and zmax_bit:
                    bigmin = self.load_bits(bit_mask, bit_pos, zmin)
                    zmax = self.load_bits(bit_mask - 1, bit_pos, zmax)
                elif zmin_bit:
                    if zmax_bit:
                        return zmin
                    else:
                        raise ValueError("illegal BIGMIN state")
            else:
                if not zmin_bit:
                    if zmax_bit:
                        zmin = self.load_bits(bit_mask, bit_pos, zmin)
                    else:
                        return bigmin
                elif not zmax_bit:
                    raise ValueError("illegal BIGMIN state")

            bit_pos -= 1
            mask >>= ONE

        return bigmin

    def point_in_box(self, p, rmin, rmax):
        for i in range(self.dim):
            x = p[i]
            if x < rmin[i] or x > rmax[i]:
                return False
        return True

    def load_bits(self, mask, bit_pos, z):
        dim = self.dim
        return (
                (z & self.wipe_masks[bit_pos]) |
                self.encode_component(mask, self.bits, dim, bit_pos % dim)
        )
