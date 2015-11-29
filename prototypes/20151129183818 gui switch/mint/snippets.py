import mint

def block_on(exc):
    def deco(f):
        def f_(*args, **kwargs):
            while True:
                block = kwargs.pop('block', True)
                try:
                    return f(*args, **kwargs)
                except exc:
                    if block:
                        mint.elapse(1)
                    else:
                        raise
        return f_
    return deco
