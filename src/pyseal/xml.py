
from lxml import etree as xml

from pyseal.soap import Envelope, Action, MessageID, To, ReplyTo
from pyseal.security import Security
from pyseal.saml import Assertion, Subject, Conditions, AttributeStatement
from pyseal.sts import RequestSecurityToken
from pyseal.dgws import MedcomHeader
from pyseal.util import formatted_datetime, timestamp
from pyseal.hsuid import HsuidHeader

__all__ = ["to_xml", "ns_saml", "ns_soap", "ns_security", "ns_wst"]


# noinspection PyProtectedMember
def to_xml(obj):

    # print("Type=", type(obj))

    if isinstance(obj, Envelope):

        #
        # soap:Envelope
        #   soap:Header
        #     ...
        #   soap:Body
        #     ...
        #

        # Create SOAP Envelope

        envelope_element = xml.Element(qn_soap_envelope, nsmap=ns_soap)

        # Add any header elements inside a SOAP Header
        if len(obj.headers) > 0:
            header_element = xml.Element(qn_soap_header)
            envelope_element.append(header_element)

            for header in obj.headers:
                if isinstance(header, xml._Element):
                    header_child_element = header
                else:
                    header_child_element = to_xml(header)
                header_element.append(header_child_element)

        # Add the SOAP Body element and any content.
        body_element = xml.Element(qn_soap_body)
        envelope_element.append(body_element)

        if obj.body is not None:
            # Add content to the SOAP Body element if applicable.
            if isinstance(obj.body, xml._Element):
                body_content_element = obj.body
            else:
                body_content_element = to_xml(obj.body)
            body_element.append(body_content_element)

        return envelope_element

    elif isinstance(obj, Security):

        #
        # wsse:Security
        #   wsu:Timestamp
        #     wsu:Created
        #   saml:Assertion
        #     ...
        #

        # Create Security element
        security_element = xml.Element(qn_wsse_security, nsmap=ns_security)

        # Create Timestamp element, if specified.
        if obj.created is not None:
            timestamp_element = xml.SubElement(security_element, qn_wsu_timestamp)
            timestamp_element = xml.SubElement(timestamp_element, qn_wsu_created)
            timestamp_element.text = formatted_datetime(obj.created)

        # Append Assertion element to Security element
        if obj.assertion is not None:

            # The assertion element is either an Assertion object, or an XML element. In the latter case it is
            # expected to be a signed assertion element created by calling the pyseal.security.sign_assertion(...)
            # function with an Assertion object as parameter. The sign assertion will return a signed XML structure.
            if isinstance(obj.assertion, Assertion):
                assertion_element = to_xml(obj.assertion)
            elif isinstance(obj.assertion, xml._Element):
                assertion_element = obj.assertion
            else:
                raise ValueError("Unexpected type for assertion: {}".format(type(obj.assertion)))

            security_element.append(assertion_element)

        return security_element
    elif isinstance(obj, Assertion):
        #
        # Create Assertion element
        #
        # saml:Assertion
        #   saml:Subject
        #     ...
        #   saml:Conditions
        #     ...
        #   saml:AttributeStatement
        #   ...
        attr = {}
        if obj.id is not None:
            attr["id"] = obj.id
        if obj.version is not None:
            attr["version"] = obj.version
        if obj.issue_instant is not None:
            attr["IssueInstant"] = formatted_datetime(obj.issue_instant)
        assertion_element = xml.Element(qn_saml_assertion, attrib=attr, nsmap=ns_saml)

        # Append Issuer to Assertion
        if obj.issuer is not None:
            issuer_element = xml.SubElement(assertion_element, qn_saml_issuer)
            issuer_element.text = obj.issuer

        # Append Subject to Assertion
        if obj.subject is not None:
            subject_element = to_xml(obj.subject)
            assertion_element.append(subject_element)

        # Append Conditions to Assertion
        if obj.conditions is not None:
            conditions_element = to_xml(obj.conditions)
            assertion_element.append(conditions_element)

        # Append all AttributeStatements to Assertion
        for attribute_statement in obj.attribute_statements:
            attribute_statement_element = to_xml(attribute_statement)
            assertion_element.append(attribute_statement_element)

        return assertion_element

    elif isinstance(obj, Subject):
        #
        # Create SAML Subject
        #
        # saml:Subject
        #   saml:NameID @Format
        #   saml:SubjectConfirmation
        #     saml:ConfirmationMethod
        #     saml:SubjectConfirmationData
        #
        #       ds:KeyInfo
        #         ds:KeyName
        # or
        #       wsse:UsernameToken
        #         wsse:Username
        #         wsse:Password
        #
        subject_element = xml.Element(qn_saml_subject)

        if obj.name_id is not None:
            name_id_element = xml.SubElement(subject_element, qn_saml_name_id, {"Format": obj.name_id_format})
            name_id_element.text = obj.name_id

        subject_confirmation_element = xml.SubElement(subject_element, qn_saml_subject_confirmation)

        confirmation_method_element = xml.SubElement(subject_confirmation_element, qn_saml_confirmation_method)
        confirmation_method_element.text = "urn:oasis:names:tc:SAML:2.0:cm:holder-of-key"

        subject_confirmation_data_element = \
            xml.SubElement(subject_confirmation_element, qn_saml_subject_confirmation_data)

        if obj.keyname is not None:
            key_info_element = xml.SubElement(subject_confirmation_data_element, qn_ds_key_info)
            key_name_element = xml.SubElement(key_info_element, qn_ds_key_name)
            key_name_element.text = obj.keyname
        else:
            # wsse:
            username_token_element = xml.SubElement(subject_confirmation_data_element, qn_wsse_username_token)
            username_element = xml.SubElement(username_token_element, qn_wsse_username)
            username_element.text = obj.username
            password_element = xml.SubElement(username_token_element, qn_wsse_password)
            password_element.text = obj.password

        return subject_element

    elif isinstance(obj, Conditions):
        #
        # saml:Conditions @not_before=... @not_on_or_after= ...
        #
        attr = {}
        if obj.not_before is not None:
            attr["NotBefore"] = formatted_datetime(obj.not_before)
        if obj.not_on_or_after is not None:
            attr["NotOnOrAfter"] = formatted_datetime(obj.not_on_or_after)
        conditions_element = xml.Element(qn_saml_conditions, attrib=attr)
        return conditions_element

    elif isinstance(obj, AttributeStatement):
        #
        # saml:AttributeStatement
        #   saml:Attribute ...
        #     saml:AttributeValue
        #   ...
        #
        attr = {"id": obj.id}
        attribute_statement_element = xml.Element(qn_saml_attribute_statement, attr)
        for a in obj.attributes:
            attr = {"Name": a.name}
            attr.update(a.attributes)
            attribute_element = xml.SubElement(attribute_statement_element, xml.QName(uri_saml, "Attribute"), attr)
            attribute_value_element = xml.SubElement(attribute_element, xml.QName(uri_saml, "AttributeValue"))
            attribute_value_element.text = a.value

        return attribute_statement_element

    elif isinstance(obj, RequestSecurityToken):
        #
        # wst:RequestSecurityToken @Context
        #   wst:TokenType
        #   wst:RequestType
        #   wst:Claims
        #     ... signed assertion ...
        #     wst:Issuer
        #       wsa:Address
        #
        attrs = {}
        if obj.context is not None:
            attrs["Context"] = obj.context
        rst_element = xml.Element(qn_wst_request_security_token, attrib=attrs, nsmap=ns_wst)

        token_type_element = xml.SubElement(rst_element, qn_wst_token_type)
        token_type_element.text = obj.token_type

        request_type_element = xml.SubElement(rst_element, qn_wst_request_type)
        request_type_element.text = obj.request_type

        claims_element = xml.SubElement(rst_element, qn_wst_claims)

        if obj.assertion is not None:
            if isinstance(obj.assertion, xml._Element):
                assertion_element = obj.assertion
            elif isinstance(obj.assertion, Assertion):
                assertion_element = to_xml(obj.assertion)
            else:
                raise TypeError("RequestForSecurityToken assertion attribute expected to be Element or Assertion.")
            claims_element.append(assertion_element)
        else:
            raise ValueError("RequestForSecurityToken assertion attribute is None.")

        issuer_element = xml.SubElement(claims_element, qn_wst_issuer)

        address_element = xml.SubElement(issuer_element, qn_wsa_address)
        address_element.text = obj.issuer

        return rst_element

    elif isinstance(obj, MedcomHeader):

        #
        # medcom:Header
        #   medcom:SecurityLevel
        #   medcom:Linking
        #     medcom:FlowID
        #     medcom:MessageID
        #   medcom:RequireNonRepudiationReceipt
        #
        header_element = xml.Element(xml.QName(uri_medcom, "Header"), nsmap={prefix_medcom: uri_medcom})

        security_level_element = xml.SubElement(header_element, xml.QName(uri_medcom, "SecurityLevel"))
        security_level_element.text = obj.security_level

        linking_element = xml.SubElement(header_element, xml.QName(uri_medcom, "Linking"))

        if obj.flow_id is not None:
            flow_id_element = xml.SubElement(linking_element, xml.QName(uri_medcom, "FlowID"))
            flow_id_element.text = obj.flow_id

        if obj.message_id is not None:
            message_id_element = xml.SubElement(linking_element, xml.QName(uri_medcom, "MessageID"))
            message_id_element.text = str(obj.message_id)

        if obj.non_repudiation_receipt is not None:
            rnrr_element = xml.SubElement(header_element, xml.QName(uri_medcom, "RequireNonRepudiationReceipt"))
            rnrr_element.text = obj.non_repudiation_receipt

        return header_element

    elif isinstance(obj, HsuidHeader):

        #
        # hsuid:HsuidHeader
        #   hsuid:Assertion @Version @IssueInstant @id
        #     hsuid:AttributeStatement @id
        #       hsuid:Attribute @Name
        #         hsuid:AttributeValue
        #       ...
        #

        header_element = xml.Element(xml.QName(uri_hsuid, "HsuidHeader"), nsmap={prefix_hsuid: uri_hsuid})

        attrs = dict()
        attrs["Version"] = "2.0"
        attrs["IssueInstant"] = \
            formatted_datetime(obj.issue_instant) if obj.issue_instant is not None else formatted_datetime(timestamp())
        attrs["id"] = obj.id if obj.id is not None else "hsuid"
        assertion_element = xml.SubElement(header_element, xml.QName(uri_hsuid, "Assertion"), attrs)

        if obj.issuer is not None:
            issuer_element = xml.SubElement(assertion_element, xml.QName(uri_hsuid, "Issuer"))
            issuer_element.text = obj.issuer

        attribute_statement_element = \
            xml.SubElement(assertion_element, xml.QName(uri_hsuid, "AttributeStatement"), {"id": "HSUIDData"})

        for key in obj.keys():
            attribute_element = \
                xml.SubElement(attribute_statement_element, xml.QName(uri_hsuid, "Attribute"), {"Name": key})
            attribute_value_element = xml.SubElement(attribute_element, xml.QName(uri_hsuid, "AttributeValue"))
            attribute_value_element.text = obj[key]

        return header_element

    elif isinstance(obj, Action):

        attrs = dict()
        attrs[xml.QName(uri_soap, "mustUnderstand")] = "true" if obj.must_understand else "false"
        action_element = xml.Element(xml.QName(uri_wsa, "Action"), attrib=attrs, nsmap={prefix_wsa: uri_wsa})
        action_element.text = obj.action

        return action_element
    elif isinstance(obj, MessageID):
        message_id_element = xml.Element(xml.QName(uri_wsa, "MessageID"), nsmap={prefix_wsa: uri_wsa})
        message_id_element.text = str(obj.message_id)
        return message_id_element

    elif isinstance(obj, To):
        to_element = xml.Element(xml.QName(uri_wsa, "To"), nsmap={prefix_wsa: uri_wsa})
        to_element.text = obj.to
        return to_element

    elif isinstance(obj, ReplyTo):
        reply_to_element = xml.Element(xml.QName(uri_wsa, "ReplyTo"), nsmap={prefix_wsa: uri_wsa})
        reply_to_element.text = obj.reply_to
        return reply_to_element

    else:
        raise TypeError("The type {} is not XML serializeable.".format(type(obj)))


