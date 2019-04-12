import random

import cbor as cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from hashlib import sha512
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList

import urllib.request
from urllib.error import HTTPError

from tp.processor.handler import generate_address


def main():
    context = create_context("secp256k1")
    private_key = context.new_random_private_key()
    signer = CryptoFactory(context).new_signer(private_key)

    payload = {
        "zencode": """
Scenario 'coconut': "coconut"
Given that I am known as 'identifier'
When I create my new keypair
Then print all data
        """
    }

    payload_bytes = cbor.dumps(payload)
    address = generate_address()

    txn_header_bytes = TransactionHeader(
        family_name="zenroom",
        family_version="1.0",
        inputs=[address],
        outputs=[address],
        signer_public_key=signer.get_public_key().as_hex(),
        batcher_public_key=signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=sha512(payload_bytes).hexdigest(),
        nonce=hex(random.randint(0, 2 ** 64)),
    ).SerializeToString()

    signature = signer.sign(txn_header_bytes)

    txn = Transaction(
        header=txn_header_bytes, header_signature=signature, payload=payload_bytes
    )

    txns = [txn]

    batch_header_bytes = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=[txn.header_signature for txn in txns],
    ).SerializeToString()

    batch = Batch(
        header=batch_header_bytes,
        header_signature=signer.sign(batch_header_bytes),
        transactions=txns,
    )

    batch_list_bytes = BatchList(batches=[batch]).SerializeToString()
    try:
        request = urllib.request.Request(
            "http://rest-api:8090/batches",
            batch_list_bytes,
            method="POST",
            headers={"Content-Type": "application/octet-stream"},
        )
        urllib.request.urlopen(request)

    except HTTPError as e:
        e.file
