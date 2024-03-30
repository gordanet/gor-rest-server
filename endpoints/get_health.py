# encoding: utf-8
import hashlib
from datetime import datetime, timedelta
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from dbsession import async_session
from models.Transaction import Transaction
from server import app, gord_client


class GordResponse(BaseModel):
    gordHost: str = ""
    serverVersion: str = "0.12.6"
    isUtxoIndexed: bool = True
    isSynced: bool = True
    p2pId: str = "1231312"


class HealthResponse(BaseModel):
    gordServers: List[GordResponse]


@app.get("/info/health", response_model=HealthResponse, tags=["Gor network info"])
async def health_state():
    """
    Returns the current hashrate for Gor network in TH/s.
    """
    await gord_client.initialize_all()

    gords = []

    async with async_session() as s:
        last_block_time = (await s.execute(select(Transaction.block_time)
                                           .limit(1)
                                           .order_by(Transaction.block_time.desc()))).scalar()

    time_diff = datetime.now() - datetime.fromtimestamp(last_block_time / 1000)

    if time_diff > timedelta(minutes=10):
        raise HTTPException(status_code=500, detail="Transactions not up to date")

    for i, gord_info in enumerate(gord_client.gords):
        gords.append({
            "isSynced": gord_info.is_synced,
            "isUtxoIndexed": gord_info.is_utxo_indexed,
            "p2pId": hashlib.sha256(gord_info.p2p_id.encode()).hexdigest(),
            "gordHost": f"GORD_HOST_{i + 1}",
            "serverVersion": gord_info.server_version
        })

    return {
        "gordServers": gords
    }
