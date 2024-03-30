# encoding: utf-8
import time
from datetime import datetime

from pydantic import BaseModel
from starlette.responses import PlainTextResponse

from helper.deflationary_table import DEFLATIONARY_TABLE
from server import app, gord_client


class HalvingResponse(BaseModel):
    nextHalvingTimestamp: int = 1714720317000
    nextHalvingDate: str = '2024-04-14 00:10:00 UTC'
    nextHalvingAmount: float = 440


@app.get("/info/halving", response_model=HalvingResponse | str, tags=["Gor network info"])
async def get_halving(field: str | None = None):
    """
    Returns information about chromatic halving
    """
    resp = await gord_client.request("getBlockDagInfoRequest")
    daa_score = int(resp["getBlockDagInfoResponse"]["virtualDaaScore"])

    future_reward = 0
    daa_breakpoint = 0

    daa_list = sorted(DEFLATIONARY_TABLE)

    for i, to_break_score in enumerate(daa_list):
        if daa_score < to_break_score:
            future_reward = DEFLATIONARY_TABLE[daa_list[i + 1]]
            daa_breakpoint = to_break_score
            break

    next_halving_timestamp = int(time.time() + (daa_breakpoint - daa_score))

    if field == "nextHalvingTimestamp":
        return PlainTextResponse(content=str(next_halving_timestamp))

    elif field == "nextHalvingDate":
        return PlainTextResponse(content=datetime.utcfromtimestamp(next_halving_timestamp)
                                 .strftime('%Y-%m-%d %H:%M:%S UTC'))

    elif field == "nextHalvingAmount":
        return PlainTextResponse(content=str(future_reward))

    else:
        return {
            "nextHalvingTimestamp": next_halving_timestamp,
            "nextHalvingDate": datetime.utcfromtimestamp(next_halving_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC'),
            "nextHalvingAmount": future_reward
        }
