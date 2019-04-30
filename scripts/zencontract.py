from zenroom import zenroom
from zenroom.zenroom import Error

from scripts.config.config import BaseConfig
from scripts.utils import get_contract


class CONTRACTS:
    CITIZEN_KEYGEN = "01-CITIZEN-credential-keygen.zencode"
    CITIZEN_CREDENTIAL_REQUEST = "02-CITIZEN-credential-request.zencode"

    CREDENTIAL_ISSUER_GENERATE_KEYPAIR = "03-CREDENTIAL_ISSUER-keygen.zencode"
    CREDENTIAL_ISSUER_PUBLISH_VERIFY = "04-CREDENTIAL_ISSUER-publish-verifier.zencode"
    CREDENTIAL_ISSUER_SIGN_CREDENTIAL = "05-CREDENTIAL_ISSUER-credential-sign.zencode"

    CITIZEN_AGGREGATE_CREDENTIAL = "06-CITIZEN-aggregate-credential-signature.zencode"
    CITIZEN_PROVE_CREDENTIAL = "07-CITIZEN-prove-credential.zencode"

    VERIFIER_VERIFY_CREDENTIAL = "08-VERIFIER-verify-credential.zencode"

    CITIZEN_CREATE_PETITION = "09-CITIZEN-create-petition.zencode"

    VERIFIER_APPROVE_PETITION = "10-VERIFIER-approve-petition.zencode"

    CITIZEN_SIGN_PETITION = "11-CITIZEN-sign-petition.zencode"

    LEDGER_INCREMENT_PETITION = "12-LEDGER-add-signed-petition.zencode"

    CITIZEN_TALLY_PETITION = "13-CITIZEN-tally-petition.zencode"
    CITIZEN_COUNT_PETITION = "14-CITIZEN-count-petition.zencode"


config = BaseConfig()
log = config.logger


class ZenContract(object):
    def __init__(self, name):
        self.name = name
        self._keys = None
        self._data = None
        self._error = None
        self.zencode = get_contract(self.name)

    def execute(self):
        if config.getboolean("debug"):  # pragma: no cover
            log.debug("+" * 50)
            log.debug("EXECUTING %s" % self.name)
            log.debug("+" * 50)
            log.debug("DATA: %s" % self.data())
            log.debug("KEYS: %s" % self.keys())
            log.debug("CODE: \n%s" % self.zencode.decode())
        try:
            result, errors = zenroom.execute(
                self.zencode, keys=self._keys, data=self._data
            )
            self._error = errors
            return result.decode()
        except Error:
            return None

    def keys(self, keys=None):
        if keys:
            self._keys = keys.encode()
        return self._keys.decode() if self._keys else None

    def data(self, data=None):
        if data:
            self._data = data.encode()
        return self._data.decode() if self._data else None

    def errors(self):
        return self._error
