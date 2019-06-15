
__all__ = ['HsuidHeader',
           'HSUID_USER_TYPE', 'HSUID_CITIZEN_USER_RELATION', 'HSUID_ORG_RESPONSIBLE_NAME', 'HSUID_SYSTEM_VERSION',
           'HSUID_SYSTEM_NAME', 'HSUID_SYSTEM_VERSION', 'HSUID_SYSTEM_OWNER_NAME',
           'HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER', 'HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER',
           'HSUID_CONSENT_OVERRIDE', 'HSUID_ORG_USING_ID', 'HSUID_RESPONSIBLE_USER_AUTHORIZATION_CODE',
           'HSUID_RESPONSIBLE_USER_CIVIL_REGISTRATION_NUMBER']

HSUID_USER_TYPE = "nsi:UserType"
HSUID_ACTING_USER_CIVIL_REGISTRATION_NUMBER = "nsi:ActingUserCivilRegistrationNumber"
HSUID_ORG_USING_ID = "OrgUsingID"
HSUID_RESPONSIBLE_USER_CIVIL_REGISTRATION_NUMBER = "nsi:ResponsibleUserCivilRegistrationNumber"
HSUID_RESPONSIBLE_USER_AUTHORIZATION_CODE = "nsi:ResponsibleUserAuthorizationCode"
HSUID_CONSENT_OVERRIDE = "nsi:ConsentOverride"
HSUID_SYSTEM_OWNER_NAME = "nsi:SystemOwnerName"
HSUID_SYSTEM_NAME = "nsi:SystemName"
HSUID_SYSTEM_VERSION = "nsi:SystemVersion"
HSUID_ORG_RESPONSIBLE_NAME = "nsi:OrgResponsibleName"
HSUID_CITIZEN_CIVIL_REGISTRATION_NUMBER = "nsi:CitizenCivilRegistrationNumber"
HSUID_CITIZEN_USER_RELATION = "nsi:CitizenUserRelation"


class HsuidHeader(dict):

    def __init__(self, *args, **kwargs):
        super(HsuidHeader, self).__init__(*args, **kwargs)
        self.__id = None
        self.__issue_instant = None
        self.__issuer = None

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def issuer(self):
        return self.__issuer

    @issuer.setter
    def issuer(self, issuer):
        self.__issuer = issuer

    @property
    def issue_instant(self):
        return self.__issue_instant

    @issue_instant.setter
    def issue_instant(self, instant):
        self.__issue_instant = instant
