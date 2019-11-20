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

import cbor2
from sawtooth_sdk.processor.exceptions import InvalidTransaction


class ACTION:
    COUNT = "count"
    CREATE = "create"
    SIGN = "sign"
    TALLY = "tally"


class Payload:
    def __init__(self, payload):
        payload = cbor2.loads(payload)
        petition_id = payload.get("petition_id", None)
        data = payload.get("data", None)
        keys = payload.get("keys", None)
        action = payload.get("action", None)

        if not petition_id:
            raise InvalidTransaction("petition_id is required")

        if not action:
            raise InvalidTransaction("action is required")

        if not keys:
            raise InvalidTransaction("keys is required")

        if action not in [
            ACTION.COUNT,
            ACTION.CREATE,
            ACTION.SIGN,
            ACTION.SHOW,
            ACTION.TALLY,
        ]:
            raise InvalidTransaction(f"Invalid action: {action}")

        try:
            keys_object = json.loads(keys)
        except ValueError:
            raise InvalidTransaction(
                "data is in a wrong format, should be a valid JSON"
            )

        if data:
            try:
                data_object = json.loads(data)
            except ValueError:
                raise InvalidTransaction(
                    "keys is in a wrong format, should be a valid JSON"
                )
            self.data = json.dumps(data_object, sort_keys=True)

        self.keys = json.dumps(keys_object, sort_keys=True)
        self.petition_id = petition_id
        self.action = action

    def data(self):
        return self.data

    def keys(self):
        return self.keys

    @staticmethod
    def from_bytes(payload):
        return Payload(payload=payload)
