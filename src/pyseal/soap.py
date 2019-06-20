from uuid import uuid4

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


class MessageID:

    def __init__(self, message_id=None):
        self.message_id = uuid4() if message_id is None else message_id


class To:

    def __init__(self, to):
        self.to = to


class ReplyTo:

    def __init__(self, reply_to):
        self.reply_to = reply_to