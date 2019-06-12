import requests
from lxml import etree as xml

import pyseal
from pyseal.soap import Envelope

_default_context = "www.sosi.dk"
_default_token_type = "urn:oasis:names:tc:SAML:2.0:assertion:"
_default_request_type = "http://schemas.xmlsoap.org/ws/2005/02/trust/Issue"
_default_issuer = "PySEAL"

_default_url = "http://test2.ekstern-test.nspop.dk:8080/sts/services/NewSecurityTokenService"

__all__ = ['RequestSecurityToken', 'request_security_token']


class RequestSecurityToken:

    def __init__(self, assertion=None):
        self.assertion = assertion
        self.context = _default_context
        self.token_type = _default_token_type
        self.request_type = _default_request_type
        self.issuer = _default_issuer


# noinspection PyProtectedMember
def request_security_token(url=_default_url, data=None):

    if data is None:
        raise ValueError("The data argument is None.")

    if isinstance(data, Envelope):
        data = pyseal.xml.to_xml(data)
    elif isinstance(data, xml._Element):
        data = xml.tostring(data)
    else:
        data = str(data)

    response = requests.post(url, data=data)
    return response



