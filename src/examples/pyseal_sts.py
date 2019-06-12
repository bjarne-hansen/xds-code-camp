import requests

from uuid import uuid4
from lxml import etree as xml

import pyseal
from pyseal.security import Security
from pyseal.saml import Assertion, AttributeStatement, Attribute, Subject, Conditions
from pyseal.soap import Envelope
from pyseal.sts import RequestSecurityToken


def create_payload():
    #
    # saml:Assertion
    #   saml:Subject
    #    ...
    # TODO: Complete hiererchy

    # Load certificate and key data.
    cert_data = pyseal.x509.load_certificate_data("etc/FOCES_cert.pem")
    key_data = pyseal.x509.load_certificate_data("etc/FOCES_key.pem")

    # Create certificate from data an build SHA-1 hash from certicate.
    cert = pyseal.x509.certificate(cert_data)
    cert_hash = pyseal.x509.certificate_sha1_hash(cert)

    # SAML Assertion
    assertion = Assertion()
    assertion.id = "IDCard"
    assertion.issuer = "PySEAL"

    # SAML Subject
    subject = Subject("46837428", pyseal.dgws.DGWS_NAME_ID_CVRNUMBER)
    assertion.subject = subject

    # SAML Conditions
    conditions = Conditions()
    assertion.conditions = conditions

    # SAML AttributeStatement (IDCardData)
    idc = AttributeStatement("IDCardData")
    idc.attributes.append(Attribute(pyseal.dgws.SOSI_ID_CARD_ID, str(uuid4())))
    idc.attributes.append(Attribute(pyseal.dgws.SOSI_ID_CARD_VERSION, "1.0.1"))
    idc.attributes.append(Attribute(pyseal.dgws.SOSI_ID_CARD_TYPE, "system"))
    idc.attributes.append(Attribute(pyseal.dgws.SOSI_AUTHENTICATION_LEVEL, "3"))
    idc.attributes.append(Attribute(pyseal.dgws.SOSI_OCES_CERT_HASH, cert_hash))
    assertion.attribute_statements.append(idc)

    # SAML AttributeStatement (SystemLog)
    sl = AttributeStatement("SystemLog")
    sl.attributes.append(Attribute(pyseal.dgws.MEDCOM_IT_SYSTEM_NAME, "XDS Code Camp"))
    sl.attributes.append(Attribute(pyseal.dgws.MEDCOM_CARE_PROVIDER_ID, "46837428",
                                   NameFormat=pyseal.dgws.DGWS_NAME_ID_CVRNUMBER))
    sl.attributes.append(Attribute(pyseal.dgws.MEDCOM_CARE_PROVIDER_NAME, "Statens Serum Institut"))
    assertion.attribute_statements.append(sl)

    # Convert assertion object to XML and sign the XML assertion.
    assertion_element = pyseal.xml.to_xml(assertion)
    signed_assertion_element = pyseal.dsig.sign(assertion_element, "IDCard", cert_data, key_data)

    # Create RequestSecurityToken object and assign the signed Assertion to it.
    #
    # wst:RequestSecutityToken
    #   wst:TokenType
    #   wst:RequestType
    #   wst:Claims
    #     saml:Assertion
    #       ...
    #
    rst = RequestSecurityToken()
    rst.assertion = signed_assertion_element

    return rst


def create_request(request_security_token):
    #
    # Create a basic WS-Security element
    #
    # wsse:Security
    #   wsu:Timestamp
    #     wsu:Created
    #
    security = Security()

    #
    # Create SOAP request
    #
    # soap:Envelope
    #   soap:Header
    #     wsse:Security
    #       ...
    #   soap:Body
    #     wst:RequestSecurityToken
    #       ...
    envelope = Envelope(headers=[security], body=request_security_token)

    return envelope


# noinspection PyProtectedMember
def sts_request(url="http://test2.ekstern-test.nspop.dk:8080/sts/services/NewSecurityTokenService", content=None):

    if content is None:
        raise ValueError("The data argument is None.")

    if isinstance(content, Envelope):
        content = xml.tostring(pyseal.xml.to_xml(content))
    elif isinstance(content, xml._Element):
        content = xml.tostring(content)
    else:
        content = str(content)

    sts_response = requests.post(url, data=content)
    return sts_response


def get_sts_assertion():
    request_security_token = create_payload()
    envelope = create_request(request_security_token)
    response = sts_request(content=envelope)
    sts_assertion = pyseal.saml.get_assertion(response)
    return sts_assertion


def main():
    # Build RequestSecurityToken SOAP request.
    request_security_token = create_payload()
    envelope = create_request(request_security_token)

    # Convert to XML and pretty print ...
    envelope_element = pyseal.xml.to_xml(envelope)
    print(xml.tostring(envelope_element, pretty_print=True).decode("utf-8"))

    # Convert SOAP request to string.
    data = xml.tostring(envelope_element, encoding="utf-8",
                        xml_declaration='<?xml version="1.0" encoding="utf-8">').decode("utf-8")

    # Excute request against STS.
    response = sts_request(content=data)

    # Convert response to XML and print it (pretty)
    response_element = xml.fromstring(response.content)
    print(xml.tostring(response_element, pretty_print=True).decode("utf-8"))


if __name__ == "__main__":
    main()
