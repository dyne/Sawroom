#!/usr/bin/env python3
import base64
import hashlib
import json
import pprint
import sys
import time

import random
import urllib.request
import uuid

import cbor



sys.path.insert(0, ".")  # TODO use the dir of this file not whoever is calling us

from scripts.zencontract import ZenContract, CONTRACTS

import scripts.zentooth_client as zs

import logging

logging.basicConfig(level=logging.INFO)

pp = pprint.PrettyPrinter(indent=4)

debug = 1
debug_zen = 1


def pp_json(json_str):
    pp_json(json_str)


def pp_json(json_str):
    pprint.pprint(json.loads(json_str), width=1)


def pp_object(obj):
    pp.pprint(obj)


print("Executing a Petition On Sawtooth!")


def load_zencode(contract_name):
    contract = ZenContract(contract_name)
    return contract.get_zencode()


def execute_contract(contract_name, keys=None, data=None):
    contract = ZenContract(contract_name)
    contract.keys(keys)
    contract.data(data)
    res = contract.execute()
    if debug_zen is 1:
        print("=====")
        print(contract_name + ":")
        print("----->")
        print(contract.get_zencode())
        print("<-----")
        if (res is not None) and res.startswith("{"):
            pp_json(res)
        else:
            print(res)

        print("=====")
    return res


def wait_for(timer=2):
    print("Sleeping for {} second...".format(timer))
    time.sleep(timer)


# Generate a citizen keypair and credential (equivalent to "sign_petition_crypto" in the python version
# Which returns a private key and "sigma" which is the credential
def generate_citizen_keypair_and_credential(issuer_keypair):
    # CITIZEN
    citizen_keypair = execute_contract(CONTRACTS.CITIZEN_KEYGEN)
    citizen_credential_request = execute_contract(CONTRACTS.CITIZEN_CREDENTIAL_REQUEST, keys=citizen_keypair)

    # ISSUER
    credential_issuer_signed_credential = execute_contract(CONTRACTS.CREDENTIAL_ISSUER_SIGN_CREDENTIAL,
                                                           keys=issuer_keypair,
                                                           data=citizen_credential_request)

    # CITIZEN
    citizen_credential = execute_contract(CONTRACTS.CITIZEN_AGGREGATE_CREDENTIAL,
                                          keys=citizen_keypair,
                                          data=credential_issuer_signed_credential)

    return citizen_keypair, citizen_credential


print("Generating citizen keypair...")

issuer_keypair = execute_contract(CONTRACTS.CREDENTIAL_ISSUER_GENERATE_KEYPAIR)
issuer_verification_public_key = execute_contract(CONTRACTS.CREDENTIAL_ISSUER_PUBLISH_VERIFY,
                                                  keys=issuer_keypair)

citizen_A_keypair, citizen_A_credential = generate_citizen_keypair_and_credential(issuer_keypair)

zen_petition = execute_contract(CONTRACTS.CITIZEN_CREATE_PETITION,
                                keys=citizen_A_credential,
                                data=issuer_verification_public_key)

petition_id = "petition-{}".format(uuid.uuid4())

zt_client = zs.ZenToothClient()

# Verify the petition and store it on the ledger:

zencode = load_zencode(CONTRACTS.VERIFIER_APPROVE_PETITION)

zt_client.send_transaction(petition_id, zencode, data=zen_petition, keys=issuer_verification_public_key)

wait_for()

zt_client.read_state(petition_id)


# Sign the petition
print("Citizen A signature: ")


citizen_A_signature = execute_contract(CONTRACTS.CITIZEN_SIGN_PETITION,
                                       keys=citizen_A_credential,
                                       data=issuer_verification_public_key)

print("Adding signature to petition...")


petition_with_signature = execute_contract(CONTRACTS.LEDGER_INCREMENT_PETITION,
                                           keys=zen_petition,
                                           data=citizen_A_signature)


zencode = load_zencode(CONTRACTS.LEDGER_VALIDATE_PETITION)
zt_client.send_transaction(petition_id, zencode, data=petition_with_signature, keys=None)


wait_for()

state_1 = zt_client.read_state(petition_id)

petition_before_signature = state_1['data']

print("####################################################################################################\n")
print("Citizen B signature: ")

citizen_B_keypair, citizen_B_credential = generate_citizen_keypair_and_credential(issuer_keypair)
citizen_B_signature = execute_contract(CONTRACTS.CITIZEN_SIGN_PETITION,
                                       keys=citizen_B_credential,
                                       data=issuer_verification_public_key)

print("Adding signature to petition...")


petition_after_signature = execute_contract(CONTRACTS.LEDGER_INCREMENT_PETITION,
                                           keys=petition_before_signature,
                                           data=citizen_B_signature)


zencode = load_zencode(CONTRACTS.LEDGER_VALIDATE_PETITION)
zt_client.send_transaction(petition_id, zencode, data=petition_after_signature, keys=None)


wait_for()

state_2 = zt_client.read_state(petition_id)

print("####################################################################################################\n")

print("Tally petition")

petition_with_all_signatures = state_2['data']

tally = execute_contract(CONTRACTS.CITIZEN_TALLY_PETITION,
                         keys=citizen_A_credential,
                         data=petition_with_all_signatures)


print("####################################################################################################\n")

print("Show results petition")

tally_count = execute_contract(CONTRACTS.CITIZEN_COUNT_PETITION,
                               keys=tally,
                               data=petition_with_all_signatures)

print("####################################################################################################\n")
