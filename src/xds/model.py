from datetime import datetime
from uuid import uuid4
from urllib.parse import quote

__all__ = [
           'AdhocQueryRequest', 'ResponseOption', 'AdhocQuery',

           'RetrieveDocumentSetRequest', 'DocumentRequest',

           'ProvideAndRegisterDocumentSetRequest',
           'SubmitObjectsRequest', 'Document',
           'RegistryObjectList', 'Association',
           'ExtrinsicObject', 'Slot', 'Classification', 'Name', 'ExternalIdentifier', 'RegistryPackage',

           'Identifier', 'PatientIdentifier', 'OrganizationIdentifier',

           'XDS_DE_PN_PATIENT_ID', 'XDS_DE_PN_STATUS', 'XDS_DE_PN_TYPE_CODE', 'XDS_DE_PN_SERVICE_START_TIME_FROM',
           'XDS_DE_PN_SERVICE_STOP_TIME_TO', 'XDS_DE_PN_TYPE',

           'XDS_DE_AUTHOR', 'XDS_DE_CLASS_CODE', 'XDS_DE_FORMAT_CODE', 'XDS_DE_HEALTHCARE_FACILITY_CODE',
           'XDS_DE_PRACTICE_SETTING_CODE', 'XDS_DE_TYPE_CODE', 'XDS_DE_PATIENT_ID', 'XDS_DE_UNIQUE_ID',
           'XDS_DE_CONTENT_TYPE_CODE',

           'XDS_SS_SOURCE_ID', 'XDS_SS_UNIQUE_ID', 'XDS_SS_PATIENT_ID', 'XDS_SS_AUTHOR', 'XDS_CN_SUBMISSION_SET',

           'XDS_TYPE_STABLE', 'XDS_TYPE_ON_DEMAND',

           'XDS_QUERY_ID_FIND_DOCUMENTS',

           'XDS_DOCUMENT_STATUS_DEPRECATED', 'XDS_DOCUMENT_STATUS_APPROVED',

           'XDS_RESPONSE_OPTION_LEAF_CLASS', 'XDS_RESPONSE_OPTION_OBJECT_REF',

           'XDS_AT_HAS_MEMBER',

           'XDS_AUTHORITY_SOR', 'XDS_AUTHORITY_CPR',

           'CS_OID_DK_IHE_FORMAT_CODE', 'CS_OID_DK_IHE_CLASS_CODE', 'CS_OID_SNOMED', 'CS_OID_LOINC',

           'LOINC_APPOINTMENT'
           ]


#
# XDSDocumentEntry Parameter Names (used in AdhocQueryRequest).
# See https://www.ihe.net/uploadedFiles/Documents/ITI/IHE_ITI_TF_Vol2a.pdf
# Section 3.18.4.1.2.3.7.1 FindDocuments
#
XDS_DE_PN_PATIENT_ID = "$XDSDocumentEntryPatientId"
XDS_DE_PN_STATUS = "$XDSDocumentEntryStatus"
XDS_DE_PN_TYPE_CODE = "$XDSDocumentEntryTypeCode"
XDS_DE_PN_SERVICE_START_TIME_FROM = "$XDSDocumentEntryServiceStartTimeFrom"
XDS_DE_PN_SERVICE_STOP_TIME_TO = "$XDSDocumentEntryServiceStopTimeTo"
XDS_DE_PN_TYPE = "$XDSDocumentEntryType"

#
# DocumentEntryType / objectType
#
XDS_TYPE_STABLE = "urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1"
XDS_TYPE_ON_DEMAND = "urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248"

#
# XDS Stored Query IDs
# See https://www.ihe.net/uploadedFiles/Documents/ITI/IHE_ITI_TF_Vol2a.pdf
# Section 3.18.4.1.2.4 Stored Query IDs
#
XDS_QUERY_ID_FIND_DOCUMENTS = "urn:uuid:14d4debf-8f97-4251-9a74-a90016b0af0d"

#
# Document Status Values
# See https://www.ihe.net/uploadedFiles/Documents/ITI/IHE_ITI_TF_Vol2a.pdf
# Section 3.18.4.1.2.3.6 Valid Document Status Values
#
XDS_DOCUMENT_STATUS_APPROVED = "urn:oasis:names:tc:ebxml-regrep:StatusType:Approved"
XDS_DOCUMENT_STATUS_DEPRECATED = "urn:oasis:names:tc:ebxml-regrep:StatusType:Deprecated"

XDS_RESPONSE_OPTION_LEAF_CLASS = "LeafClass"
XDS_RESPONSE_OPTION_OBJECT_REF = "ObjectRef"

