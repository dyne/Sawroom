##############################################################################
#
#    Petition TP, Transaction processor for Decode Petition over sawtooth
#    Copyright (c) 2019-TODAY Dyne.org <http://dyne.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import json
import logging
import traceback
from json import JSONDecodeError

import cbor2
from sawtooth_sdk.processor.exceptions import InvalidTransaction, InternalError
from sawtooth_sdk.processor.handler import TransactionHandler
from tp.processor.payload import Payload, ACTION
from hashlib import sha512
from zenroom.zenroom import zencode_exec_rng

FAMILY_NAME = "DECODE_PETITION"
LOG = logging.getLogger(__name__)


class PetitionTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ["1.0"]

    @property
    def namespaces(self):
        return [sha512(FAMILY_NAME.encode("utf-8")).hexdigest()[0:6]]

    def get_address(self):
        pid = sha512(self.payload.petition_id.encode("utf-8")).hexdigest()[-64:]
        return self.namespaces[0] + pid

    def apply(self, transaction, context):
        try:
            self.context = context
            self.payload = Payload(transaction.payload)
            self.seed = "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"
            self.make_action()
        except Exception as e:
            LOG.error(traceback.format_exc())
            raise InvalidTransaction(
                "An error happened tying to process tx, see logs " + str(e)
            )

    def make_action(self):
        action = self.payload.action
        if action == ACTION.CREATE:
            self.create_petition()
        if action == ACTION.SIGN:
            self.sign_petition()
        if action == ACTION.TALLY:
            self.tally_petition()
        if action == ACTION.COUNT:
            self.count_petition()

    def create_petition(self):
        zencode = f"""Scenario coconut: approve petition
Given that I have a valid 'verifier' from 'MadHatter'
and I have a valid 'credential proof'
and I have a valid 'petition'
When I aggregate the verifiers
and I verify the credential proof
and I verify the new petition to be empty
Then print the 'petition'
and print the 'verifiers'
        """
        result = zencode_exec_rng(
            script=zencode,
            random_seed=bytearray(self.seed, "utf=8"),
            keys=self.payload.keys,
            data=self.payload.data,
        )
        self.save_petition_state(result.stdout)
        LOG.debug("PETITION CREATED")

    def sign_petition(self):
        zencode = """Scenario coconut: aggregate petition signature
Given that I have a valid 'petition signature'
and I have a valid 'petition'
and I have a valid 'verifiers'
When the petition signature is not a duplicate
and the petition signature is just one more
and I add the signature to the petition
Then print the 'petition'
and print the 'verifiers'
        """
        petition = zencode_exec_rng(
            script=zencode,
            random_seed=bytearray(self.seed, "utf=8"),
            keys=self.lookup_petition(),
            data=self.payload.keys,
        )
        self.save_petition_state(petition.stdout)
        LOG.debug("PETITION SIGNED")

    def tally_petition(self):
        zencode = """Scenario coconut: tally petition
Given that I am 'Alice'
and I have my valid 'credential keypair'
and I have a valid 'petition'
When I create a petition tally
Then print all data
        """
        petition = zencode_exec_rng(
            script=zencode,
            random_seed=bytearray(self.seed, "utf=8"),
            keys=self.payload.keys,
            data=self.lookup_petition(),
        )
        LOG.debug("PETITION TALLIED")
        LOG.info(petition.stdout)

    def count_petition(self):
        zencode = """Scenario coconut: count petition
Given that I have a valid 'petition'
and I have a valid 'petition tally'
When I count the petition results
Then print the 'results'
            """
        petition = zencode_exec_rng(
            script=zencode,
            random_seed=bytearray(self.seed, "utf=8"),
            keys=self.payload.keys,
            data=self.lookup_petition(),
        )
        LOG.debug("PETITION COUNT")
        LOG.info(petition.stdout)

    def lookup_petition(self):
        state = self.context.get_state([self.get_address()])
        try:
            return cbor2.loads(state[0].data)["petition"]
        except IndexError:
            return {}
        except JSONDecodeError:
            raise InvalidTransaction("Invalid petition object, should be a valid JSON")
        except:  # noqa
            raise InternalError("Failed to load petition")

    def save_petition_state(self, petition):
        try:
            state = dict(petition=json.dumps(json.loads(petition), sort_keys=True))
        except JSONDecodeError:
            raise InvalidTransaction("Invalid petition object, should be a valid JSON")
        self.save_state(state)

    def save_state(self, state):
        encoded_state = cbor2.dumps(state)
        state = {self.get_address(): encoded_state}
        LOG.debug(
            f"Saving state with context_id [{self.payload.petition_id}] as : {state}"
        )
        try:
            self.context.set_state(state)
        except Exception:
            raise InvalidTransaction("State error")
