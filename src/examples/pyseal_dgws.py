import time
import requests
from copy import deepcopy

from uuid import uuid4
from lxml import etree as xml

from signxml import XMLVerifier

import pyseal
from pyseal.security import Security
from pyseal.saml import Attribute, AttributeStatement, Assertion, Subject, Conditions
from pyseal.soap import Envelope


def create_dgws_header(certificate_data, key_data):

    # Create certificate from data an build SHA-1 hash from certicate.
    cert = pyseal.x509.certificate(certificate_data)
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
    signed_assertion_element = pyseal.saml.sign_assertion(assertion_element, key_data, certificate_data, "IDCard")

    # Add the signed assertion XML to a WS-Security element.
    security = Security()
    security.assertion = signed_assertion_element

    return security


def verify_signature(envelope_element, certificate_data):
    #
    # Verification of XML signature.
    #
    try:

        nodes = envelope_element.xpath("//saml:Assertion", namespaces={pyseal.xml.prefix_saml: pyseal.xml.uri_saml})
        if len(nodes) > 0:
            # deepcopy(nodes[0])
            assertion_element_copy = nodes[0]
            verified_data = XMLVerifier().verify(assertion_element_copy, x509_cert=certificate_data).signed_xml
            return verified_data
        else:
            raise Exception("No saml:Assertion element found.")
    except:
        raise Exception("XML signature verification failed.")


def create_dgws_request(security, body=None):
    # Create SOAP Envelope
    envelope = Envelope(headers=[security], body=body)
    return envelope


def main():
    # Load certificate and key data.
    certificate_data = pyseal.x509.load_certificate_data("etc/FOCES_cert.pem")
    key_data = pyseal.x509.load_certificate_data("etc/FOCES_key.pem")

    # Create the DGWS request using the profiled WS-Security header.
    security = create_dgws_header(certificate_data, key_data)
    envelope = create_dgws_request(security)

    # Convert model classes to XML (DOM).
    envelope_element = pyseal.xml.to_xml(envelope)

    # Just for fun try and verify the signature ...
    verify_signature(envelope_element, certificate_data)

    print("Request:")
    print("--------")
    # Convert XML structure to string ...
    print(xml.tostring(envelope_element, pretty_print=True).decode("utf-8"))
    soap_request = xml.tostring(envelope_element).decode("utf-8")
    start_time = time.time()
    # Send request to our simple server ...
    response = requests.post("http://localhost:5000/dgws", data=soap_request)
    exec_time = round((time.time() - start_time) * 1000)
    print("Response:")
    print("---------")
    print("HTTP Status: %d" % response.status_code)
    print("Execution time: %d ms." % exec_time)
    print(response.content)


if __name__ == '__main__':
    main()
