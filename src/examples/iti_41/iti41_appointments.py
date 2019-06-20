import time
import requests
from datetime import datetime
from io import StringIO
from urllib.parse import unquote
from lxml import etree as xml


from uuid import uuid4

import xds.xml
import xds.util
from xds.model import *

from examples.pyseal_sts import get_sts_assertion
import pyseal.xml
from pyseal.security import Security
from pyseal.soap import Envelope, Action, MessageID, To, ReplyTo
from pyseal.dgws import MedcomHeader
from pyseal.hsuid import HsuidHeader, \
    HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER, HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER, HSUID_USER_TYPE, \
    HSUID_SYSTEM_OWNER_NAME, HSUID_SYSTEM_NAME, HSUID_SYSTEM_VERSION, HSUID_ORG_RESPONSIBLE_NAME, \
    HSUID_CITIZEN_USER_RELATION

from pyseal.util import MimeMultipart, split_header, first


def create_signed_assersion():
    # Get signed assertion from STS.
    assertion = get_sts_assertion()
    return assertion


def create_security(assertion):
    # Create WS-Security header with assertion from STS.
    security = Security()
    security.assertion = assertion
    return security


def create_hsuid():
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
    return hsuid_header


def create_medcom_header():
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
    return medcom_header


def create_provide_and_register_request():

    #
    # Generated unique ids.
    # The xdsuuid() function returns a special variant of a uuid v4 that includes a millisecons timestamp.
    #
    document_id = xds.util.xdsuuid()
    document_unique_id = xds.util.xdsuuid()
    document_lid = xds.util.xdsuuid()
    package_id = xds.util.xdsuuid()
    association_id = xds.util.xdsuuid()

    #
    # Create ProvideAndRegisterDocumentSetRequest
    #
    provide_and_register_document_set_request = ProvideAndRegisterDocumentSetRequest()

    #
    # Create the SubmitObjectRequest and assign it to the provide and register document set.
    #
    submit_object_request = SubmitObjectsRequest()
    provide_and_register_document_set_request.submit_object_request = submit_object_request

    #
    # RegistryObjectList (we can register one or more documents in one request).
    #
    rol = RegistryObjectList()
    submit_object_request.registry_object_list = rol

    #
    # ExtrinsicObject (meta-data about document being submitted)
    #
    eo = ExtrinsicObject(document_id,                                               # id: Document being submitted
                         XDS_DOCUMENT_STATUS_APPROVED,                              # status:
                         XDS_TYPE_STABLE,                                           # objectType:
                         document_lid)
    eo.mime_type = "text/xml"                                                       # mime type of content.
    eo.name = Name("Aftale for 2512489996", "en-US", "UTF-8")                       # Name of document.
    rol.extrinsic_objects.append(eo)

    # Slots
    eo.slots.append(Slot("creationTime", "20170531120000"))
    eo.slots.append(Slot("serviceStartTime", "20190101010101"))
    eo.slots.append(Slot("serviceStopTime", "20200101010101"))
    eo.slots.append(Slot("sourcePatientId", PatientIdentifier("2512489996")))

    # Classification: authorInstitution
    slot = Slot("authorInstitution", OrganizationIdentifier("OUH Radiologisk Afdeling (Svendborg)", "242621000016001"))
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_AUTHOR, "", slot=slot))

    # Classification: codingScheme (classCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    slot = Slot("codingScheme", CS_OID_DK_IHE_CLASS_CODE)  # DK IHE Class Code
    name = Name("Klinisk rapport", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_CLASS_CODE, "001", slot=slot, name=name))

    # Classification: codingScheme (formatCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    #   In this case we are submitting an appointment.
    slot = Slot("codingScheme", CS_OID_DK_IHE_FORMAT_CODE)  # DK IHE Format Code
    name = Name("DK PHMR schema", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_FORMAT_CODE, "urn:ad:dk:medcom:appointmentsummary:full",
                                             slot=slot, name=name))

    # Classification: codingScheme (healthcareFacilityCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    slot = Slot("codingScheme", CS_OID_SNOMED)  # DK IHE Healthcare Facility Code (SNOMED)
    name = Name("hjemmesygepleje", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_HEALTHCARE_FACILITY_CODE, "550621000005101",
                                             slot=slot, name=name))

    # Classification: codingScheme (practiceSettingCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    slot = Slot("codingScheme", CS_OID_SNOMED)  # DK IHE Practice Setting Code (SNOMED)
    name = Name("almen medicin", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_PRACTICE_SETTING_CODE, "408443003",
                                             slot=slot, name=name))

    # Classification: codingScheme (typeCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    slot = Slot("codingScheme", CS_OID_LOINC)  # DK IHE Type Code (LOINC)
    name = Name("Dato og tidspunkt for møde mellem patient og sundhedsperson", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_TYPE_CODE, "39289-4", slot=slot, name=name))

    # ExternalIdentifier: patientId
    name = Name("XDSDocumentEntry.patientId")
    ei = ExternalIdentifier(uuid4(), document_id, XDS_DE_PATIENT_ID, PatientIdentifier("2512489996"), name=name)
    eo.external_identifiers.append(ei)

    # ExternalIdentifier: uniqueId
    name = Name("XDSDocumentEntry.uniqueId")
    ei = ExternalIdentifier(uuid4(), document_id, XDS_DE_UNIQUE_ID, document_unique_id, name=name)
    eo.external_identifiers.append(ei)

    #
    # RegistryPackage:
    #
    rp = RegistryPackage(package_id,
                         XDS_DOCUMENT_STATUS_APPROVED,
                         package_id,
                         Name(package_id, "en-US", "UTF-8"))
    rol.registry_packages.append(rp)

    # Slot: submissionTome
    rp.slots.append(Slot("submissionTime", "20170531120000"))

    #
    # Classification: codingScheme (typeCode)
    #   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
    #   Here used as a classification of the SubmissionSet rather than the document as above.
    #   The content type code specifies the action that resulted in one or more documents being submitted within this
    #   SubmissionSet, i.e. it must cover all the documents as such.
    #
    slot = Slot("codingScheme", CS_OID_LOINC)  # DK IHE Type Code (LOINC)
    name = Name("Dato og tidspunkt for møde mellem patient og sundhedsperson", "en-US", "UTF-8")
    rp.classifications.append(Classification(uuid4(), package_id, XDS_DE_CONTENT_TYPE_CODE, "39289-4", slot=slot, name=name))

    # Classification: authorInstitution
    slot = Slot("authorInstitution", OrganizationIdentifier("OUH Radiologisk Afdeling (Svendborg)", "242621000016001"))
    rp.classifications.append(Classification(uuid4(), package_id, XDS_SS_AUTHOR, "", slot=slot))

    # ExternalIdentifier: patientId
    name = Name("XDSSubmissionSet.patientId")
    ei = ExternalIdentifier(uuid4(), package_id, XDS_SS_PATIENT_ID, PatientIdentifier("2512489996"), name=name)
    rp.external_identifiers.append(ei)

    # ExternalIdentifier: uniqueId
    name = Name("XDSSubmissionSet.uniqueId")
    ei = ExternalIdentifier(uuid4(), package_id, XDS_SS_UNIQUE_ID, package_id, name=name)
    rp.external_identifiers.append(ei)

    # ExternalIdentifier: sourceId
    name = Name("XDSSubmissionSet.sourceId")
    ei = ExternalIdentifier(uuid4(), package_id, XDS_SS_SOURCE_ID, package_id, name=name)
    rp.external_identifiers.append(ei)

    # Classification that identifies this as a submission set (IHE XDS)
    rol.classifications.append(Classification(uuid4(), package_id, classification_node=XDS_CN_SUBMISSION_SET))

    # Create Association than includes the document (ExtrinsicObject) in the SubmissionSet (RegistryPackage),
    association = Association(association_id,
                              XDS_AT_HAS_MEMBER,
                              package_id,                                           # SubmissionSet (registry package)
                              document_id,                                          # Document being submitted
                              XDS_DOCUMENT_STATUS_APPROVED)
    rol.associations.append(association)

    association.slots.append(Slot("SubmissionSetStatus", "Original"))
    # association.slots.append(Slot("OriginalStatus", XDS_DOCUMENT_STATUS_APPROVED))
    # association.slots.append(Slot("NewStatus", XDS_DOCUMENT_STATUS_APPROVED))

    # Load Document from file ...
    document = Document.from_file(document_id, 'data/ITI-41-CDA-APPT.xml')
    provide_and_register_document_set_request.documents.append(document)

    # Return complete provide and register document set object hierarchy.
    return provide_and_register_document_set_request


