from datetime import datetime


__all__ = ['Security']


class Security:

    def __init__(self, security_id=None, created=None, assertion=None):
        self.id = security_id
        self.created = created if created is not None else datetime.utcnow()
        self.assertion = assertion
