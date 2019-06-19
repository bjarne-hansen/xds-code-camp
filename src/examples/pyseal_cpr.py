import requests

import pyseal

from lxml import etree as xml
from time import time

from examples.pyseal_sts import create_payload, create_request, sts_request

from pyseal.security import Security
from pyseal.dgws import MedcomHeader
from pyseal.soap import Envelope


prefix_ns2 = "ns2"
uri_ns2 = "urn:oio:medcom:cprservice:1.0.4"
prefix_none = None
uri_none = "http://rep.oio.dk/cpr.dk/xml/schemas/core/2005/03/18/"
ns_cpr = {prefix_none: uri_none, prefix_ns2: uri_ns2}


def request_security_token():

    # Build RequestSecurityToken SOAP request.
    request_security_token = create_payload()
    envelope = create_request(request_security_token)
    response = sts_request(content=envelope)

#envelope_element = pyseal.xml.to_xml(envelope)

# Print SOAP request (pretty)
#print(xml.tostring(envelope_element, pretty_print=True).decode("utf-8"))

# Convert SOAP request to string.
#data = xml.tostring(envelope_element, encoding="utf-8",
#                    xml_declaration='<?xml version="1.0" encoding="utf-8">').decode("utf-8")

# Excute request against STS.
#response = request_security_token(data=data)

# Convert response to XML and print it (pretty)
    response_element = xml.fromstring(response.content)
    sts_assertion_element = pyseal.saml.get_assertion(response_element)
    return sts_assertion_element
# Extract SAML Assertion element from response using XPath ...
#sts_assertion_element = None
#nodes = response_element.xpath("//saml:Assertion", namespaces=pyseal.xml.ns_saml)
#if len(nodes) > 0:
#    sts_assertion_element = nodes[0]
#    sts_assertion_string = xml.tostring(sts_assertion_element)
#assert sts_assertion_element is not None, "Failed to extract signed SAML Assertion from response."

# Print the SAML Assertion signed by the STS.
#print(xml.tostring(sts_assertion_element, pretty_print=True).decode("utf-8"))

def call_cpr_service():
    sts_assertion_element = request_security_token()
# Build request to CPR lookup service by creating a Securit
    security = Security(assertion=sts_assertion_element)
    medcom_header = MedcomHeader(non_repudiation_receipt="no")

    body_element = xml.Element(xml.QName(uri_ns2, "getPersonWithHealthCareInformationIn"), nsmap=ns_cpr)
    identifier_element = xml.SubElement(body_element, xml.QName(uri_none, "PersonCivilRegistrationIdentifier"))
    identifier_element.text = "0411884953" # "0202999573"
    envelope = Envelope([security, medcom_header], body_element)

    # Convert to XML ...
    envelope_element = pyseal.xml.to_xml(envelope)

# Convert to string ...
    data = xml.tostring(envelope_element)

    # Send SCES Request to NSP
    print("\nCPR Request:")
    print("------------")
    print(xml.tostring(envelope_element, pretty_print=True).decode())
    start_time = time()
    response = requests.post("http://test2.ekstern-test.nspop.dk:8080/stamdata-cpr-ws/service/DetGodeCPROpslag-1.0.4",data=data)
    end_time = time()

    # Process response.
    print("\nCPR Response:")
    print("-------------")
    print("HTTP Status: %s" % response.status_code)
    print("Execution time: %d ms." % (round((end_time - start_time) * 1000)))
    print(xml.tostring(xml.fromstring(response.content), pretty_print=True).decode())


def main():
    call_cpr_service()


if __name__ == '__main__':
    main()