def main():
    #  "http://test1-cnsp.ekstern-test.nspop.dk:8080/drs/proxy"
    #  "http://test2-cnsp.ekstern-test.nspop.dk:8080/drs/proxy"

    # URL to send ITI-41 request to.
    url = "http://test1-cnsp.ekstern-test.nspop.dk:8080/drs/proxy"

    # Create all the parts of the ITI-41 request ...

    # First, get signed assertion from the STS.
    assertion = get_sts_assertion()

    # Create new WS-Security structure including the signed assertion from STS.
    security = Security()
    security.assertion = assertion

    # Create the MEDCOM header.
    medcom_header = MedcomHeader(non_repudiation_receipt="no")

    # Create WS-Adressing elements.
    action = Action("urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b", True)
    message_id = MessageID()
    to = To(url)
    reply_to = ReplyTo("http://www.w3.org/2005/08/addressing/anonymous")

    prdsr = create_provide_and_register_request()

    # Since the ProvideAndRegisterDocumentSetRequest if from the 'xds' module, and not the 'pyseal' module
    # we use the XML serialization from the 'xds' module.
    prdsr_element = xds.xml.to_xml(prdsr)

    # Wrap in soap envelope
    envelope = Envelope([security, medcom_header, action, message_id, to, reply_to], prdsr_element)
    envelope_element = pyseal.xml.to_xml(envelope)

    # Optionally pretty print the SOAP request
    # print(xml.tostring(envelope_element, pretty_print=True).decode("utf-8"))

    # Write SOAP as generated to a file.
    with open("data/iti41/request-soap.xml", "w") as f:
        f.write(xml.tostring(envelope_element).decode())
        f.flush()
        f.close()

    # Create mime from SOAP envelope.
    request = xml.tostring(envelope_element).decode()
    mime = xds.util.to_mime(request, prdsr.documents)

    # Create content type HTTP header for the MIME request.
    content_type = 'multipart/related; ' \
                   'charset="utf-8"; ' \
                   'type="application/xop+xml"; ' \
                   'boundary="{}"; ' \
                   'start="<{}>"; ' \
                   'start-info="application/soap+xml"'.format(mime["boundary"], mime["root"])

    # Set up HTTP headers for request.
    headers = {
        'Content-Type': content_type,
        'SOAPAction': '"urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b"',
        'MIME-Version': '1.0'
    }

    # Write full mime request as generated.
    with open("data/iti41/request-mime.txt", "w", encoding="utf-8") as f:
        for k,v in headers.items():
            f.write(k)
            f.write(": ")
            f.write(v)
            f.write("\n")
        f.write("\n")
        f.write(mime["data"])
        f.flush()
        f.close()

    # Execute request ...
    print("Sending ITI-41 request to {} ...".format(url))
    response = requests.post(url,
                             headers=headers,
                             data=mime["data"].encode("utf-8"))

    # Write response to file.
    with open("data/iti41/response-mime.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
        f.flush()
        f.close()

    # Report success/failure.
    print("\n\nResponse:\nStatus: {}".format(response.status_code))

    if response.status_code == 200:

        # Print response headers ...
        print("\nHeaders:")
        for k, v in response.headers.items():
            print(k, v)

        # Get and split the Content-Type header'
        content_type = split_header(response.headers.get("content-type"))
        if content_type[None] == "multipart/related":

            # Get boundary (MIME separator) and start (Content-ID) from the Content-Type header.
            boundary = content_type["boundary"]
            start = content_type["start"]

            # Parse the MIME response and get the part with the Content-ID specified in the 'start' part of the
            # Content-Type.
            mime = MimeMultipart.parse(boundary, response.text)
            content = mime.content(start)

            if content is not None:
                envelope_element = xml.parse(StringIO(content))
                elements = envelope_element.xpath("//rs:RegistryResponse", namespaces={"rs": "urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0"})
                if len(elements) > 0:
                    response = elements[0]
                    response_status = response.get("status")
                    print("\n\nRegistry response status: {}".format(response_status))
                    if response_status == "urn:oasis:names:tc:ebxml-regrep:ResponseStatusType:Success":
                        print("I don't yehaaa a lot, but this is a yehaaa!")
                else:
                    print("Didn't really find any RegistryResponse. This may be an error.")
            else:
                print("Really? There seems to be no MIME content with Content-ID {}".format(start))
        else:
            print("The response does not seem to be multipart/related. Is this an error?")
    else:
        print("Sorry. Looks like something went wrong. See data/iti41/response-mime.txt for details.")




if __name__ == "__main__":
    main()

