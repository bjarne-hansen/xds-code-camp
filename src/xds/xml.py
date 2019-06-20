
# Import of library packages.
from lxml import etree as xml
from datetime import datetime
from uuid import uuid4, UUID
import io

# Import of own model package.
from xds.model import *

__all__ = ['to_xml']

# Definition of namespace uri and prefixes.
uri_query = "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0"
prefix_query = None

uri_rim = "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0"
prefix_rim = "rim"

uri_lcm = "urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0"
prefix_lcm = "lcm"

uri_xdsb = "urn:ihe:iti:xds-b:2007"
prefix_xdsb = None

uri_xop = "http://www.w3.org/2004/08/xop/include"
prefix_xop = "xop"


# Function to recursively serialize xds.model objects into a XML document (etree).
def to_xml(obj):

    if isinstance(obj, str):
        # A string is just a string ...
        return obj

    if isinstance(obj, bool):
        if obj:
            return "true"
        else:
            return "false"

    elif isinstance(obj, UUID):
        # UUIDs are encoded using the urn:uuid scheme as per RFC 4122.
        return "urn:uuid:{}".format(str(obj))

    elif isinstance(obj, PatientIdentifier):
        # PatientIdentifier encoded as HL7 CX datatype.
        # See table 4.1-3 Data Types in IHE_ITI_TF_Rev8-0_Vol3_FT_2011-08-19.pdf
        return str(obj)

    elif isinstance(obj, OrganizationIdentifier):
        # OrganizationIdentifier encoded as HL7 XON data type.
        # See table 4.1-3 Data Types in IHE_ITI_TF_Rev8-0_Vol3_FT_2011-08-19.pdf
        return str(obj)

    elif isinstance(obj, AdhocQueryRequest):

        #
        # AdhocQueryRequest used in ITI-18.
        #
        # AdhocQueryRequest
        #   ResponseOption
        #   rim:AdhocQuery
        #     ...
        #
        adhoc_query_request_element = xml.Element(xml.QName(prefix_query, "AdhocQueryRequest"),
                                                  nsmap={prefix_query: uri_query, prefix_rim: uri_rim})

        if obj.response_option is not None:
            response_option_element = to_xml(obj.response_option)
            adhoc_query_request_element.append(response_option_element)

        if obj.adhoc_query is not None:
            adhoc_query_element = to_xml(obj.adhoc_query)
            adhoc_query_request_element.append(adhoc_query_element)

        return adhoc_query_request_element

    elif isinstance(obj, ResponseOption):
        #
        # ResponseOption @returnType @returnCompositeObjects
        attrs = dict()
        if obj.return_type is not None:
            attrs["returnType"] = to_xml(obj.return_type)
        if obj.return_composite_objects is not None:
            attrs["returnComposedObjects"] = to_xml(obj.return_composite_objects)
        response_option = xml.Element(xml.QName(uri_query, "ResponseOption"), attrs)

        return response_option

    elif isinstance(obj, AdhocQuery):

        attrs = dict()
        if obj.query_id is not None:
            attrs["id"] = to_xml(obj.query_id)
        adhoc_query_element = xml.Element(xml.QName(uri_rim, "AdhocQuery"), attrs, nsmap={prefix_rim: uri_rim})

        for s in obj.slots:
            if isinstance(s, Slot):
                slot_element = to_xml(s)
                adhoc_query_element.append(slot_element)
            else:
                raise TypeError("AdhocQuery.slots expected element instance of Slot "
                                "but got {}.".format(type(obj)))

        return adhoc_query_element
        # for key in obj.keys():
        #     attrs = {"name": key}
        #     slot_element = xml.SubElement(adhoc_query_element, xml.QName(uri_rim, "Slot"), attrs)
        #
        #     value = obj[key]
        #
        #     if isinstance(value, list):
        #         list_of_values = value
        #         index = 0
        #         value = "("
        #         for e in list_of_values:
        #             if index > 0:
        #                 value += ","
        #             value += "'%s'" % str(e)
        #             index += 1
        #         value += ")"
        #     else:
        #         if isinstance(value, datetime):
        #             value = value.strftime("%Y%m%d%H%M%S")
        #         else:
        #             value = str(value)
        #
        #     value_list_element = xml.SubElement(slot_element, xml.QName(uri_rim, "ValueList"))
        #     value_element = xml.SubElement(value_list_element, xml.QName(uri_rim, "Value"))
        #     value_element.text = value

    elif isinstance(obj, RetrieveDocumentSetRequest):

        #
        # RetrieveDocumentSetRequest used in ITI-43
        #
        # RetrieveDocumentSetRequest
        #   DocumentRequest
        #   ...
        #
        retrieve_document_set_request_element = \
            xml.Element(xml.QName(uri_xdsb, "RetrieveDocumentSetRequest"), nsmap={prefix_xdsb: uri_xdsb})

        for dr in obj.document_requests:
            if isinstance(dr, DocumentRequest):
                document_request_element = to_xml(dr)
                retrieve_document_set_request_element.append(document_request_element)
            else:
                raise TypeError("RetrieveDocumentSetRequest.document_requests expected element instance of "
                                "DocumentRequest but got {}.".format(type(dr)))

        # for document_request in obj.document_requests:
        #     document_request_element = \
        #         xml.SubElement(retrieve_document_set_request_element, xml.QName(uri_xdsb, "DocumentRequest"))
        #
        #     home_community_id_element = \
        #         xml.SubElement(document_request_element, xml.QName(uri_xdsb, "HomeCommunityId"))
        #     home_community_id_element.text = document_request["HomeCommunityId"]
        #
        #     repository_unique_id_element = \
        #         xml.SubElement(document_request_element, xml.QName(uri_xdsb, "RepositoryUniqueId"))
        #     repository_unique_id_element.text = document_request["RepositoryUniqueId"]
        #
        #     document_unique_id = xml.SubElement(document_request_element, xml.QName(uri_xdsb, "DocumentUniqueId"))
        #     document_unique_id.text = document_request["DocumentUniqueId"]

            return retrieve_document_set_request_element

    elif isinstance(obj, DocumentRequest):
        #
        # DocumentRequest
        #   HomeCommunityId
        #   RepositoryUniqueId
        #   DocumentUniqueId
        #
        document_request_element = xml.Element(xml.QName(uri_xdsb, "DocumentRequest"))

        child_element = xml.SubElement(document_request_element, xml.QName(uri_xdsb, "HomeCommunityId"))
        child_element.text = obj.home_community_id

        child_element = xml.SubElement(document_request_element, xml.QName(uri_xdsb, "RepositoryUniqueId"))
        child_element.text = obj.repository_unique_id

        child_element = xml.SubElement(document_request_element, xml.QName(uri_xdsb, "DocumentUniqueId"))
        child_element.text = obj.document_unique_id

        return document_request_element

    elif isinstance(obj, ProvideAndRegisterDocumentSetRequest):
        #
        # ProvideAndRegiterDocumentSetRequest
        #   SubmitObjectRequest
        #     ...
        #  Document
        #    ...
        #  ...
        #
        prdsr = xml.Element(xml.QName(uri_xdsb, "ProvideAndRegisterDocumentSetRequest"),
                            nsmap={prefix_xdsb: uri_xdsb, prefix_lcm: uri_lcm, prefix_rim: uri_rim})

        if obj.submit_object_request is not None:
            if isinstance(obj.submit_object_request, SubmitObjectsRequest):
                sor_element = to_xml(obj.submit_object_request)
                prdsr.append(sor_element)
            else:
                raise TypeError("ProvideAndRegisterDocumentSet.submit_object_request expected instance of "
                                "SubmitObjectsRequest but got {}.".format(type(obj.submit_object_request)))

        for d in obj.documents:
            if isinstance(d, Document):
                document_element = to_xml(d)
                prdsr.append(document_element)
            else:
                raise TypeError("ProvideAndRegisterDocumentSet.documents expected element instance of "
                                "Document but got {}.".format(type(d)))

        return prdsr

    elif isinstance(obj, Document):
        #
        # Document
        #   Include @href
        #

        attrs = dict()
        attrs["id"] = obj.document_id
        document_element = xml.Element(xml.QName(uri_xdsb, "Document"), attrib=attrs)

        attrs = dict()
        attrs["href"] = obj.cid
        xml.SubElement(document_element, xml.QName(uri_xop, "Include"), attrib=attrs, nsmap={prefix_xop: uri_xop})

        return document_element

    elif isinstance(obj, SubmitObjectsRequest):

        attrs = dict()
        if obj.id is not None:
            attrs["id"] = to_xml(obj.id)
        if obj.comment is not None:
            attrs["comment"] = to_xml(obj.comment)

        sor_element = xml.Element(xml.QName(uri_lcm, "SubmitObjectsRequest"), attrs)

        if obj.registry_object_list is not None:
            if isinstance(obj.registry_object_list, RegistryObjectList):
                rol_element = to_xml(obj.registry_object_list)
                sor_element.append(rol_element)
            else:
                raise TypeError("SubmitObjectsRequest.registry_object_list expected instance of RegistryObjectList "
                                "but got {}.".format(type(obj.registry_object_list)))

        return sor_element

    elif isinstance(obj, RegistryObjectList):

        rol_element = xml.Element(xml.QName(uri_rim, "RegistryObjectList"))

        for eo in obj.extrinsic_objects:
            if isinstance(eo, ExtrinsicObject):
                eo_element = to_xml(eo)
                rol_element.append(eo_element)
            else:
                raise TypeError("RegistryObjectList.extrinsic_objects expected element instance of "
                                "ExtrinsicObject but got {}.".format(type(eo)))

        for rp in obj.registry_packages:
            if isinstance(rp, RegistryPackage):
                rp_element = to_xml(rp)
                rol_element.append(rp_element)
            else:
                raise TypeError("RegistryObjectList.registry_packages expected element instance of "
                                "RegistryPackage but got {}.".format(type(rp)))

        for c in obj.classifications:
            if isinstance(c, Classification):
                c_element = to_xml(c)
                rol_element.append(c_element)
            else:
                raise TypeError("RegistryObjectList.classifications expected element instance of "
                                "Classification but got {}.".format(type(c)))

        for a in obj.associations:
            if isinstance(a, Association):
                a_element = to_xml(a)
                rol_element.append(a_element)
            else:
                raise TypeError("RegistryObjectList.association expected element instance of "
                                "Association but got {}.".format(type(a)))

        return rol_element

    elif isinstance(obj, ExtrinsicObject):

        attrs = dict()
        if obj.extrinsic_object_id is not None:
            attrs["id"] = to_xml(obj.extrinsic_object_id)
        if obj.status is not None:
            attrs["status"] = to_xml(obj.status)
        if obj.object_type is not None:
            attrs["objectType"] = to_xml(obj.object_type)
        if obj.lid is not None:
            attrs["lid"] = to_xml(obj.lid)
        if obj.mime_type is not None:
            attrs["mimeType"] = to_xml(obj.mime_type)

        eo_element = xml.Element(xml.QName(uri_rim, "ExtrinsicObject"), attrs)

        for s in obj.slots:
            if isinstance(s, Slot):
                s_element = to_xml(s)
                eo_element.append(s_element)
            else:
                raise TypeError("ExtrinsicObject.slots expected element instance of "
                                "Slot but got {}.".format(type(s)))

        if obj.name is not None:
            if isinstance(obj.name, Name):
                name_element = to_xml(obj.name)
                eo_element.append(name_element)
            else:
                raise TypeError("ExtrinsicObject.name expected instance of Name but got {}.".format(type(obj.name)))

        for c in obj.classifications:
            if isinstance(c, Classification):
                c_element = to_xml(c)
                eo_element.append(c_element)
            else:
                raise TypeError("ExtrinsicObject.classifications expected element instance of "
                                "Classification but got {}.".format(type(c)))

        for ei in obj.external_identifiers:
            if isinstance(ei, ExternalIdentifier):
                ei_element = to_xml(ei)
                eo_element.append(ei_element)
            else:
                raise TypeError("ExtrinsicObject.external_identifiers expected element instance of "
                                "ExternalIdentifier but got {}.".format(type(ei)))

        return eo_element

    elif isinstance(obj, RegistryPackage):

        attrs = dict()
        if obj.registry_package_id is not None:
            attrs["id"] = to_xml(obj.registry_package_id)
        if obj.status is not None:
            attrs["status"] = to_xml(obj.status)
        if obj.lid is not None:
            attrs["lid"] = to_xml(obj.lid)
        rp_element = xml.Element(xml.QName(uri_rim, "RegistryPackage"), attrs)

        for s in obj.slots:
            if isinstance(s, Slot):
                s_element = to_xml(s)
                rp_element.append(s_element)
            else:
                raise TypeError("RegistryPackage.slots expected element instance of Slot but got {}.".format(type(s)))

        if obj.name is not None:
            if isinstance(obj.name, Name):
                name_element = to_xml(obj.name)
                rp_element.append(name_element)
            else:
                raise TypeError("RegistryPackage.name expected instance of Name but got {}.".format(type(obj.name)))

        for c in obj.classifications:
            if isinstance(c, Classification):
                c_element = to_xml(c)
                rp_element.append(c_element)
            else:
                raise TypeError("RegistryPackage.classifications expected element "
                                "instance of Classification but got {}.".format(type(c)))

        for ei in obj.external_identifiers:
            if isinstance(ei, ExternalIdentifier):
                ei_element = to_xml(ei)
                rp_element.append(ei_element)
            else:
                raise TypeError("RegistryPackage.external_identifiers expected element instance of "
                                "ExternalIdentifier but got {}.".format(type(ei)))

        return rp_element

    elif isinstance(obj, Classification):
        attrs = dict()

        if obj.classification_scheme is not None:
            attrs["classificationScheme"] = to_xml(obj.classification_scheme)
        if obj.node_represention is not None:
            attrs["nodeRepresentation"] = to_xml(obj.node_represention)
        if obj.classified_object is not None:
            attrs["classifiedObject"] = to_xml(obj.classified_object)
        if obj.classification_node is not None:
            attrs["classificationNode"] = to_xml(obj.classification_node)
        if obj.classification_id is not None:
            attrs["id"] = to_xml(obj.classification_id)

        c_element = xml.Element(xml.QName(uri_rim, "Classification"), attrs)

        if obj.slot is not None:            # TODO: Must be list of slots
            if isinstance(obj.slot, Slot):
                s_element = to_xml(obj.slot)
                c_element.append(s_element)
            else:
                raise TypeError("Classification.slot expected instance of Slot but got {}.".format(type(obj.slot)))

        if obj.name is not None:
            if isinstance(obj.name, Name):
                n_element = to_xml(obj.name)
                c_element.append(n_element)
            else:
                raise TypeError("Classification.name expected to be instance of Name class, is '{}'"
                                .format(type(obj.name)))

        return c_element

    elif isinstance(obj, Association):
        attrs = dict()

        if obj.association_type is not None:
            attrs["associationType"] = to_xml(obj.association_type)
        if obj.source_object is not None:
            attrs["sourceObject"] = to_xml(obj.source_object)
        if obj.target_object is not None:
            attrs["targetObject"] = to_xml(obj.target_object)
        if obj.status is not None:
            attrs["status"] = to_xml(obj.status)
        if obj.association_id is not None:
            attrs["id"] = to_xml(obj.association_id)

        a_element = xml.Element(xml.QName(uri_rim, "Association"), attrs)

        for s in obj.slots:
            if isinstance(s, Slot):
                s_element = to_xml(s)
                a_element.append(s_element)
            else:
                raise TypeError("Association.slots expected element instance of Slot but got {}.".format(type(s)))

        return a_element

    elif isinstance(obj, Slot):

        attrs = {"name": to_xml(obj.name)}
        slot_element = xml.Element(xml.QName(uri_rim, "Slot"), attrs)

        value = obj.value
        if isinstance(value, list):
            list_of_values = value
            index = 0
            value = "("
            for e in list_of_values:
                if index > 0:
                    value += ","
                value += "'%s'" % str(e)
                index += 1
            value += ")"
        else:
            if isinstance(value, datetime):
                value = value.strftime("%Y%m%d%H%M%S")
            else:
                value = str(value)

        value_list_element = xml.SubElement(slot_element, xml.QName(uri_rim, "ValueList"))
        value_element = xml.SubElement(value_list_element, xml.QName(uri_rim, "Value"))
        value_element.text = value

        return slot_element

    elif isinstance(obj, ExternalIdentifier):

        attrs = dict()

        if obj.identification_scheme is not None:
            attrs["identificationScheme"] = to_xml(obj.identification_scheme)
        if obj.value is not None:
            attrs["value"] = to_xml(obj.value)
        if obj.registry_object is not None:
            attrs["registryObject"] = to_xml(obj.registry_object)
        if obj.external_identifier_id is not None:
            attrs["id"] = to_xml(obj.external_identifier_id)

        external_identifier_element = xml.Element(xml.QName(uri_rim, "ExternalIdentifier"), attrs)

        if obj.slot is not None:  # TODO must be list of slots
            if isinstance(obj.slot, Slot):
                slot_element = to_xml(obj.slot)
                external_identifier_element.append(slot_element)
            else:
                raise TypeError("ExternalIdentifier.slot expected instance of Slot but got {}.".format(type(obj.slot)))

        if obj.name is not None:
            if isinstance(obj.name, Name):
                name_element = to_xml(obj.name)
                external_identifier_element.append(name_element)
            else:
                raise TypeError("ExternalIdentifier.name expected instance of Name but got {}.".format(type(obj.name)))

        return external_identifier_element

    elif isinstance(obj, Name):

        name_element = xml.Element(xml.QName(uri_rim, "Name"))

        attrs = dict()
        if obj.value is not None:
            attrs["value"] = to_xml(obj.value)
        if obj.language is not None:
            attrs["{http://www.w3.org/XML/1998/namespace}lang"] = to_xml(obj.language)
        if obj.charset is not None:
            attrs["charset"] = to_xml(obj.charset)

        xml.SubElement(name_element, xml.QName(uri_rim, "LocalizedString"), attrs)

        return name_element

    else:
        raise TypeError("Invalid type in XDS XML serialization {}".format(type(obj)))