XDS_AT_HAS_MEMBER = "urn:oasis:names:tc:ebxml-regrep:AssociationType:HasMember"

# DocumentEntry constants
XDS_DE_AUTHOR = "urn:uuid:93606bcf-9494-43ec-9b4e-a7748d1a838d"
XDS_DE_CLASS_CODE = "urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a"
XDS_DE_FORMAT_CODE = "urn:uuid:a09d5840-386c-46f2-b5ad-9c3699a4309d"
XDS_DE_HEALTHCARE_FACILITY_CODE = "urn:uuid:f33fb8ac-18af-42cc-ae0e-ed0b0bdb91e1"
XDS_DE_PRACTICE_SETTING_CODE = "urn:uuid:cccf5598-8b07-4b77-a05e-ae952c785ead"
XDS_DE_TYPE_CODE = "urn:uuid:f0306f51-975f-434e-a61c-c59651d33983"
XDS_DE_PATIENT_ID = "urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427"
XDS_DE_UNIQUE_ID = "urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab"
XDS_DE_CONTENT_TYPE_CODE = "urn:uuid:aa543740-bdda-424e-8c96-df4873be8500"

# SubmissionSet constants
XDS_SS_AUTHOR = "urn:uuid:a7058bb9-b4e4-4307-ba5b-e3f0ab85e12d"
XDS_SS_PATIENT_ID = "urn:uuid:6b5aea1a-874d-4603-a4bc-96a0a7b38446"
XDS_SS_UNIQUE_ID = "urn:uuid:96fdda7c-d067-4183-912e-bf5ee74998a8"
XDS_SS_SOURCE_ID = "urn:uuid:554ac39e-e3fe-47fe-b233-965d2a147832"

XDS_CN_SUBMISSION_SET = "urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd"

# Classification Systems.
CS_OID_DK_IHE_CLASS_CODE = "1.2.208.184.100.9"
CS_OID_DK_IHE_FORMAT_CODE = "1.2.208.184.100.10"
CS_OID_SNOMED = "2.16.840.1.113883.6.96"
CS_OID_LOINC = "2.16.840.1.113883.6.1"

# Misc. codes from code systems.
LOINC_APPOINTMENT = "39289-4"


class AssigningAuthority:
    def __init__(self, oid):
        self._oid = oid
        self._id_type = "ISO"

    def __str__(self):
        return "&{}&{}".format(str(self._oid), str(self._id_type))

    @property
    def oid(self):
        return self._oid

    @property
    def type(self):
        return self._id_type


#
# The Danish Central Person Registry (CPR) holds a unique id for people in
# Denmark. Compares to a social security number (SSN) in other countries.
#   See http://oid-info.com/get/1.2.208.176.1.2
#
XDS_AUTHORITY_CPR = AssigningAuthority("1.2.208.176.1.2")

# The Danish Healthcare Organization Registry (SOR) assigns identities to
# organizational units in within the healthcare sector.
#   See http://oid-info.com/get/1.2.208.176.1.1
#
XDS_AUTHORITY_SOR = AssigningAuthority("1.2.208.176.1.1")


class Identifier:

    def __init__(self, identifier, authority=None):
        self.__identifier = identifier
        self.__authority = authority

    def __str__(self):
        return "%s^^%s" % (self.__identifier, self.__authority)


class PatientIdentifier:

    def __init__(self, patient_id, authority=None):
        self._patient_id = patient_id
        self._authority = authority if authority is not None else XDS_AUTHORITY_CPR

    def __str__(self):
        # Encoded as CX, see table 4.1-3 Data Types in IHE_ITI_TF_Rev8-0_Vol3_FT_2011-08-19.pdf
        return "{}^^^{}".format(str(self._patient_id), str(self._authority))

    @property
    def patient_id(self):
        return self._patient_id

    @property
    def authority(self):
        return self._authority


class OrganizationIdentifier:

    def __init__(self, name, organization_id, authority=None):
        self._name = name
        self._id = organization_id
        self._authority = authority if authority is not None else XDS_AUTHORITY_SOR

    def __str__(self):
        # Encoded as XON, see table 4.1-3 Data Types in IHE_ITI_TF_Rev8-0_Vol3_FT_2011-08-19.pdf
        return "{}^^^^^{}^^^^{}".format(str(self._name), str(self._authority), str(self._id))

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def authority(self):
        return self._authority


class AdhocQueryRequest:

    def __init__(self, response_option=None, adhoc_query=None):
        self.response_option = response_option
        self.adhoc_query = adhoc_query


class ResponseOption:

    def __init__(self, return_type, return_composite_objects):
        self.return_type = return_type
        self.return_composite_objects = return_composite_objects


