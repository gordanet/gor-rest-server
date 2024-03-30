# encoding: utf-8

from fastapi import Path, HTTPException
from pydantic import BaseModel

from server import app, gord_client


class BalanceResponse(BaseModel):
    address: str = "gor:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00"
    balance: int = 38240000000


@app.get("/addresses/{gorAddress}/balance", response_model=BalanceResponse, tags=["Gor addresses"])
async def get_balance_from_gor_address(
        gorAddress: str = Path(
            description="Gor address as string e.g. gor:pzhh76qc82wzduvsrd9xh4zde9qhp0xc8rl7qu2mvl2e42uvdqt75zrcgpm00",
            regex="^gor\:[a-z0-9]{61,63}$")):
    """
    Get balance for a given gor address
    """
    resp = await gord_client.request("getBalanceByAddressRequest",
                                       params={
                                           "address": gorAddress
                                       })

    try:
        resp = resp["getBalanceByAddressResponse"]
    except KeyError:
        if "getUtxosByAddressesResponse" in resp and "error" in resp["getUtxosByAddressesResponse"]:
            raise HTTPException(status_code=400, detail=resp["getUtxosByAddressesResponse"]["error"])
        else:
            raise

    try:
        balance = int(resp["balance"])

    # return 0 if address is ok, but no utxos there
    except KeyError:
        balance = 0

    return {
        "address": gorAddress,
        "balance": balance
    }
