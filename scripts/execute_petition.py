#!/usr/bin/env python3

import json
import random
import string
import time
import hashlib

import base64
import requests
import pprint
import yaml
import urllib.parse
import urllib.request
import uuid

import cbor
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
from sawtooth_signing import CryptoFactory, create_context

pp = pprint.PrettyPrinter(indent=4, width=2)


def pp_json(json_str):
    pp.pprint(json.loads(json_str))


def pp_object(obj):
    pp.pprint(obj)


print("Executing a Petition On Sawtooth!")


family_name = "zenroom"
family_version = "1.0"
family_namespace = hashlib.sha512(family_name.encode("utf-8")).hexdigest()[0:6]

context = create_context("secp256k1")
private_key = context.new_random_private_key()
public_key = context.get_public_key(private_key)

signer = CryptoFactory(context).new_signer(private_key)

petition_id = "petition-{}".format(uuid.uuid4())

payload = {
    "context-id": petition_id,
    "zencode": """
ZEN:begin(0)
ZEN:parse([[
Scenario 'coconut': "Count the petition results: any Citizen can count the petition as long as they have the 'tally'"
Given that I receive a petition
and I receive a tally
When I count the petition results
Then print all data
]])
ZEN:run()
        """,
    "data": """
{"verifier":{"alpha":"26ed76c322d2d5a7ae054ae7cb8ff48965f72af8659af231413a5ef2bd8f63fa99fec211ced1f868776fda9b8e3e50080dfb0b196de451e509858a737edceacf7bcb4ff5d295559672b0ea7192d98cec617208536f2ade9c670e93343b78dc41458813f0b36415018f7fde018ea9abeb111f812187e78664481ee86f1788b3b4f99144636400e68f71547db1d5b014125045dc425f844696bd1c79526644c92514fd7745a6d00c90a0690b980dc88369cf596918416e9b4895a0ce6396b1f732","zenroom":"0.9","beta":"0dbc2ef91831b09d1d755994d267d55136edd66e52202e2a14d76045fa24af3e2e62121d35941cc1f595b64b2ffd33e91bcdc576a53c8b5537de81e560eae9e22152b821f791a862321be60f1e74137abfcb35c6f2a6007ac598ee811589372b4b903abb70832049d77d4f758bee22708782f1d0320474726bb07626bf98984db77e13986a929466a6970073998e968d11f5bc157cb20d1f36ad2e636f585006fe150173dfbeb42fceda7ea1638724de907b5715bfe611436b50b1a05be80a14","curve":"bls383","schema":"issue_verify","encoding":"hex"},"petition":{"owner":"0425d40a99d767d34ce85baab8d4763701b13d91b4fafc43976a88cc2a38948a4e66690b3f7d899cae879714280d35ce431020d63e8c0b2ec30a97f905fe01df395178fb986d9b764318dff30d0cbe725c183efbff75a6d5efd9c3cc844086299e","zenroom":"0.9","curve":"bls383","list":{"040e9c19ba56a0cc48fd9b92a24c5c9946e57069bf8b219bd35abe5f8acdb74081aaad945a6c5f6223559971b4136a562035d64b636b20265646580ba78bdd6312065f9c97342a75f413aadc309e3f8cf0be5d34eba43e18278848a69ad26774e2":true},"encoding":"hex","scores":{"zenroom":"0.9","pos":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee23c60e165285b7ae68b9d3392f71dfea64ef36870b3329816403a14c5201473efe771d02e1e0857a90476464b41b6f986","right":"0416da678fe475bca4bd68a56955c78068349c44949133999c90baa119463f51aeb2ddbca2afa8e3679c07ffffe35ee8ad00a1d105657d8ae72ef0bf3896cbac17e659ee1eeb456aaf32fb029651252bbd7a8f8c0b627b39c91486a5ace70195b4"},"curve":"bls383","neg":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee2190475303c4ff3cf14d07a3128cc93de51b9ddbc40330cfb6bf7a33c494cb104931a6efb6c5c2d82d5c0d71943f3b725","right":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"schema":"petition_scores","encoding":"hex"},"schema":"petition","uid":"petition"}}
        """,
    "keys": """
{"tally":{"dec":{"neg":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562b1e6275dedf6a7b1c43c3ea4b490f90f2a71d0438b8fc68c4ade3385babf6c3fc88fb451e21a90d78913e09c9673e5f","pos":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"c":"64045531ba689dda727152d68aec0d3736e106be06143a6c61d5f6a887eada2e","schema":"petition_tally","zenroom":"0.9","encoding":"hex","curve":"bls383","rx":"2e1e1ef4a2e82fd7b6d4855437f1f797fd71d79be017f084b3e789c5e9604783","uid":"petition"},"petition":{"zenroom":"0.9","uid":"petition","schema":"petition","encoding":"hex","scores":{"neg":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee2190475303c4ff3cf14d07a3128cc93de51b9ddbc40330cfb6bf7a33c494cb104931a6efb6c5c2d82d5c0d71943f3b725","right":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"zenroom":"0.9","schema":"petition_scores","encoding":"hex","curve":"bls383","pos":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee23c60e165285b7ae68b9d3392f71dfea64ef36870b3329816403a14c5201473efe771d02e1e0857a90476464b41b6f986","right":"0416da678fe475bca4bd68a56955c78068349c44949133999c90baa119463f51aeb2ddbca2afa8e3679c07ffffe35ee8ad00a1d105657d8ae72ef0bf3896cbac17e659ee1eeb456aaf32fb029651252bbd7a8f8c0b627b39c91486a5ace70195b4"}},"curve":"bls383","owner":"0425d40a99d767d34ce85baab8d4763701b13d91b4fafc43976a88cc2a38948a4e66690b3f7d899cae879714280d35ce431020d63e8c0b2ec30a97f905fe01df395178fb986d9b764318dff30d0cbe725c183efbff75a6d5efd9c3cc844086299e"}}
        """,
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
    payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
    nonce=hex(random.randint(0, 2 ** 64)),
).SerializeToString()

signature = signer.sign(txn_header_bytes)

txn = Transaction(
    header=txn_header_bytes, header_signature=signature, payload=payload_bytes
)

txns = [txn]

print("Transaction: {}".format(txn))

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


def generate_address(context_id):
    return family_namespace + hashlib.sha512(context_id.encode("utf-8")).hexdigest()[-64:]


address = generate_address(petition_id)

print("Sleeping for 1 second to wait for tx to commit...")
time.sleep(1)
print("Going to try and retrieve the state @ address : " + address)

try:
    url = "http://localhost:8090/state/{}".format(address)
    request = urllib.request.Request(
        url,
        batch_list_bytes,
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