class AdhocQuery:

    def __init__(self, query_id=None):
        self.query_id = query_id
        self._slots = list()

    @property
    def slots(self):
        return self._slots


class DocumentRequest:

    def __init__(self, home_community_id, repository_unique_id, document_unique_id):
        self.home_community_id = home_community_id
        self.repository_unique_id = repository_unique_id
        self.document_unique_id = document_unique_id


class RetrieveDocumentSetRequest:

    def __init__(self):
        self._document_requests = list()

    @property
    def document_requests(self):
        return self._document_requests

    def add_document_request(self, home_community_id, repository_unique_id, document_unique_id):
        self._document_requests.append(DocumentRequest(home_community_id, repository_unique_id, document_unique_id))


class ProvideAndRegisterDocumentSetRequest:
    def __init__(self):
        self.submit_object_request = None
        self._documents = list()

    @property
    def documents(self):
        return self._documents


class SubmitObjectsRequest:
    def __init__(self, submit_object_request_id=None, comment=None):
        self.id = submit_object_request_id
        self.comment = comment
        self.registry_object_list = None


class RegistryObjectList:

    def __init__(self):
        self._extrinsic_objects = list()
        self._registry_packages = list()
        self._classifications = list()
        self._associations = list()

    @property
    def extrinsic_objects(self):
        return self._extrinsic_objects

    @property
    def registry_packages(self):
        return self._registry_packages

    @property
    def classifications(self):
        return self._classifications

    @property
    def associations(self):
        return self._associations


class Association:

    def __init__(self, association_id, association_type, source_object, target_object, status):
        self.association_id = association_id
        self.association_type = association_type
        self.source_object = source_object
        self.target_object = target_object
        self.status = status
        self._slots = list()

    @property
    def slots(self):
        return self._slots


class ExtrinsicObject:

    def __init__(self, extrinsic_object_id, status, object_type, lid):
        self.extrinsic_object_id = extrinsic_object_id
        self.status = status
        self.object_type = object_type
        self.lid = lid
        self._slots = list()
        self._classifications = list()
        self._external_identifiers = list()
        self.mime_type = None
        self.name = None

    @property
    def slots(self):
        return self._slots

    @property
    def classifications(self):
        return self._classifications

    @property
    def external_identifiers(self):
        return self._external_identifiers


class Slot:

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Classification:
    def __init__(self, classification_id, classified_object, classification_scheme=None, node_representation=None,
                 classification_node=None, slot=None, name=None):
        self.classification_id = classification_id
        self.classified_object = classified_object
        self.classification_scheme = classification_scheme
        self.node_represention = node_representation
        self.classification_node = classification_node
        self.slot = slot
        self.name = name


class Name:
    def __init__(self, value, language=None, charset=None):
        self.value = value
        self.language = language
        self.charset = charset


class ExternalIdentifier:

    def __init__(self, external_identifier_id, registry_object, identification_scheme, value, name=None, slot=None):
        self.external_identifier_id = external_identifier_id
        self.registry_object = registry_object
        self.identification_scheme = identification_scheme
        self.value = value
        self.name = name
        self.slot = slot


class RegistryPackage:

    def __init__(self, registry_package_id, status, lid, name=None):
        self.registry_package_id = registry_package_id
        self.status = status
        self.lid = lid
        self._slots = list()
        self.name = name
        self._classifications = list()
        self._external_identifiers = list()

    @property
    def slots(self):
        return self._slots

    @property
    def classifications(self):
        return self._classifications

    @property
    def external_identifiers(self):
        return self._external_identifiers


class Document:

    def __init__(self, document_id, data, encoding="utf-8", domain="urn:ihe:iti:xds-b:2007"):
        # Argument 'data' should be bytes, string
        self.document_id = document_id
        self._cid_uuid = uuid4()
        self._cid_domain = domain
        self._data = data

    @property
    def cid(self):
        """
        Content id as specified in RFC 2392.
        :return:
        """
        return "cid:{}@{}".format(str(self._cid_uuid), quote(str(self._cid_domain)))

    @property
    def mime_cid(self):
        """
        Content-ID as specified in MIME (RFC 2045)
        :return:
        """
        return "<{}@{}>".format(str(self._cid_uuid), str(self._cid_domain))

    @property
    def data(self):
        return self._data

    @staticmethod
    def from_file(document_id, filename, encoding="utf-8", domain="urn:ihe:iti:xds-b:2007"):

        with open(filename, 'r', encoding=encoding) as f:
            data = f.read()
            return Document(document_id, data, encoding=encoding, domain=domain)
