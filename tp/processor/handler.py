##############################################################################
#
#    Zenroom TP, Transaction processor for zenroom over sawtooth
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
import hashlib
import logging
import json
import requests

import cbor
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler
from zenroom import zenroom

LOG = logging.getLogger(__name__)
FAMILY_NAME = "zenroom"
NAMESPACE = ADDRESS_PREFIX = hashlib.sha512(FAMILY_NAME.encode("utf-8")).hexdigest()[
    0:6
]


def generate_address(context_id):
    return NAMESPACE + hashlib.sha512(context_id.encode("utf-8")).hexdigest()[-64:]


class ZenroomTransactionHandler(TransactionHandler):
    def __init__(self, url):
        super()
        self.url = url

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ["1.0"]

    @property
    def namespaces(self):
        return [NAMESPACE]

    def retrieve_payload(self):
        payload = ""
        r = requests.get(f"{self.url}/blocks")
        data = r.json()
        blocks = data["data"][0]["batches"]
        for b in blocks:
            payload += b["transactions"][0]["payload"]

        return payload

    def apply(self, transaction, context):
        try:
            script, data, keys, context_id = decode_transaction(transaction)
            LOG.debug(f"Context Id: ${context_id}\nExecuting Zencode: ${script}")
            payload = self.retrieve_payload()
            result, _ = zenroom.zencode_exec_rng(
                script=script,
                data=data,
                keys=keys,
                random_seed=bytearray(payload, "utf=8"),
            )
            json_result = json.dumps(json.loads(result), sort_keys=True)
            LOG.debug(json_result)
            save_state(context, context_id, json_result)
        except Exception:
            LOG.exception("Exception saving state")
            raise InvalidTransaction("An error happened tying to process tx, see logs")


def decode_transaction(transaction):
    try:
        content = cbor.loads(transaction.payload)
    except Exception:
        raise InvalidTransaction("Invalid payload serialization")

    try:
        zencode = content["zencode"]
    except AttributeError:
        raise InvalidTransaction("Zencode script is required to run the transaction")

    data = content.get("data", None)
    keys = content.get("keys", None)
    context_id = content.get("context-id", None)

    return zencode, data, keys, context_id


def save_state(context, context_id, result):
    state = dict(context_id=context_id, zencode_output=result)
    encoded_state = cbor.dumps(state)

    address = generate_address(context_id)
    state = {address: encoded_state}
    LOG.debug(f"Saving state with context_id [{context_id}] as : {state}")
    try:
        context.set_state(state)
    except Exception:
        raise InvalidTransaction("State error")
