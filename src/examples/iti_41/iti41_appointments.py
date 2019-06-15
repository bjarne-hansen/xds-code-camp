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
from xds.model import RetrieveDocumentSetRequest

from examples.pyseal_sts import get_sts_assertion

from uuid import uuid4

#
# # Get signed assertion from STS.
# assertion = get_sts_assertion()
#
# # Create WS-Security header with assertion from STS.
# security = Security()
# security.assertion = assertion
#
# # Create the MEDCOM header
# medcom_header = MedcomHeader(non_repudiation_receipt="no")
#
# # Create the HSUID header
# hsuid_header = HsuidHeader()
# hsuid_header.id = "hsuid"
# hsuid_header.issuer = "XDS Code Camp Sample Code"
# hsuid_header[HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER] = "2512489996"
# hsuid_header[HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER] = "2512489996"
# hsuid_header[HSUID_USER_TYPE] = "nsi:Citizen"
# hsuid_header[HSUID_SYSTEM_OWNER_NAME] = "Lakeside"
# hsuid_header[HSUID_SYSTEM_NAME] = "XDS Code Camp Sample Code"
# hsuid_header[HSUID_SYSTEM_VERSION] = "0.1"
# hsuid_header[HSUID_ORG_RESPONSIBLE_NAME] = "lakeside.dk"
# hsuid_header[HSUID_CITIZEN_USER_RELATION] = "nsi:Citizen"
#

from xds.model import *

XDS_DE_AUTHOR = "urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d"
XDS_DE_CLASS_CODE = "urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a"
XDS_DE_FORMAT_CODE = "urn:uuid:a09d5840-386c-46f2-b5ad-9c3699a4309d"
XDS_DE_HEALTHCARE_FACILITY_CODE = "urn:uuid:f33fb8ac-18af-42cc-ae0e-ed0b0bdb91e1"
XDS_DE_PRACTICE_SETTING_CODE = "urn:uuid:cccf5598-8b07-4b77-a05e-ae952c785ead"
XDS_DE_TYPE_CODE = "urn:uuid:f0306f51-975f-434e-a61c-c59651d33983"
XDS_DE_PATIENT_ID = "urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427"
XDS_DE_UNIQUE_ID = "urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab"
XDS_DE_CONTENT_TYPE_CODE = "urn:uuid:aa543740-bdda-424e-8c96-df4873be8500"

XDS_SS_AUTHOR = "urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d"
XDS_SS_PATIENT_ID = "urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446"
XDS_SS_UNIQUE_ID = "urn:uuid:96fdda7c-d067-4183-912e-bf5ee74998a8"
XDS_SS_SOURCE_ID = "urn:uuid:554ac39e-e3fe-47fe-b233-965d2a147832"

XDS_CN_SUBMISSION_SET = "urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd"

CS_OID_DK_IHE_CLASS_CODE = "1.2.208.184.100.9"
CS_OID_DK_IHE_FORMAT_CODE = "1.2.208.184.100.10"

CS_OID_SNOMED = "2.16.840.1.113883.6.96"
CS_OID_LOINC = "2.16.840.1.113883.6.1"

# Generated unique ids.
document_unique_id = "5810095692724235632.653971985411228666.1508924053323"
document_id = "6506406950972547768.3005222075357642518.1508924053324"
package_id = "8068729215432144472.7462049093652427029.1508924053325"
association_id = "6354836999366958523.1074640606702552246.1505117218674"

#
# Create ProvideAndRegisterDocumentSetRequest
#
provide_and_register_document_set_request = ProvideAndRegisterDocumentSetRequest()

#
#
#
submit_object_request = SubmitObjectRequest()
provide_and_register_document_set_request.submit_object_request = submit_object_request

# RegistryObjectList
rol = RegistryObjectList()
submit_object_request.registry_object_list = rol

# ExtrinsicObject
eo = ExtrinsicObject(document_id,                                               # id: Document being submitted
                     XDS_DOCUMENT_STATUS_APPROVED,                              # status:
                     XDS_TYPE_STABLE,                                           # objectType:
                     "8882987292134516828.9018552530933664388.1505117218657")   # lid: TODO: Generated?

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
name = Name("Klinisk rapport", "en_US")
eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_CLASS_CODE, "001", slot=slot, name=name))

# Classification: codingScheme (formatCode)
#   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
slot = Slot("codingScheme", CS_OID_DK_IHE_FORMAT_CODE)  # DK IHE Format Code
name = Name("DK PHMR schema", "en_US")
eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_FORMAT_CODE, "urn:ad:dk:medcom:phmr:full",
                                         slot=slot, name=name))

# Classification: codingScheme (healthcareFacilityCode)
#   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
slot = Slot("codingScheme", CS_OID_SNOMED)  # DK IHE Healthcare Facility Code (SNOMED)
name = Name("hjemmesygepleje", "en_US")
eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_HEALTHCARE_FACILITY_CODE, "550621000005101",
                                         slot=slot, name=name))

# Classification: codingScheme (practiceSettingCode)
#   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
slot = Slot("codingScheme", CS_OID_SNOMED)  # DK IHE Practice Setting Code (SNOMED)
name = Name("almen medicin", "en_US")
eo.classifications.append(Classification(uuid4(), document_id, XDS_DE_PRACTICE_SETTING_CODE, "408443003",
                                         slot=slot, name=name))

# Classification: codingScheme (typeCode)
#   See DK-IHE_Metadata-Common_Code_systems-Value_sets.xls
slot = Slot("codingScheme", CS_OID_LOINC)  # DK IHE Type Code (LOINC)
name = Name("Dato og tidspunkt for møde mellem patient og sundhedsperson", "da_DK")
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
                     Name(package_id, "en_US"))

rol.registry_packages.append(rp)

# Slot: submissionTome
rp.slots.append(Slot("submissionTime", "20170531120000"))

# Classification: authorInstitution
slot = Slot("authorInstitution", OrganizationIdentifier("OUH Radiologisk Afdeling (Svendborg)", "242621000016001"))
rp.classifications.append(Classification(uuid4(), package_id, XDS_SS_AUTHOR, "", slot=slot))

# Classification: codingScheme (XDS DocumentEntry contentTypeCode) # IHE_ITI_TF_Rev8-0_Vol3_FT Table 4.1-6
slot = Slot("codingScheme", "urn:uuid:aa543740-bdda-424e-8c96-df4873be8500")
name = Name("NscContentType", "en_US", "UTF-8")
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

association.slots.append(Slot("SumissionSetStatus", "Original"))
association.slots.append(Slot("OriginalStatus", XDS_DOCUMENT_STATUS_APPROVED))
association.slots.append(Slot("NewStatus", XDS_DOCUMENT_STATUS_APPROVED))

#
# Convert the lot to XML ...
#
request_element = xds.xml.to_xml(provide_and_register_document_set_request)
print(xml.tostring(request_element, pretty_print=True).decode("utf-8"))