from urllib.error import URLError

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from environs import Env
from pydantic import UrlStr
from tp.lib.sawtooth import SawtoothHelper
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK

router = APIRouter()
security = OAuth2PasswordBearer(tokenUrl="/token")
env = Env()
env.read_env()


@router.get("/keygen", tags=["Petitions"], summary="Creates a `private_key`")
async def keygen():
    sh = SawtoothHelper(None)
    return sh.private_key


@router.post(
    "/create",
    tags=["Petitions"],
    summary="Creates a new petition",
    status_code=HTTP_201_CREATED,
)
def create(
    petition_id: str,
    petition_request: str,
    verifier: str,
    address: UrlStr = "http://localhost:8090/batches",
    private_key: str = None,
    token: str = Security(security),
):
    payload = dict(
        action="create", keys=verifier, data=petition_request, petition_id=petition_id
    )
    _post(private_key, address, payload)


@router.post(
    "/sign", tags=["Petitions"], summary="Sign a new petition", status_code=HTTP_200_OK
)
def sign(
    petition_id: str,
    signature: str,
    address: UrlStr = "http://localhost:8090/batches",
    private_key: str = None,
    token: str = Security(security),
):
    payload = dict(action="sign", keys=signature, petition_id=petition_id)
    _post(private_key, address, payload)


@router.post(
    "/tally", tags=["Petitions"], summary="Tally a petition", status_code=HTTP_200_OK
)
def tally(
    petition_id: str,
    credentials: str,
    address: UrlStr = "http://localhost:8090/batches",
    private_key: str = None,
    token: str = Security(security),
):
    payload = dict(action="tally", keys=credentials, petition_id=petition_id)
    _post(private_key, address, payload)


@router.post(
    "/count",
    tags=["Petitions"],
    summary="Count signatures on a tallied petition",
    status_code=HTTP_200_OK,
)
def count(
    petition_id: str,
    tally: str,
    address: UrlStr = "http://localhost:8090/batches",
    private_key: str = None,
    token: str = Security(security),
):
    payload = dict(action="tally", keys=tally, petition_id=petition_id)
    _post(private_key, address, payload)


def _post(pk, address, payload):
    sh = SawtoothHelper(None, pk=pk if pk else None)
    sh.set_url(address)
    try:
        sh.post(payload)
    except URLError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Sawtooth server address is not available",
        )
