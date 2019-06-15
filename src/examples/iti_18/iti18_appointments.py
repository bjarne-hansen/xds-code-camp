from lxml import etree as xml
from datetime import datetime
import time
import requests
from uuid import uuid4

import pyseal
import pyseal.util

from pyseal.security import Security
from pyseal.soap import Envelope
from pyseal.dgws import MedcomHeader

from pyseal.hsuid import HsuidHeader, \
    HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER, HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER, HSUID_USER_TYPE, \
    HSUID_SYSTEM_OWNER_NAME, HSUID_SYSTEM_NAME, HSUID_SYSTEM_VERSION, HSUID_ORG_RESPONSIBLE_NAME, \
    HSUID_CITIZEN_USER_RELATION

import xds
from xds.model import *

from examples.pyseal_sts import get_sts_assertion


def main():

    # Get signed assertion from STS.
    assertion = get_sts_assertion()

    # Create WS-Security header with assertion from STS.
    security = Security()
    security.assertion = assertion

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

    # Build the XDS AdhocQueryRequest
    adhoc_query_request = AdhocQueryRequest()

    # Add ResponseOption
    response_option = ResponseOption(XDS_RESPONSE_OPTION_LEAF_CLASS, "true")
    adhoc_query_request.response_option = response_option

    # Add AddhocQuery
    adhoc_query = AdhocQuery(XDS_QUERY_ID_FIND_DOCUMENTS)
    adhoc_query.slots.append(Slot(XDS_DE_PN_PATIENT_ID, PatientIdentifier("2512489996")))
    adhoc_query.slots.append(Slot(XDS_DE_PN_STATUS, [XDS_DOCUMENT_STATUS_APPROVED]))
    adhoc_query.slots.append(Slot(XDS_DE_PN_TYPE_CODE, [Identifier(LOINC_APPOINTMENT, CS_OID_LOINC)]))
    adhoc_query.slots.append(Slot(XDS_DE_PN_SERVICE_START_TIME_FROM, datetime(2017, 12, 31)))
    adhoc_query.slots.append(Slot(XDS_DE_PN_SERVICE_STOP_TIME_TO, datetime(2018, 12, 31)))
    adhoc_query.slots.append(Slot(XDS_DE_PN_TYPE, XDS_TYPE_ON_DEMAND))
    adhoc_query_request.adhoc_query = adhoc_query

    # Convert to XML ...
    adhoc_query_request_element = xds.xml.to_xml(adhoc_query_request)

    #
    # Wrap everything in a SOAP envelope
    #
    # soap:Envelope
    #   soap:Header
    #     wsse:Security
    #       ...
    #     medcom:MedcomHeader
    #       ...
    #     hsuid:HsuidHeader
    #       ...
    #   soap:Body
    #     AdHocQueryRequest
    #       ...
    #
    envelope = Envelope([security, medcom_header, hsuid_header], adhoc_query_request_element)
    envelope_element = pyseal.xml.to_xml(envelope)
    request_str = xml.tostring(envelope_element).decode()

    #
    # Now, everything is ready to send ITI-18 request to NSP ...
    #

    # Create a request timestamp as string.
    request_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Write request to file.
    fn = "data/iti18/{}-iti18-request.xml".format(request_timestamp)
    with open(fn, "w") as f:
        f.write(xml.tostring(envelope_element, pretty_print=True).decode())

    # Send request to NSP
    print("\nXDS ITI-18 Request ...")
    start_time = time.time()
    iti18_response = requests.post("https://test2-cnsp.ekstern-test.nspop.dk:8443/ddsregistry",
                                   data=request_str)
    end_time = time.time()
    print("Got ITI-18 response in %d ms." % (round((end_time - start_time) * 1000)))

    iti18_response_element = xml.fromstring(iti18_response.text)

    # Write response to file.
    fn = "data/iti18/{}-iti18-response.xml".format(request_timestamp)
    with open(fn, "w") as f:
        f.write(xml.tostring(iti18_response_element, pretty_print=True).decode())

    # Find all ExtrinsicObject elements using XPath.
    ns = {"rim": "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0"}
    result = iti18_response_element.xpath("//rim:ExtrinsicObject", namespaces=ns)

    # Process each ExtrinsicObject element and extract central information from each.
    idx = 1
    for e in result:

        evaluator = xml.XPathElementEvaluator(e, namespaces=ns)

        # Extract data from each ExtrinsicObject.
        status = e.get("status")
        home_community_id = e.get("home")
        repository_unique_id = pyseal.util.first(evaluator("rim:Slot[@name='repositoryUniqueId']/"
                                                           "rim:ValueList/rim:Value/text()"))
        unique_id = pyseal.util.first(evaluator("rim:ExternalIdentifier[rim:Name/rim:LocalizedString/"
                                                "@value='XDSDocumentEntry.uniqueId']/@value"))
        patient_id = pyseal.util.first(evaluator("rim:ExternalIdentifier[rim:Name/rim:LocalizedString/"
                                                 "@value='XDSDocumentEntry.patientId']/@value"))
        service_start_time = pyseal.util.first(evaluator("rim:Slot[@name='serviceStartTime']/"
                                                         "rim:ValueList/rim:Value/text()"))
        service_stop_time = pyseal.util.first(evaluator("rim:Slot[@name='serviceStopTime']/"
                                                        "rim:ValueList/rim:Value/text()"))

        # Print information about response.
        if home_community_id is not None:
            print(idx, ":",
                  status, ",",
                  patient_id, ",",
                  service_start_time, ",",
                  service_stop_time, "\n    ",
                  home_community_id, ",",
                  repository_unique_id, ",",
                  unique_id)
        else:
            print(idx, "Invalid meta-data entry.")

        idx += 1


if __name__ == '__main__':
    main()
