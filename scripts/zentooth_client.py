import hashlib
import cbor
from sawtooth_signing import CryptoFactory, create_context
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
import random
import urllib.request
import pprint
import json
import base64


def pp_json(json_str):
    pp_json(json_str)


def pp_json(json_str):
    pprint.pprint(json.loads(json_str), width=1)


def pp_object(obj):
    pprint.pprint(obj)


class ZenToothClient(object):

    def __init__(self):
        self.family_name = "zenroom"
        self.family_version = "1.0"
        self.family_namespace = hashlib.sha512(self.family_name.encode("utf-8")).hexdigest()[0:6]

        self.context = create_context("secp256k1")
        self.private_key = self.context.new_random_private_key()
        self.public_key = self.context.get_public_key(self.private_key)

        self.signer = CryptoFactory(self.context).new_signer(self.private_key)

    def send_transaction(self, petition_id, zencode, data, keys):
        payload = {
            "context-id": petition_id,
            "zencode": """
ZEN:begin(0)
ZEN:parse([[""" + zencode + """
]])
ZEN:run()
        """,
            "data": data,
            "keys": keys,
        }

        payload_bytes = cbor.dumps(payload)

        txn_header_bytes = TransactionHeader(
            family_name=self.family_name,
            family_version=self.family_version,
            inputs=[self.family_namespace],
            outputs=[self.family_namespace],
            signer_public_key=self.public_key.as_hex(),
            batcher_public_key=self.public_key.as_hex(),
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
            nonce=hex(random.randint(0, 2 ** 64)),
        ).SerializeToString()

        signature = self.signer.sign(txn_header_bytes)

        txn = Transaction(
            header=txn_header_bytes, header_signature=signature, payload=payload_bytes
        )

        txns = [txn]

        print("Transaction: {}".format(txn))

        batch_header_bytes = BatchHeader(
            signer_public_key=self.public_key.as_hex(),
            transaction_ids=[txn.header_signature for txn in txns],
        ).SerializeToString()

        signature = self.signer.sign(batch_header_bytes)

        batch = Batch(
            header=batch_header_bytes, header_signature=signature, transactions=txns
        )

        batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

        try:
            request = urllib.request.Request(
                "http://localhost:8090/batches",
                batch_list_bytes,
                method="POST",
                headers={"Content-Type": "application/octet-stream"},
            )

            response = urllib.request.urlopen(request)
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            response_body = json.loads(data.decode(encoding))
            pp_object(response_body)

        except urllib.error.URLError:
            print("error: " + response)

    def generate_address(self, context_id):
        return self.family_namespace + hashlib.sha512(context_id.encode("utf-8")).hexdigest()[-64:]

    def read_state(self, petition_id):
        address = self.generate_address(petition_id)

        try:
            url = "http://localhost:8090/state/{}".format(address)
            request = urllib.request.Request(
                url,
                method="GET"
            )

            response = urllib.request.urlopen(request)
            data = response.read()
            encoding = response.info().get_content_charset("utf-8")
            response_body = json.loads(data.decode(encoding))

        except urllib.error.URLError:
            print("error: {}".format(response))

        data_encoded = response_body['data']

        data_decoded = base64.b64decode(data_encoded)

        data = cbor.loads(data_decoded)

        print("\nGET {} HTTP/1.0".format(url))
        print("Petition ID: {}".format(data['context_id']))

        print("Zencode:")
        print(data['zencode'])

        print("Zencode Data:")
        pp_json(data['data'])

        print("Zencode Output:")
        pp_json(data['output'])



