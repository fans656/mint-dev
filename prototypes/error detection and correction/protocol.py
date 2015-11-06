class Protocol(object):

    class FalseTransmission(Exception): pass
    class ErrorDetected(FalseTransmission): pass

    def __init__(self, bits=None, error_func=lambda x: x):
        self.error_func = error_func
        if bits:
            self.send(bits)
            self.recv()

    def send(self, bits):
        self.error = ''
        self.bits = bits

        self.bits_before_send = self.bits
        self.before_send()
        self.bits_sent = self.bits

        self.bits = self.error_func(self.bits)
        self.bits_recv = self.bits

    def recv(self):
        try:
            self.after_recv()
        except Protocol.ErrorDetected as e:
            self.error = '   !!!!! {}'.format(e)
            raise
        if self.bits_before_send != self.bits:
            raise Protocol.FalseTransmission

    def before_send(self):
        pass

    def after_recv(self):
        pass

    def show(self):
        print 'Original:  {}'.format(self.bits_before_send)
        print 'Sent:      {}'.format(self.bits_sent)
        print 'Received:  {}{}'.format(self.bits_recv, self.error)
        print 'Processed: {}'.format(self.bits)
