# encoding: utf-8

from pydantic import BaseModel

from helper import get_gor_price
from server import app, gord_client


class MarketCapResponse(BaseModel):
    marketcap: int = 12000132


@app.get("/info/marketcap", response_model=MarketCapResponse | str, tags=["Gor network info"])
async def get_marketcap(stringOnly: bool = False):
    """
    Get $GOR price and market cap. Price info is from coingecko.com
    """
    gor_price = await get_gor_price()
    resp = await gord_client.request("getCoinSupplyRequest")
    mcap = round(float(resp["getCoinSupplyResponse"]["circulatingSompi"]) / 100000000 * gor_price)

    if not stringOnly:
        return {
            "marketcap": mcap
        }
    else:
        if mcap < 1000000000:
            return f"{round(mcap / 1000000, 1)}M"
        else:
            return f"{round(mcap / 1000000000, 1)}B"
