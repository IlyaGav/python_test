def z_encode(x, y):
    x = (x | x << 16) & 0x0000FFFF
    x = (x | x << 8) & 0x00FF00FF
    x = (x | x << 4) & 0x0F0F0F0F
    x = (x | x << 2) & 0x33333333
    x = (x | x << 1) & 0x55555555

    y = (y | y << 16) & 0x0000FFFF
    y = (y | y << 8) & 0x00FF00FF
    y = (y | y << 4) & 0x0F0F0F0F
    y = (y | y << 2) & 0x33333333
    y = (y | y << 1) & 0x55555555

    return x | (y << 1)


def z_decode(morton):
    x = morton & 0x55555555
    x = (x ^ (x >> 1)) & 0x33333333
    x = (x ^ (x >> 2)) & 0x0F0F0F0F
    x = (x ^ (x >> 4)) & 0x00FF00FF
    x = (x ^ (x >> 8)) & 0x0000FFFF

    y = (morton >> 1) & 0x55555555
    y = (y ^ (y >> 1)) & 0x33333333
    y = (y ^ (y >> 2)) & 0x0F0F0F0F
    y = (y ^ (y >> 4)) & 0x00FF00FF
    y = (y ^ (y >> 8)) & 0x0000FFFF

    return (x, y)


def cmp_zorder(a, b):
    j = 0
    k = 0
    x = 0
    for k in range(2):
        y = a[k] ^ b[k]
        if less_msb(x, y):
            j = k
            x = y
    return a[j] - b[j]


def less_msb(x, y):
    return x < y and x < (x ^ y)
