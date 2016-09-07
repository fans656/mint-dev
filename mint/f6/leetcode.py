class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None

def tolink(a, last=False):
    a = map(ListNode, a)
    for i in xrange(len(a) - 1):
        a[i].next = a[i + 1]
    head = a[0] if a else None
    return head if not last else (head, a[-1] if a else None)

def tolist(p):
    a = []
    while p:
        a.append(p.val)
        p = p.next
    return a
