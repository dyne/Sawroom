import cbor
import json
import urllib.parse
import urllib.request

from hashlib import sha512

from sawtooth_signing import CryptoFactory, create_context
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader


def main():
    family_name = "zenroom"
    family_version = "1.0"
    family_namespace = sha512(family_name.encode("utf-8")).hexdigest()[0:6]

    context = create_context("secp256k1")
    private_key = context.new_random_private_key()
    public_key = context.get_public_key(private_key)

    signer = CryptoFactory(context).new_signer(private_key)

    payload = {
        "zencode": """
Scenario 'coconut': "coconut"
Given that I am known as 'identifier'
When I create my new keypair
Then print all data"""
    }

    payload_bytes = cbor.dumps(payload)

    txn_header_bytes = TransactionHeader(
        family_name=family_name,
        family_version=family_version,
        inputs=[family_namespace],
        outputs=[family_namespace],
        signer_public_key=public_key.as_hex(),
        batcher_public_key=public_key.as_hex(),
        dependencies=[],
        payload_sha512=sha512(payload_bytes).hexdigest(),
    ).SerializeToString()

    signature = signer.sign(txn_header_bytes)

    txn = Transaction(
        header=txn_header_bytes, header_signature=signature, payload=payload_bytes
    )

    txns = [txn]

    batch_header_bytes = BatchHeader(
        signer_public_key=public_key.as_hex(),
        transaction_ids=[txn.header_signature for txn in txns],
    ).SerializeToString()

    signature = signer.sign(batch_header_bytes)

    batch = Batch(
        header=batch_header_bytes, header_signature=signature, transactions=txns
    )

    batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

    try:
        request = urllib.request.Request(
            "http://rest-api:8090/batches",
            batch_list_bytes,
            method="POST",
            headers={"Content-Type": "application/octet-stream"},
        )

        response = urllib.request.urlopen(request)
        data = response.read()
        encoding = response.info().get_content_charset("utf-8")
        response_body = json.loads(data.decode(encoding))
        print(response_body)
    except urllib.error.URLError:
        print("error: " + response)
