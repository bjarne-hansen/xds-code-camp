from requests import Response
from lxml import etree as xml
from signxml import XMLSigner
from datetime import datetime, timedelta

from pyseal.util import timestamp
import pyseal

__all__ = ['Assertion', 'Subject', 'Conditions', 'Attribute', 'AttributeStatement', 'get_assertion', 'sign_assertion']


# noinspection PyProtectedMember
def get_assertion(response):

    if response is None:
        raise ValueError("The 'name' parameter is None.")

    if isinstance(response, Response):
        response_element = xml.fromstring(response.content)
    elif isinstance(response, xml._Element):
        response_element = response
    elif isinstance(response, str):
        response_element = xml.fromstring(response)
    else:
        raise TypeError("Invalid response parameter {}.".format(type(response)))

    nodes = response_element.xpath("//saml:Assertion", namespaces=pyseal.xml.ns_saml)
    if len(nodes) > 0:
        sts_assertion_element = nodes[0]
        # sts_assertion_string = xml.tostring(sts_assertion_element)
        return sts_assertion_element
    else:
        return None


def sign_assertion(assertion, key, cert, reference_uri):

    signer = XMLSigner(signature_algorithm="rsa-sha1",
                       digest_algorithm="sha1",
                       c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")

    signed_assertion_element = signer.sign(assertion,
                                           key=key,
                                           cert=cert,
                                           reference_uri=reference_uri)

    return signed_assertion_element


class Assertion:

    def __init__(self, assertion_id=None, issue_instant=timestamp(), version="2.0"):
        self.id = assertion_id
        self.version = version
        self.issue_instant = issue_instant
        self.issuer = None
        self.subject = None
        self.conditions = None
        self.__attribute_statements = []

    @property
    def attribute_statements(self):
        return self.__attribute_statements


class Subject:

    def __init__(self, name_id, name_id_format, keyname="OCESSignature", username=None, password=None):

        self.name_id = name_id
        self.name_id_format = name_id_format
        self.keyname = keyname
        self.username = username
        self.password = password


class Conditions:

    def __init__(self, not_before: datetime = None, not_on_or_after: datetime = None):
        if not_before is None:
            # Not before is set tu current time minus a grace period of 5 minutes.
            not_before = timestamp() - timedelta(minutes=5)

        if not_on_or_after is None:
            # Add default validity period to get expiration time.
            not_on_or_after = not_before + timedelta(hours=24)

        self.not_before = not_before
        self.not_on_or_after = not_on_or_after


class Attribute:

    def __init__(self, *args, **kwargs):

        if len(args) > 0:
            if len(args) == 1:
                self.__name = args[0]
                if "value" in kwargs:
                    self.__value = kwargs["value"]
                    del kwargs["value"]
                else:
                    raise ValueError("Named argument 'value' expected.")
            elif len(args) == 2:
                self.__name = args[0]
                self.__value = args[1]
            else:
                raise ValueError("Zero, one, or two positional arguments expected.")
        else:
            if "name" in kwargs:
                self.__name = kwargs["name"]
                del kwargs["name"]
            else:
                raise ValueError("Named argument 'name' expected.")

            if "value" in kwargs:
                self.__value = kwargs["value"]
                del kwargs["value"]
            else:
                raise ValueError("Named argumemt 'value' expected")
        self.__attributes = kwargs

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def attributes(self):
        return self.__attributes


class AttributeStatement:

    def __init__(self, attribute_statement_id=None):
        if attribute_statement_id is None:
            raise ValueError("AttributeStatement id is required.")
        self.__id = attribute_statement_id
        self.__attributes = []

    @property
    def id(self):
        return self.__id

    @property
    def attributes(self):
        return self.__attributes
