import time
import requests
from datetime import datetime
from io import StringIO
from urllib.parse import unquote
from lxml import etree as xml

import pyseal.xml
from pyseal.security import Security
from pyseal.soap import Envelope
from pyseal.dgws import MedcomHeader
from pyseal.util import MimeMultipart, split_header, first
from pyseal.hsuid import HsuidHeader, \
    HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER, HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER, HSUID_USER_TYPE, \
    HSUID_SYSTEM_OWNER_NAME, HSUID_SYSTEM_NAME, HSUID_SYSTEM_VERSION, HSUID_ORG_RESPONSIBLE_NAME, \
    HSUID_CITIZEN_USER_RELATION

import xds.xml
from xds.model import *

from examples.pyseal_sts import get_sts_assertion


# Get signed assertion from STS.
assertion = get_sts_assertion()
print("Assertion")
print(xml.tostring(assertion))

# Create WS-Security header with assertion from STS.
security = Security()
security.assertion = assertion
print("Security")
print(xml.tostring(pyseal.xml.to_xml(security)))

# Create the MEDCOM header
medcom_header = MedcomHeader(non_repudiation_receipt="no")

# Create the HSUID header
hsuid_header = HsuidHeader()
hsuid_header.id = "hsuid"
hsuid_header.issuer = "XDS Code Camp Sample Code"
hsuid_header[HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER] = "2512489996"
hsuid_header[HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER] = "2512489996"
hsuid_header[HSUID_USER_TYPE] = "nsi:Citizen"
hsuid_header[HSUID_SYSTEM_OWNER_NAME] = "Lakeside"
hsuid_header[HSUID_SYSTEM_NAME] = "XDS Code Camp Sample Code"
hsuid_header[HSUID_SYSTEM_VERSION] = "0.1"
hsuid_header[HSUID_ORG_RESPONSIBLE_NAME] = "lakeside.dk"
hsuid_header[HSUID_CITIZEN_USER_RELATION] = "nsi:Citizen"

# Build RetriveDocumentSetRequest to fetch one document.
rdsr = RetrieveDocumentSetRequest()

# HomeCommunityId (test2)       TODO: Tell that the value is actually not the right value.
# RepositoryUniqueId (test2)
# DocumentUniqueId (MEDCOM)
rdsr.add_document_request("urn:oid:1.2.208.176.43210.8.20.11",
                          "1.2.208.176.43210.8.20.11",
                          "1.2.208.184^0762074171766375104.2674916774698055898.7649316548312")

rdsr_element = xds.xml.to_xml(rdsr)

# Wrap everything in a SOAP envelope
envelope = Envelope([security, medcom_header, hsuid_header], rdsr_element)
envelope_element = pyseal.xml.to_xml(envelope)

request_str = xml.tostring(envelope_element).decode()

request_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Write request to file.
fn = "data/iti43/{}-iti43-request.xml".format(request_timestamp)
with open(fn, "w") as f:
    f.write(xml.tostring(envelope_element, pretty_print=True).decode())

# Send ITI-43 Request to NSP
start_time = time.time()
iti43_response = requests.post("https://test2-cnsp.ekstern-test.nspop.dk:8443/ddsrepository", data=request_str)
end_time = time.time()

print("\nXDS ITI-43 Response:")
print("----------------------")
print("HTTP Status: %s" % iti43_response.status_code)
print("Execution time: %d ms." % (round((end_time - start_time) * 1000)))


# Write response to file.
fn = "data/iti43/{}-iti43-response.xml".format(request_timestamp)
with open(fn, "w", encoding="utf-8") as f:
    for h, v in iti43_response.headers.items():
        f.write("{}: {}\n".format(h, v))
    f.write("\n")
    f.write(iti43_response.text)

if iti43_response.status_code == 200:
    print("\nInterpret raw response:")

    # Display the fill content-type.
    print("Content-Type: {}".format(iti43_response.headers.get("content-type")))

    # Split content type into its (potential) parts.
    content_type = split_header(iti43_response.headers.get("content-type"))

    if content_type[None] == "multipart/related":

        # Get multipart boundary ...
        boundary = content_type["boundary"]

        # Get Content-ID of first message in the multipart/related set of messages.
        # The 'start' value denotes a Content-ID header value of the RetrieveDocumentSetResponse.
        start = content_type["start"]

        # Report on boundary and content-id of the RetrieveDocumentSetResponse
        print("Boundary: {}".format(boundary))
        print("Start: {}".format(start))

        # Parse multipart content using the boundary as separator.
        parts = MimeMultipart.parse(boundary, iti43_response.text)

        # Get the actual ITI-43 response and parse it as XML document.
        print("\nGet RetrieveDocumentSetResponse using Content-ID: {}".format(start))
        content = parts.content(start)

        if content is not None:
            # Parse the RetrieveDocumentSetReponse XML message.
            document = xml.parse(StringIO(content))

            # Check that the response was successful.
            status = document.xpath("//rs:RegistryResponse/@status",
                                    namespaces={"rs": "urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0"})
            print("Status of request: {}".format(first(status)))

            # Get reference to all documents that are referred to in the result.
            content_ids = document.xpath("//xds:Document/xop:Include/@href",
                                         namespaces={"xds": "urn:ihe:iti:xds-b:2007",
                                                     "xop": "http://www.w3.org/2004/08/xop/include"})

            # Print all references (see RFC 2392 Message- and Content-ID URLs)
            print("\nResult document references (RFC 2392):")
            for href in content_ids:
                print("  Reference: {}".format(unquote(href)))

            # If there is at least one result document, fetch it from the mime parts.
            if len(content_ids) > 0:

                # Create Content-ID header value from the content id reference.
                cid = unquote(content_ids[0])
                if cid.startswith("cid:"):
                    cid = cid[4:]
                content_id = "<{}>".format(cid)

                # Get the multipart content referenced by the content id.
                content = parts.content(content_id)
                assert content is not None, "No result document with id {}.".format(unquote(content_ids[0]))

                # Parse the XML(?) document referenced.
                document = xml.parse(StringIO(content))
                print("\nDocument contents:")
                print(xml.tostring(document, pretty_print=True).decode("utf-8"))
            else:
                print("No documents referenced in RetrieveDocumentSetResponse.")
        else:
            print("No RetrieveDocumentSetResponse document found.")
    else:
        print("Not a multipart/related response.")
