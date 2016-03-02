import heapq
import operator
import functools
from mint.utils import each

class BatchHeap(object):

    def __init__(self, lt=operator.lt):
        self.a = []
        self.wrapper = functools.partial(Wrapper, lt)

    def push(self, e):
        heapq.heappush(self.a, self.wrapper(e))

    def pop(self):
        e = heapq.heappop(self.a)
        r = [e]
        try:
            while self.a[0] == e:
                r.append(heapq.heappop(self.a))
        except IndexError:
            pass
        return [t.e for t in r]

    def __repr__(self):
        return repr(list(each(self.a).e))

    def __len__(self):
        return len(self.a)

class Wrapper(object):

    def __init__(self, lt, e):
        self.lt = lt
        self.e = e

    def __lt__(self, o):
        return self.lt(self.e, o.e)

    def __eq__(self, o):
        return not (self.lt(self.e, o.e)
                    or self.lt(o.e, self.e))
