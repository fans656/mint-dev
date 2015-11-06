def random_bits(length=8):
    import random
    return ''.join('1' if random.randint(0,1) else '0'
            for _ in range(length))

def occurrence_rate(f, n_executions=100, args=(), kwargs={}):
    m = sum(bool(f(*args, **kwargs)) for _ in xrange(n_executions))
    return float(m) / n_executions

#theoretical_compare(f, theoritical_rate, n_samples=100, n_executions=100)

if __name__ == '__main__':
    for _ in range(8):
        print randombits()