# SOAP namespace URI
uri_soap = "http://schemas.xmlsoap.org/soap/envelope/"
prefix_soap = "soap"

# WS-Security namespace URI
uri_wsse = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
prefix_wsse = "wsse"

# WS-Security utility namespace URI
uri_wsu = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
prefix_wsu = "wsu"

# SAML namespace URI
uri_saml = "urn:oasis:names:tc:SAML:2.0:assertion"
prefix_saml = "saml"

# XML DSIG namespace URI.
uri_ds = "http://www.w3.org/2000/09/xmldsig#"
prefix_ds = "ds"

# WS-Trust
uri_wst = "http://docs.oasis-open.org/ws-sx/ws-trust/200512"
prefix_wst = "wst"

# WS-Adressing
# http://www.w3.org/2005/08/addressing
# http://schemas.xmlsoap.org/ws/2004/08/addressing
uri_wsa = "http://www.w3.org/2005/08/addressing"
prefix_wsa = "wsa"

uri_medcom = "http://www.medcom.dk/dgws/2006/04/dgws-1.0.xsd"
prefix_medcom = "medcom"

prefix_hsuid = None
uri_hsuid = "http://www.nsi.dk/hsuid/2016/08/hsuid-1.1.xsd"


ns_soap = {prefix_soap: uri_soap}
ns_security = {prefix_wsse: uri_wsse, prefix_wsu: uri_wsu}
ns_saml = {prefix_saml: uri_saml, prefix_ds: uri_ds}
ns_wst = {prefix_wst: uri_wst, prefix_wsa: uri_wsa}

