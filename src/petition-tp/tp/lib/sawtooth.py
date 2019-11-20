import requests
from random import randint

import cbor2 as cbor2
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_signing import create_context, CryptoFactory
from hashlib import sha512


class SawtoothHelper:
    def __init__(self, base_url, validator_url=None, pk=None, context=None):
        self.base_url = base_url
        self.validator_url = validator_url if validator_url else f"{base_url}:4004"
        self.context = context if context else create_context("secp256k1")
        self.pk = pk if pk else self.context.new_random_private_key()
        self.signer = CryptoFactory(self.context).new_signer(self.pk)

    @property
    def private_key(self):
        return self.pk.secp256k1_private_key.serialize()

    def set_url(self, url):
        self.base_url = url

    def create_transaction(self, payload, family_name, family_version, address):
        payload_bytes = cbor2.dumps(payload)

        txn_header = TransactionHeader(
            batcher_public_key=self.signer.get_public_key().as_hex(),
            inputs=[address],
            outputs=[address],
            dependencies=[],
            family_name=family_name,
            family_version=family_version,
            nonce=hex(randint(0, 2 ** 64)),
            payload_sha512=sha512(payload_bytes).hexdigest(),
            signer_public_key=self.signer.get_public_key().as_hex(),
        ).SerializeToString()

        txn = Transaction(
            header=txn_header,
            header_signature=self.signer.sign(txn_header),
            payload=payload_bytes,
        )

        return [txn]

    def create_batch(self, transactions):
        batch_header = BatchHeader(
            signer_public_key=self.signer.get_public_key().as_hex(),
            transaction_ids=[txn.header_signature for txn in transactions],
        ).SerializeToString()

        batch = Batch(
            header=batch_header,
            header_signature=self.signer.sign(batch_header),
            transactions=transactions,
        )

        return BatchList(batches=[batch]).SerializeToString()

    def _post(self, payload, family_name, family_version, address):
        transactions = self.create_transaction(
            payload, family_name, family_version, address
        )
        batches = self.create_batch(transactions)
        response = requests.post(
            f"{self.base_url}",
            data=batches,
            headers={"Content-Type": "application/octet-stream"},
        )
        return response.json()

    def post(self, payload):
        family_name = "DECODE_PETITION"
        family_version = "1.0"
        address = self.generate_address(family_name, payload)
        return self._post(payload, family_name, family_version, address)

    @staticmethod
    def generate_address(family_name, payload):
        namespace = sha512(family_name.encode("utf-8")).hexdigest()[0:6]
        petition = sha512(payload["petition_id"].encode("utf-8")).hexdigest()[-64:]
        return namespace + petition
