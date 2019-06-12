from datetime import datetime

__all__ = ['Identifier', 'PatientIdentifier', 'AdhocQueryRequest', 'RetrieveDocumentSetRequest',
           'XDS_DE_PATIENT_ID', 'XDS_DE_STATUS', 'XDS_DE_TYPE_CODE', 'XDS_DE_SERVICE_START_TIME_FROM',
           'XDS_DE_SERVICE_STOP_TIME_TO', 'XDS_DE_TYPE',
           'XDS_TYPE_STABLE', 'XDS_TYPE_ON_DEMAND',
           'XDS_QUERY_ID_FIND_DOCUMENTS',
           'XDS_DOCUMENT_STATUS_DEPRECATED', 'XDS_DOCUMENT_STATUS_APPROVED',
           'AUTHORITY_LOINC',
           'LOINC_APPOINTMENT']

#
# XDSDocumentEntry
# See https://www.ihe.net/uploadedFiles/Documents/ITI/IHE_ITI_TF_Vol2a.pdf
# Section 3.18.4.1.2.3.7.1 FindDocuments
#
XDS_DE_PATIENT_ID = "$XDSDocumentEntryPatientId"
XDS_DE_STATUS = "$XDSDocumentEntryStatus"
XDS_DE_TYPE_CODE = "$XDSDocumentEntryTypeCode"
XDS_DE_SERVICE_START_TIME_FROM = "$XDSDocumentEntryServiceStartTimeFrom"
XDS_DE_SERVICE_STOP_TIME_TO = "$XDSDocumentEntryServiceStopTimeTo"
XDS_DE_TYPE = "$XDSDocumentEntryType"

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

AUTHORITY_LOINC = "2.16.840.1.113883.6.1"
LOINC_APPOINTMENT = "39289-4"

URI_QUERY30 = "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0"
URI_RIM30 = "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0"


class Identifier:

    def __init__(self, identifier, authority=None):
        self.__identifier = identifier
        self.__authority = authority

    def __str__(self):
        return "%s^^%s" % (self.__identifier, self.__authority)


class PatientIdentifier:

    def __init__(self, patient_id, scheme=None):
        self.__patient_id = patient_id
        if scheme is None:
            self.__scheme = "&1.2.208.176.1.2&ISO"
        else:
            self.__scheme = scheme

    def __str__(self):
        return "%s^^^%s" % (self.__patient_id, self.__scheme)


class AdhocQueryRequest(dict):

    def __init__(self, *args, **kwargs):
        super(AdhocQueryRequest, self).__init__(*args, **kwargs)
        self.__response_option = XDS_RESPONSE_OPTION_LEAF_CLASS
        self.__query_id = XDS_QUERY_ID_FIND_DOCUMENTS
        self.__query_status = None

    @property
    def query_id(self):
        return self.__query_id

    @query_id.setter
    def query_id(self, query_id):
        self.__query_id = query_id

    @property
    def response_option(self):
        return self.__response_option

    @response_option.setter
    def response_option(self, option):
        self.__response_option = option

    @property
    def query_status(self):
        return self.__query_status

    @query_status.setter
    def query_status(self, status):
        self.__query_status = status

    # def build(self):
    #
    #     builder = XmlUtil.Builder()
    #     builder.namespace({None: URI_QUERY30, "rim": URI_RIM30})
    #
    #     query_attr = {"id": self.__query_id}
    #     if self.__query_status is not None:
    #         query_attr["status"] = self.__query_status
    #
    #     builder.element("AdhocQueryRequest") \
    #                 .value("ResponseOption", None, {"returnType": self.response_option, "returnComposedObjects": "true"}) \
    #                 .element("rim:AdhocQuery", query_attr)
    #
    #     for key in self.keys():
    #         builder.element("rim:Slot", {"name": key})
    #
    #         value = self[key]
    #         if isinstance(value, list):
    #             list_of_values = value
    #             index = 0
    #             value = "("
    #             for e in list_of_values:
    #                 if index > 0:
    #                     value += ","
    #                 value += "'%s'" % str(e)
    #                 index += 1
    #             value += ")"
    #         else:
    #             if isinstance(value, datetime):
    #                 value = value.strftime("%Y%m%d%H%M%S")
    #             else:
    #                 value = str(value)
    #
    #         builder.element("rim:ValueList") \
    #                     .value("rim:Value", value) \
    #                     .up() \
    #                     .up()
    #
    #     return builder.root()


class RetrieveDocumentSetRequest(list):

    def __init__(self, *args, **kwargs):
        super(RetrieveDocumentSetRequest, self).__init__(*args, **kwargs)
        pass

    def add_document_request(self, home_community_id, repository_unique_id, document_unique_id):
        self.append({"HomeCommunityId": home_community_id,
                     "RepositoryUniqueId": repository_unique_id,
                     "DocumentUniqueId": document_unique_id})



# def build_retrieve_document_set_request(rdsr):
#
#     builder = XmlUtil.Builder()
#     builder.namespace({None: "urn:ihe:iti:xds-b:2007"})
#
#     builder.element("RetrieveDocumentSetRequest")
#
#     for dr in rdsr:
#         builder.element("DocumentRequest") \
#                     .value("HomeCommunityId", dr["HomeCommunityId"]) \
#                     .value("RepositoryUniqueId", dr["RepositoryUniqueId"]) \
#                     .value("DocumentUniqueId", dr["DocumentUniqueId"]) \
#                     .up()
#
#     return builder.root()

