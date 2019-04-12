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
import random
import string

import cbor as cbor
from sawtooth_sdk.processor.exceptions import InvalidTransaction, InternalError
from sawtooth_sdk.processor.handler import TransactionHandler
from zenroom import zenroom

FAMILY_NAME = "zenroom"
NAMESPACE = ADDRESS_PREFIX = hashlib.sha512(FAMILY_NAME.encode("utf-8")).hexdigest()[
    0:6
]


def generate_address():
    # FIXME: THIS IS A RANDOM GENERATED NAME. IN THE FUTURE SOMETHING MEANINGFUL... SHOULD BE! cit. yoda
    name = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    return NAMESPACE + hashlib.sha512(name.encode("utf-8")).hexdigest()[-64:]


class ZenroomTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ["1.0"]

    @property
    def namespaces(self):
        return NAMESPACE

    def apply(self, transaction, context):
        result = zenroom.zencode(**decode_transaction(transaction))
        save_state(context, result)


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

    return dict(zencode=zencode, data=data, keys=keys)


def save_state(context, result):
    address = generate_address()
    state = dict(address=result)
    encoded = cbor.dumps(state)

    addresses = context.set_state({address: encoded})

    if not addresses:
        raise InternalError("State error")
