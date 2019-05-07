##############################################################################
#
#    Zenroom TP, Transaction processor for zenroom over sawtooth
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
import random

import cbor
import json
import click
import urllib.parse
import urllib.request

from hashlib import sha512

from sawtooth_signing import CryptoFactory, create_context
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader


@click.group()
def main():
    pass


@main.command()
@click.argument("out", type=click.File("w"), default="-", required=False)
def keygen(out):
    context = create_context("secp256k1")
    private_key = context.new_random_private_key()
    click.secho("Private key created!", fg="green")
    click.echo(private_key.secp256k1_private_key.serialize(), file=out)


@main.command()
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option("-c", "--context-id", help="Set a context id", default="zenroom")
@click.option("-d", "--data", help="Data passed to zenroom", type=click.File("rb"))
@click.option("-k", "--keys", help="Keys passed to zenroom", type=click.File("rb"))
@click.option(
    "-a",
    "--address",
    help="Rest API server address",
    default="http://rest-api:8090/batches",
)
@click.argument("zencode", type=click.File("rb"), default="-", required=True)
def transaction(private_key, data, keys, context_id, address, zencode):
    family_name = "zenroom"
    family_version = "1.0"
    family_namespace = sha512(family_name.encode("utf-8")).hexdigest()[0:6]

    context = create_context("secp256k1")

    if private_key:
        pk = private_key.read().decode().strip()
        private_key = Secp256k1PrivateKey.from_hex(pk)
    else:
        private_key = context.new_random_private_key()

    public_key = context.get_public_key(private_key)
    signer = CryptoFactory(context).new_signer(private_key)

    payload = {
        "zencode": zencode.read().decode(),
        "context-id": context_id,
        "data": data.read().decode() if data else None,
        "keys": keys.read().decode() if data else None,
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
        nonce=hex(random.randint(0, 2 ** 64)),
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
            address,
            batch_list_bytes,
            method="POST",
            headers={"Content-Type": "application/octet-stream"},
        )

        response = urllib.request.urlopen(request)
        data = response.read()
        encoding = response.info().get_content_charset("utf-8")
        response_body = json.loads(data.decode(encoding))
        click.secho(str(response_body), fg="green")
    except urllib.error.URLError as e:
        print(f"error: {e}")