qn_wst_request_security_token = xml.QName(uri_wst, "RequestSecurityToken")
qn_wst_token_type = xml.QName(uri_wst, "TokenType")
qn_wst_request_type = xml.QName(uri_wst, "RequestType")
qn_wst_claims = xml.QName(uri_wst, "Claims")
qn_wst_issuer = xml.QName(uri_wst, "Issuer")
qn_wsa_address = xml.QName(uri_wsa, "Address")

qn_soap_envelope = xml.QName(uri_soap, "Envelope")
qn_soap_header = xml.QName(uri_soap, "Header")
qn_soap_body = xml.QName(uri_soap, "Body")
qn_wsse_security = xml.QName(uri_wsse, "Security")
qn_wsu_timestamp = xml.QName(uri_wsu, "Timestamp")
qn_wsu_created = xml.QName(uri_wsu, "Created")
qn_saml_assertion = xml.QName(uri_saml, "Assertion")
qn_saml_issuer = xml.QName(uri_saml, "Issuer")
qn_saml_subject = xml.QName(uri_saml, "Subject")
qn_saml_name_id = xml.QName(uri_saml, "NameID")
qn_saml_subject_confirmation = xml.QName(uri_saml, "SubjectConfirmation")
qn_saml_confirmation_method = xml.QName(uri_saml, "ConfirmationMethod")
qn_saml_subject_confirmation_data = xml.QName(uri_saml, "SubjectConfirmationData")
qn_ds_key_info = xml.QName(uri_ds, "KeyInfo")
qn_ds_key_name = xml.QName(uri_ds, "KeyName")
qn_wsse_username_token = xml.QName(uri_wsse, "UsernameToken")
qn_wsse_username = xml.QName(uri_wsse, "Username")
qn_wsse_password = xml.QName(uri_wsse, "Password")
qn_saml_conditions = xml.QName(uri_saml, "Conditions")
qn_saml_attribute_statement = xml.QName(uri_saml, "AttributeStatement")
