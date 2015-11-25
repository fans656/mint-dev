from collections import deque
from containerstack import ContainerStack
from batchheap import BatchHeap

class Event(object):

    def __init__(self, name, now, waiters):
        self.name = name
        self.now = now
        self.waiters = waiters

    def __repr__(self):
        return '<{} {}>'.format(self.name, self.now)

class Thread(object):

    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def __repr__(self):
        return '{} {} on {}'.format(
            self.name, self.priority, self.current_event)

def events2waiters(events, waiters):
    for event in events.get():
        for waiter in event.waiters:
            waiter.current_event = event
            waiters.put(waiter)

def loop(f):
    while timeline:
        f()

def step_thread():
    print timeline.get()

def step_same_priorty():
    print timeline.get(depth=1)

def step_same_now():
    print timeline.get(depth=2)

by_now = lambda x,y: x.now < y.now
by_priority = lambda x,y: x.priority > y.priority

timeline = ContainerStack()
timeline.add_layer(container=BatchHeap(by_now),
                   get=BatchHeap.pop,
                   put=BatchHeap.push,
                   broker=events2waiters
                   )
timeline.add_layer(container=BatchHeap(by_priority),
                   get=BatchHeap.pop,
                   put=BatchHeap.push
                   )
timeline.add_layer(container=deque(),
                   get=deque.popleft,
                   put=deque.extend
                   )

thread_f = Thread('f', 0)
thread_g = Thread('g', 1)
thread_h = Thread('h', 1)
timeline.put(Event('Initial', 0, [thread_f]))
timeline.put(Event('Initial', 0, [thread_g]))
timeline.put(Event('Initial', 0, [thread_h]))
timeline.put(Event('Timeout', 1, [thread_f, thread_g]))

loop(step_thread)
#loop(step_same_priorty)
#loop(step_same_now)
