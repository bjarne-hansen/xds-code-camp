

#
# The SOAP Envelope is a simple wrapper around a number of headers and a body.
#
class Envelope:

    def __init__(self, headers: list = None, body=None):
        self.headers = headers
        self.body = body


class Action:

    def __init__(self, action, must_understand=True):
        self.action = action
        self.must_understand = must_understand
