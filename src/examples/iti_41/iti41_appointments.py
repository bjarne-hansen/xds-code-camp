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
from pyseal.soap import Envelope, Action
from pyseal.dgws import MedcomHeader
from pyseal.hsuid import HsuidHeader, \
    HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER, HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER, HSUID_USER_TYPE, \
    HSUID_SYSTEM_OWNER_NAME, HSUID_SYSTEM_NAME, HSUID_SYSTEM_VERSION, HSUID_ORG_RESPONSIBLE_NAME, \
    HSUID_CITIZEN_USER_RELATION


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
    # Generated unique ids.
    # document_id = "6506406950972547768.3005222075357642518.1508924053324"
    # document_unique_id = "5810095692724235632.653971985411228666.1508924053323"
    # document_lid = "8882987292134516828.9018552530933664388.1505117218657"
    # package_id = "8068729215432144472.7462049093652427029.1508924053325"
    # association_id = "6354836999366958523.1074640606702552246.1505117218674"

    document_id = xds.util.xdsuuid()
    time.sleep(0.127)
    document_unique_id = xds.util.xdsuuid()
    time.sleep(0.127)
    document_lid = xds.util.xdsuuid()
    time.sleep(0.127)
    package_id = xds.util.xdsuuid()
    time.sleep(0.127)
    association_id = xds.util.xdsuuid()

    #
    # Create ProvideAndRegisterDocumentSetRequest
    #
    provide_and_register_document_set_request = ProvideAndRegisterDocumentSetRequest()

    #
    #
    #
    submit_object_request = SubmitObjectsRequest()
    provide_and_register_document_set_request.submit_object_request = submit_object_request

    # RegistryObjectList
    rol = RegistryObjectList()
    submit_object_request.registry_object_list = rol

    # ExtrinsicObject
    eo = ExtrinsicObject(document_id,                                               # id: Document being submitted
                         XDS_DOCUMENT_STATUS_APPROVED,                              # status:
                         XDS_TYPE_STABLE,                                           # objectType:
                         document_lid)

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
    slot = Slot("codingScheme", CS_OID_DK_IHE_FORMAT_CODE)  # DK IHE Format Code
    name = Name("DK PHMR schema", "en-US", "UTF-8")
    eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_FORMAT_CODE, "urn:ad:dk:medcom:phmr:full",
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


    # RegistryPackage:


    rp = RegistryPackage(package_id,
                         XDS_DOCUMENT_STATUS_APPROVED,
                         package_id,
                         Name(package_id, "en-US", "UTF-8"))

    rol.registry_packages.append(rp)

    # Slot: submissionTome
    rp.slots.append(Slot("submissionTime", "20170531120000"))

    # Classification: authorInstitution
    slot = Slot("authorInstitution", OrganizationIdentifier("OUH Radiologisk Afdeling (Svendborg)", "242621000016001"))
    rp.classifications.append(Classification(uuid4(), package_id, XDS_SS_AUTHOR, "", slot=slot))

    # Classification: codingScheme (XDS DocumentEntry contentTypeCode) # IHE_ITI_TF_Rev8-0_Vol3_FT Table 4.1-6
    slot = Slot("codingScheme",  XDS_DE_CONTENT_TYPE_CODE)
    name = Name("NscContentType", "en-US", "UTF-8")
    rp.classifications.append(Classification(uuid4(), package_id, XDS_DE_CONTENT_TYPE_CODE, "NscContentType",
                                             slot=slot, name=name))

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

    rol.classifications.append(Classification(uuid4(), package_id, classification_node=XDS_CN_SUBMISSION_SET))

    association = Association(association_id,
                              XDS_AT_HAS_MEMBER,
                              package_id,   # SubmissionSet (registry package)
                              document_id,  # Document being submitted
                              XDS_DOCUMENT_STATUS_APPROVED)
    rol.associations.append(association)

    association.slots.append(Slot("SubmissionSetStatus", "Original"))
    association.slots.append(Slot("OriginalStatus", XDS_DOCUMENT_STATUS_APPROVED))
    association.slots.append(Slot("NewStatus", XDS_DOCUMENT_STATUS_APPROVED))

    document = Document.from_file(document_id, 'data/ITI-41-CDA-APPT.xml')
    #document = Document.from_file(document_id, 'data/ITI-41-CDA-APPT-test.xml')
    provide_and_register_document_set_request.documents.append(document)

    return provide_and_register_document_set_request


def main():

    # Create all the parts of the ITI-41 request ...
    assertion = get_sts_assertion()
    security = Security()
    security.assertion = assertion

    print("Assertion")
    print(xml.tostring(assertion))
    print("Security")
    print(xml.tostring(pyseal.xml.to_xml(security)))

    medcom_header = MedcomHeader(non_repudiation_receipt="no")
    action = Action("urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b", True)

    prdsr = create_provide_and_register_request()

    # Since the ProvideAndRegisterDocumentSetRequest if from the 'xds' module, and not the 'pyseal' module
    # we use the XML serialization from the 'xds' module.
    prdsr_element = xds.xml.to_xml(prdsr)

    # Wrap in soap envelope
    envelope = Envelope([security, medcom_header, action], prdsr_element)
    envelope_element = pyseal.xml.to_xml(envelope)
    print(xml.tostring(envelope_element, pretty_print=True).decode("utf-8"))

    # Write SOAP as generated.
    with open("data/iti41/request-soap.xml", "w") as f:
        f.write(xml.tostring(envelope_element).decode())
        f.flush()
        f.close()

    # Create mime from SOAP envelope
    request = xml.tostring(envelope_element).decode()
    mime = xds.util.to_mime(request, prdsr.documents)

    print("Mime root={}".format(mime["root"]))
    print("Mime boundary={}".format(mime["boundary"]))
    print("Mime data:")
    print(mime["data"])
    part1 = mime["data"].split("--" + mime["boundary"] + "\n")[1]
    payload1 = part1.split("\n\n", 1)[1]
    print(payload1)

    # Write SOAP extracted from mime
    with open("data/iti41/request-soap-mime.xml", "w") as f:
       f.write(payload1)
       f.flush()
       f.close()

    content_type = 'multipart/related; ' \
                   'charset="utf-8"; ' \
                   'type="application/xop+xml"; ' \
                   'boundary="{}"; ' \
                   'start="<{}>"; ' \
                   'start-info="text/xml"'.format(mime["boundary"], mime["root"])
    headers = {
        'Content-Type': content_type
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

    response = requests.post("http://test2-cnsp.ekstern-test.nspop.dk:8080/drs/proxy",
                             headers=headers,
                             data=mime["data"].encode("utf-8"))
    print("\n\nResponse:\nStatus: {}".format(response.status_code))
    print(response.text)


if __name__ == "__main__":
    main()
