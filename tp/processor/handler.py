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
import pprint

import cbor as cbor
from sawtooth_sdk.processor.exceptions import InvalidTransaction, InternalError
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
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ["1.0"]

    @property
    def namespaces(self):
        return [NAMESPACE]

    def apply(self, transaction, context):
        try:
            args = decode_transaction(transaction)
            context_id = args["context_id"]
            LOG.debug("Context Id: " + context_id)

            del(args["context_id"])
            LOG.debug("Executing Zencode: " + args["script"])
            result, _ = zenroom.execute(**args)

            json_data = json.dumps(json.loads(args["data"]), sort_keys=True)
            json_result = json.dumps(json.loads(result), sort_keys=True)

            LOG.debug("Zencode Data: <-----")
            pprint.pprint(json.loads(json_data), width=1)

            LOG.debug("Zencode Output: ----->")
            pprint.pprint(json.loads(json_result), width=1)

            save_state(context, context_id, args["script"], json_data, json_result)
        except Exception:
            LOG.exception("Exception saving state")
            #raise InvalidTransaction("An error happened tying to process tx, see logs") This doesnt seem to halt processing


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

    return dict(script=zencode, data=data, keys=keys, context_id=context_id)


def save_state(context, context_id, zencode, data, result):
    state = dict(context_id=context_id, zencode=zencode, data=data, output=result)
    encoded_state = cbor.dumps(state)

    address = generate_address(context_id)
    state = {address: encoded_state}
    LOG.debug("Saving state with context_id [{}]".format(context_id))
    addresses = context.set_state(state)
    LOG.debug("Saved state at address [{}]".format(addresses[0]))

    if not addresses:
        raise InternalError("State error")
