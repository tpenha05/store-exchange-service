import os
from datetime import datetime, timezone
from typing import Any, Dict
import base64

import jwt
import requests
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv("../.env")

app = FastAPI(title="Exchange Service")

security = HTTPBearer()
raw_secret = os.getenv("JWT_SECRET_KEY")
JWT_SECRET = base64.b64decode(raw_secret)
JWT_ALGO   = os.getenv("JWT_ALGORITHM", "HS256")

SPREAD_PERCENTAGE = float(os.getenv("SPREAD_PERCENTAGE", "2.0"))

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

class ExchangeResponse(BaseModel):
    sell: float
    buy: float
    date: datetime
    account_id: str

@app.get(
    "/exchange/{from_currency}/{to_currency}",
    response_model=ExchangeResponse,
    summary="Converte de uma moeda para outra"
)
def get_exchange(
    from_currency: str,
    to_currency: str,
    token_payload: Dict[str, Any] = Depends(verify_token),
):
    base = os.getenv("EXCHANGE_API_BASE_URL")
    key  = os.getenv("EXCHANGE_API_KEY")
    url = f"{base}/{key}/latest/{from_currency}"

    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro na API externa")

    rates = resp.json().get("conversion_rates")
    if not rates or to_currency not in rates:
        raise HTTPException(status_code=404, detail="Taxa não encontrada")

    base_rate = rates[to_currency]
    
    spread_factor = SPREAD_PERCENTAGE / 100
    buy_rate = round(base_rate * (1 - spread_factor/2), 4)
    sell_rate = round(base_rate * (1 + spread_factor/2), 4)

    return ExchangeResponse(
        sell=sell_rate,
        buy=buy_rate,
        date=datetime.now(timezone.utc),
        account_id = token_payload.get("jti"),
    )