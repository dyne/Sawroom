#!/usr/bin/env python3

import json
import random
import string
import time
import hashlib
import requests
import pprint
import yaml

import cbor
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
from sawtooth_signing import CryptoFactory, create_context

pp = pprint.PrettyPrinter(indent=4)


def pp_json(json_str):
    pp.pprint(json.loads(json_str))


def pp_object(obj):
    print("Type : " + str(type(obj)))
    pp.pprint(obj)


print("Executing a Petition On Sawtooth!")

FAMILY_NAME = "zenroom"
NAMESPACE = ADDRESS_PREFIX = hashlib.sha512(FAMILY_NAME.encode("utf-8")).hexdigest()[
                             0:6
                             ]


def generate_address(petitionId):
    return NAMESPACE + hashlib.sha512(petitionId.encode("utf-8")).hexdigest()[64:]


def sha512(data):
    return hashlib.sha512(data).hexdigest()


def get_prefix():
    return sha512('intkey'.encode('utf-8'))[0:6]


def get_address(id):
    prefix = get_prefix()
    id_address = sha512(id.encode('utf-8'))[64:]
    return prefix + id_address


def send_request(url, suffix, data=None, content_type=None, name=None):
    if url.startswith("http://"):
        url = "{}/{}".format(url, suffix)
    else:
        url = "http://{}/{}".format(url, suffix)

    headers = {}

    if content_type is not None:
        headers['Content-Type'] = content_type

    try:
        if data is not None:
            result = requests.post(url, headers=headers, data=data)
        else:
            result = requests.get(url, headers=headers)

        if result.status_code == 404:
            raise Exception("No such key: {}".format(name))

        if not result.ok:
            raise Exception("Error {}: {}".format(
                result.status_code, result.reason))

    except requests.ConnectionError as err:
        raise IntkeyClientException(
            'Failed to connect to REST API: {}'.format(err))

    except BaseException as err:
        raise Exception(err)

    return result.text


def get_status(url, batch_id, wait):
    try:
        result = send_request(
            url,
            'batch_statuses?id={}&wait={}'.format(batch_id, wait),)
        return yaml.safe_load(result)['data'][0]['status']
    except BaseException as err:
        raise Exception(err)


def send_transaction(url, petition_id, zencode, data, signer, wait=None):
    payload = cbor.dumps({
        'petition-id': petition_id,
        'zencode': zencode,
        'data': data,
    })

    # Construct the address
    address = get_address(petitionId)

    header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name="zenroom",
        family_version="1.0",
        inputs=[address],
        outputs=[address],
        dependencies=[],
        payload_sha512=sha512(payload),
        batcher_public_key=signer.get_public_key().as_hex(),
        nonce=hex(random.randint(0, 2**64))
    ).SerializeToString()

    signature = signer.sign(header)

    transaction = Transaction(
        header=header,
        payload=payload,
        header_signature=signature
    )

    batch_list = create_batch_list([transaction], signer)
    batch_id = batch_list.batches[0].header_signature

    if wait and wait > 0:
        wait_time = 0
        start_time = time.time()
        response = send_request(
            url, "batches",
            batch_list.SerializeToString(),
            'application/octet-stream',
        )
        while wait_time < wait:
            status = get_status(
                batch_id,
                wait - int(wait_time),
                )
            wait_time = time.time() - start_time

            if status != 'PENDING':
                return response

        return response

    return send_request(
        "batches", batch_list.SerializeToString(),
        'application/octet-stream',
    )


def create_batch_list(transactions, signer):
    transaction_signatures = [t.header_signature for t in transactions]

    header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=transaction_signatures
    ).SerializeToString()

    signature = signer.sign(header)

    batch = Batch(
        header=header,
        transactions=transactions,
        header_signature=signature)
    return BatchList(batches=[batch])


context = create_context("secp256k1")
private_key = context.new_random_private_key()

signer = CryptoFactory(context).new_signer(private_key)

petitionId = "".join(random.choice(string.ascii_lowercase) for _ in range(10))

print("petitionId: " + petitionId)

zencode = """
ZEN:begin(0)
ZEN:parse([[
Scenario 'coconut': "coconut"
Given that I am known as 'identifier'
When I create my new keypair
Then print all data
]])
ZEN:run()
"""

data = "I am some data"

data = "some data"
url = "http://localhost:8090"
send_transaction(url, petitionId, zencode, data, signer, wait=True)

