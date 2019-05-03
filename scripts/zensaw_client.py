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


class ZenSawClient(object):

    def __init__(self):
        self.family_name = "zenroom"
        self.family_version = "1.0"
        self.family_namespace = hashlib.sha512(self.family_name.encode("utf-8")).hexdigest()[0:6]

        self.context = create_context("secp256k1")
        self.private_key = self.context.new_random_private_key()
        self.public_key = self.context.get_public_key(self.private_key)

        self.signer = CryptoFactory(self.context).new_signer(self.private_key)

    def send_transaction(self, petition_id, zencode, data):
        payload = {
            "context-id": petition_id,
            "zencode": """
ZEN:begin(0)
ZEN:parse([[""" + zencode + """
]])
ZEN:run()
        """,
            "data": data,
            "keys": """
{"tally":{"dec":{"neg":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562b1e6275dedf6a7b1c43c3ea4b490f90f2a71d0438b8fc68c4ade3385babf6c3fc88fb451e21a90d78913e09c9673e5f","pos":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"c":"64045531ba689dda727152d68aec0d3736e106be06143a6c61d5f6a887eada2e","schema":"petition_tally","zenroom":"0.9","encoding":"hex","curve":"bls383","rx":"2e1e1ef4a2e82fd7b6d4855437f1f797fd71d79be017f084b3e789c5e9604783","uid":"petition"},"petition":{"zenroom":"0.9","uid":"petition","schema":"petition","encoding":"hex","scores":{"neg":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee2190475303c4ff3cf14d07a3128cc93de51b9ddbc40330cfb6bf7a33c494cb104931a6efb6c5c2d82d5c0d71943f3b725","right":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"zenroom":"0.9","schema":"petition_scores","encoding":"hex","curve":"bls383","pos":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee23c60e165285b7ae68b9d3392f71dfea64ef36870b3329816403a14c5201473efe771d02e1e0857a90476464b41b6f986","right":"0416da678fe475bca4bd68a56955c78068349c44949133999c90baa119463f51aeb2ddbca2afa8e3679c07ffffe35ee8ad00a1d105657d8ae72ef0bf3896cbac17e659ee1eeb456aaf32fb029651252bbd7a8f8c0b627b39c91486a5ace70195b4"}},"curve":"bls383","owner":"0425d40a99d767d34ce85baab8d4763701b13d91b4fafc43976a88cc2a38948a4e66690b3f7d899cae879714280d35ce431020d63e8c0b2ec30a97f905fe01df395178fb986d9b764318dff30d0cbe725c183efbff75a6d5efd9c3cc844086299e"}}
        """,
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
        print("Zencode Output:")
        pp_json(data['zencode_output'])



