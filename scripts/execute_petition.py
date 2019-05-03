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

import scripts.zensaw_client as zs

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


def setup_petition():
    print("Generating citizen keypair...")

    issuer_keypair = execute_contract(CONTRACTS.CREDENTIAL_ISSUER_GENERATE_KEYPAIR)
    issuer_verification_public_key = execute_contract(CONTRACTS.CREDENTIAL_ISSUER_PUBLISH_VERIFY,
                                                      keys=issuer_keypair)

    citizen_A_keypair, citizen_A_credential = generate_citizen_keypair_and_credential(issuer_keypair)

    zen_petition = execute_contract(CONTRACTS.CITIZEN_CREATE_PETITION,
                                    keys=citizen_A_credential,
                                    data=issuer_verification_public_key)

    petition_approved = execute_contract(CONTRACTS.VERIFIER_APPROVE_PETITION,
                                         keys=issuer_verification_public_key,
                                         data=zen_petition)


petition_id = "petition-{}".format(uuid.uuid4())

zs_client = zs.ZenSawClient()

zencode = """Scenario 'coconut': "Count the petition results: any Citizen can count the petition as long as they have the 'tally'"
Given that I receive a petition
and I receive a tally
When I count the petition results
Then print all data
"""

data = """
{"verifier":{"alpha":"26ed76c322d2d5a7ae054ae7cb8ff48965f72af8659af231413a5ef2bd8f63fa99fec211ced1f868776fda9b8e3e50080dfb0b196de451e509858a737edceacf7bcb4ff5d295559672b0ea7192d98cec617208536f2ade9c670e93343b78dc41458813f0b36415018f7fde018ea9abeb111f812187e78664481ee86f1788b3b4f99144636400e68f71547db1d5b014125045dc425f844696bd1c79526644c92514fd7745a6d00c90a0690b980dc88369cf596918416e9b4895a0ce6396b1f732","zenroom":"0.9","beta":"0dbc2ef91831b09d1d755994d267d55136edd66e52202e2a14d76045fa24af3e2e62121d35941cc1f595b64b2ffd33e91bcdc576a53c8b5537de81e560eae9e22152b821f791a862321be60f1e74137abfcb35c6f2a6007ac598ee811589372b4b903abb70832049d77d4f758bee22708782f1d0320474726bb07626bf98984db77e13986a929466a6970073998e968d11f5bc157cb20d1f36ad2e636f585006fe150173dfbeb42fceda7ea1638724de907b5715bfe611436b50b1a05be80a14","curve":"bls383","schema":"issue_verify","encoding":"hex"},"petition":{"owner":"0425d40a99d767d34ce85baab8d4763701b13d91b4fafc43976a88cc2a38948a4e66690b3f7d899cae879714280d35ce431020d63e8c0b2ec30a97f905fe01df395178fb986d9b764318dff30d0cbe725c183efbff75a6d5efd9c3cc844086299e","zenroom":"0.9","curve":"bls383","list":{"040e9c19ba56a0cc48fd9b92a24c5c9946e57069bf8b219bd35abe5f8acdb74081aaad945a6c5f6223559971b4136a562035d64b636b20265646580ba78bdd6312065f9c97342a75f413aadc309e3f8cf0be5d34eba43e18278848a69ad26774e2":true},"encoding":"hex","scores":{"zenroom":"0.9","pos":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee23c60e165285b7ae68b9d3392f71dfea64ef36870b3329816403a14c5201473efe771d02e1e0857a90476464b41b6f986","right":"0416da678fe475bca4bd68a56955c78068349c44949133999c90baa119463f51aeb2ddbca2afa8e3679c07ffffe35ee8ad00a1d105657d8ae72ef0bf3896cbac17e659ee1eeb456aaf32fb029651252bbd7a8f8c0b627b39c91486a5ace70195b4"},"curve":"bls383","neg":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee2190475303c4ff3cf14d07a3128cc93de51b9ddbc40330cfb6bf7a33c494cb104931a6efb6c5c2d82d5c0d71943f3b725","right":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"schema":"petition_scores","encoding":"hex"},"schema":"petition","uid":"petition"}}
        """

keys="""
{"tally":{"dec":{"neg":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562b1e6275dedf6a7b1c43c3ea4b490f90f2a71d0438b8fc68c4ade3385babf6c3fc88fb451e21a90d78913e09c9673e5f","pos":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"c":"64045531ba689dda727152d68aec0d3736e106be06143a6c61d5f6a887eada2e","schema":"petition_tally","zenroom":"0.9","encoding":"hex","curve":"bls383","rx":"2e1e1ef4a2e82fd7b6d4855437f1f797fd71d79be017f084b3e789c5e9604783","uid":"petition"},"petition":{"zenroom":"0.9","uid":"petition","schema":"petition","encoding":"hex","scores":{"neg":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee2190475303c4ff3cf14d07a3128cc93de51b9ddbc40330cfb6bf7a33c494cb104931a6efb6c5c2d82d5c0d71943f3b725","right":"0414a5bed322d6bc186f4f6bb4f7ab7f60913f1047d237e1dd84991d7714619dc81ce497e47ca56abb42dc4a3229a42d562a46f41f85cc043a8429e9d9d4a182f3ae062928baaca8a8e783d4c90db52e307e0343e46c42dc1e61a5df5abc43724c"},"zenroom":"0.9","schema":"petition_scores","encoding":"hex","curve":"bls383","pos":{"left":"04265e9161af6cabce36ba1cdf2e4d5330db7cf493617090a8dff6f309fae4f4f154db620d05d84488e6f51a6c6252bee23c60e165285b7ae68b9d3392f71dfea64ef36870b3329816403a14c5201473efe771d02e1e0857a90476464b41b6f986","right":"0416da678fe475bca4bd68a56955c78068349c44949133999c90baa119463f51aeb2ddbca2afa8e3679c07ffffe35ee8ad00a1d105657d8ae72ef0bf3896cbac17e659ee1eeb456aaf32fb029651252bbd7a8f8c0b627b39c91486a5ace70195b4"}},"curve":"bls383","owner":"0425d40a99d767d34ce85baab8d4763701b13d91b4fafc43976a88cc2a38948a4e66690b3f7d899cae879714280d35ce431020d63e8c0b2ec30a97f905fe01df395178fb986d9b764318dff30d0cbe725c183efbff75a6d5efd9c3cc844086299e"}}
        """

zs_client.send_transaction(petition_id, zencode, data, keys)

print("Sleeping for 1 second to wait for tx to commit...")
time.sleep(1)
print("Going to try and retrieve the state for petition: " + petition_id)


zs_client.read_state(petition_id)
