##############################################################################
#
#    Petition TP, Transaction processor for Decode Petition over sawtooth
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
import base64
from urllib.error import URLError

import cbor2
import click as click
import requests
from tp.lib.sawtooth import SawtoothHelper

sh = SawtoothHelper(None)


@click.group()
def main():
    pass


@main.command()
@click.argument("out", type=click.File("w"), default="-", required=False)
def keygen(out):
    click.secho("Private key created!", fg="green")
    click.echo(sh.private_key, file=out)


@main.command()
@click.option(
    "--petition-request",
    type=click.File("rb"),
    required=True,
    help="A file that contains a petition request",
)
@click.option(
    "--verifier",
    type=click.File("rb"),
    required=True,
    help="a file that contains a Credential Issuer Verifier Signature ",
)
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option(
    "-a",
    "--address",
    help="Rest API server address",
    default="http://localhost:8090/batches",
)
@click.argument("petition-id", required=True)
def create(petition_id, petition_request, verifier, address, private_key):
    sh.set_url(address)
    payload = dict(
        action="create",
        keys=verifier.read().decode(),
        data=petition_request.read().decode(),
        petition_id=petition_id,
    )
    _send_command(payload)


@main.command()
@click.option(
    "--signature",
    type=click.File("rb"),
    required=True,
    help="A file that contains a petition signature",
)
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option(
    "-a",
    "--address",
    help="Rest API server address",
    default="http://localhost:8090/batches",
)
@click.argument("petition-id", required=True)
def sign(petition_id, signature, address, private_key):
    sh.set_url(address)
    payload = dict(
        action="sign", keys=signature.read().decode(), petition_id=petition_id
    )
    _send_command(payload)


@main.command()
@click.option(
    "--credential",
    type=click.File("rb"),
    required=True,
    help="A file that contains the credentials of the petition owner",
)
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option(
    "-a",
    "--address",
    help="Rest API server address",
    default="http://localhost:8090/batches",
)
@click.argument("petition-id", required=True)
def tally(petition_id, credential, address, private_key):
    sh.set_url(address)
    payload = dict(
        action="tally", keys=credential.read().decode(), petition_id=petition_id
    )
    _send_command(payload)


@main.command()
@click.option(
    "--tally-object",
    type=click.File("rb"),
    required=True,
    help="A file that contains the tally object",
)
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option(
    "-a",
    "--address",
    help="Rest API server address",
    default="http://localhost:8090/batches",
)
@click.argument("petition-id", required=True)
def count(petition_id, tally_object, address, private_key):
    sh.set_url(address)
    payload = dict(
        action="count", keys=tally_object.read().decode(), petition_id=petition_id
    )
    _send_command(payload)


@main.command()
@click.option(
    "-p",
    "--private-key",
    type=click.File("rb"),
    help="If specified loads a private key from a file else automatically a new key is generated",
)
@click.option(
    "-a", "--address", help="Rest API server address", default="http://localhost:8090"
)
@click.argument("petition-id", required=True)
def show(petition_id, address, private_key):
    payload = dict(petition_id=petition_id)
    petition_address = sh.generate_address("DECODE_PETITION", payload)
    r = requests.get(f"{address}/state?address={petition_address}")
    r = requests.get(f"{address}/blocks/{r.json()['head']}")
    batches = r.json()["data"]["batches"]
    click.secho("PAYLOADS:", fg="green")
    for b in batches:
        for t in b["transactions"]:
            click.secho("=" * 80, fg="cyan")
            click.secho("FAMILY NAME", bold=True, bg="blue", fg="white")
            click.secho(t["header"]["family_name"])
            click.secho("FAMILY VERSION", bold=True, bg="blue", fg="white")
            click.secho(t["header"]["family_version"])
            click.secho("PAYLOAD VALUES", bold=True, bg="blue", fg="white")
            click.echo(cbor2.loads(base64.b64decode(t["payload"])))


def _send_command(payload):
    try:
        response = sh.post(payload)
        click.secho(str(response), fg="green")
    except URLError:
        click.secho("ADDRESS ERROR: please double check your -a option", fg="red")


main.add_command(create)
