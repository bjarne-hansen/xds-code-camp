from uuid import uuid4
#
# DGWS name id format definitions.
#
# Format definitions are used in:
#   //saml:Subject/saml:NameID/@Format
#   //saml:AttributeStatement[@id='SystemLog']/saml:Attribute[@Name='medcom:CareProviderID]/@NameFormat
#
DGWS_NAME_ID_CPRNUMBER = "medcom:cprnumber"
DGWS_NAME_ID_YNUMBER = "medcom:ynumber"
DGWS_NAME_ID_PNUMBER = "medcom:pnumber"
DGWS_NAME_ID_SKSCODE = "medcom:skscode"
DGWS_NAME_ID_CVRNUMBER = "medcom:cvrnumber"
DGWS_NAME_ID_COMMUNALNUMBER = "medcom:communalnumber"
DGWS_NAME_ID_LOCATIONNUMBER = "medcom:locationnumber"
DGWS_NAME_ID_OTHER = "medcom:other"

# List of DGWS name formats (for validation).
DGWS_NAME_ID_FORMATS = [DGWS_NAME_ID_CPRNUMBER, DGWS_NAME_ID_YNUMBER, DGWS_NAME_ID_PNUMBER, DGWS_NAME_ID_SKSCODE,
                        DGWS_NAME_ID_CVRNUMBER, DGWS_NAME_ID_COMMUNALNUMBER, DGWS_NAME_ID_LOCATIONNUMBER,
                        DGWS_NAME_ID_OTHER]

# IDCardData AttributeStatement
SOSI_ID_CARD_ID = "sosi:IDCardID"
SOSI_ID_CARD_VERSION = "sosi:IDCardVersion"
SOSI_ID_CARD_TYPE = "sosi:IDCardType"
SOSI_AUTHENTICATION_LEVEL = "sosi:AuthenticationLevel"
SOSI_OCES_CERT_HASH = "sosi:OCESCertHash"

# UserLog AttributeStatement
MEDCOM_USER_CIVIL_REGISTRATION_NUMBER = "medcom:UserCivilRegistrationNumber"
MEDCOM_USER_GIVEN_NAME = "medcom:UserGivenName"
MEDCOM_USER_SURNAME = "medcom:UserSurName"
MEDCOM_USER_EMAIL_ADDRESS = "medcom:UserEmailAddress"
MEDCOM_USER_ROLE = "medcom:UserRole"
MEDCOM_USER_OCCUPATION = "medcom:UserOccupation"
MEDOM_USER_AUTHORIZATION_CODE = "medcom:UserAuthorizationCode"

# SystemLog AttributeStatement
MEDCOM_IT_SYSTEM_NAME = "medcom:ITSystemName"
MEDCOM_CARE_PROVIDER_ID = "medcom:CareProviderID"           # {"NameFormat": name_format})
MEDCOM_CARE_PROVIDER_NAME = "medcom:CareProviderName"

#
# DGWS security levels.
#
DGWS_SECURITY_LEVELS = ["1", "2", "3", "4", "5"]

#
# DGWS id card types.
#
DGWS_ID_CARD_TYPES = ["user", "system"]

#
# DGWS request priorities
#   "AKUT" means "acute" (highest priority)
#   "HASTER" means "urgent" (elevated priority)
#   "RUTINE" means "as usual" (normal priority)
#
# Default is "RUTINE", as should only be change if the service provider actually honours the request priorities.
#
# Used in:
#   //medcom:Header/medcom:RequestPriority
#
DGWS_PRIORITY_ACUTE = "AKUT"
DGWS_PRIORITY_URGENT = "HASTER"
DGWS_PRIORITY_NORMAL = "RUTINE"

# List of DGWS request priorities (for validation).
DGWS_REQUEST_PRIORITIES = [DGWS_PRIORITY_ACUTE, DGWS_PRIORITY_URGENT, DGWS_PRIORITY_NORMAL]


class MedcomHeader:

    def __init__(self,
                 message_id=None,
                 security_level="3",
                 request_priority="RUTINE",
                 flow_id=None,
                 non_repudiation_receipt=None):
        assert security_level in DGWS_SECURITY_LEVELS, \
            "Invalid security level '{}'".format(security_level)
        assert request_priority in DGWS_REQUEST_PRIORITIES, \
            "Invalid request priority '{}'".format(request_priority)
        assert non_repudiation_receipt is None or non_repudiation_receipt in ["yes", "no"], \
            "Invalid non_repudiation_receipt '%s'." % non_repudiation_receipt
        self.message_id = uuid4() if message_id is None else message_id
        self.security_level = security_level
        self.request_priority = request_priority
        self.flow_id = flow_id
        self.non_repudiation_receipt = non_repudiation_receipt
