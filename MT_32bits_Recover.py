# !/usr/bin/python3
# Reference
# https://shainer.github.io/crypto/python/matasano/random/2016/10/27/mersenne-twister-p2.html
# https://github.com/python/cpython/blob/23362f8c301f72bbf261b56e1af93e8c52f5b6cf/Modules/_randommodule.c
# https://github.com/eboda/mersenne-twister-recover/blob/master/MTRecover.py

class MT_32bits_Recover:
    def __init__(self):
        self.AMASK = 0x9d2c5680
        self.BMASK = 0xefc60000
        self.idx = 0
        self.N = 624
        self.state = []

    def setstate(self):
        M = 397
        MATRIX_A = 0x9908b0df
        UPPER_MASK = 0x80000000
        LOWER_MASK = 0x7fffffff
        mag01 = [0x00, MATRIX_A]
        kk = 0
        y = 0
        for kk in range(self.N - M):
            y = (self.state[kk] & UPPER_MASK) | (self.state[kk + 1] & LOWER_MASK)
            self.state[kk] = self.state[kk+M] ^ (y >> 1) ^ mag01[y & 0x01]
        kk += 1
        for kkk in range(kk, self.N - 1):
            y = (self.state[kkk] & UPPER_MASK) | (self.state[kkk + 1] & LOWER_MASK)
            self.state[kkk] = self.state[kkk+(M-self.N)] ^ (y >> 1) ^ mag01[y & 0x01]
        self.idx = 0


    def untemper(self, y):
        y ^= (y >> 18)
        y ^= ((y << 15) & self.BMASK)
        a = y << 7
        b = y ^ (a & self.AMASK)
        c = b << 7
        d = y ^ (c & self.AMASK)
        e = d << 7
        f = y ^ (e & self.AMASK)
        g = f << 7
        h = y ^ (g & self.AMASK)
        i = h << 7
        y ^= (i & self.AMASK)

        z = y >> 11
        x = y ^ z
        s = x >> 11
        y = y ^ s
        return y

    def rand(self):
        if self.idx >= self.N:
            self.setstate()
        y = self.state[self.idx]
        self.idx += 1
        y ^= (y >> 11)
        y ^= (y << 7) & self.AMASK
        y ^= (y << 15) & self.BMASK
        y ^= (y >> 18)

        return y

    def recover(self, outputs):
        values = []
        res = 0
        for i in outputs:
            values.append(self.untemper(i))

        if len(outputs) > 624:
            challenge = outputs[624]
            for i in range(0, 625):
                res = values[i:i+624]
                self.state = res
                self.setstate()
                if challenge == self.rand():
                    print(i)
                    break
        else:
            self.state = values
            self.setstate()
        for i in range(625, len(outputs)):
            x = self.rand()
            assert outputs[i] == x

# test
if __name__ == "__main__":    
    import random
    mtr = MT_32bits_Recover()
    r = random.Random(0x31337)

    [r.getrandbits(32) for _ in range(3456)]

    n = [r.getrandbits(32) for _ in range(1000)]
    mtr.recover(n)

    assert r.getrandbits(32) == mtr.rand()
