# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 10:55:51 2023

@author: shangfr
"""


import asyncio
import json
import logging
import random
import sys
from datetime import datetime
from typing import Iterator

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

application = FastAPI()
templates = Jinja2Templates(directory="templates")
random.seed()  # Initialize the random number generator

@application.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return templates.TemplateResponse("line-race.html", {"request": request})


async def generate_random_data(request: Request) -> Iterator[str]:
    """
    Generates random value between 0 and 100

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    client_ip = request.client.host

    logger.info("Client %s connected", client_ip)

    while True:
        json_data = json.dumps(
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "value": random.random() * 100,
            }
        )
        yield f"data:{json_data}\n\n"
        await asyncio.sleep(0.1)


@application.get("/chart-data")
async def chart_data(request: Request) -> StreamingResponse:
    response = StreamingResponse(generate_random_data(request), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


from fastapi.responses import JSONResponse

@application.get("/local_data2")
async def read_json():
    filepath = "data/life-expectancy-table.json"
    with open(filepath) as json_file:
        data = json.load(json_file)
        output = [{"data":data,"countries":[
          'Finland',
          'France',
          'Germany',
          'Iceland',
          'Norway',
          'Poland',
          'Russia',
          'United Kingdom'
        ]}]
    return JSONResponse(content=output)

import pandas as pd

@application.get("/local_data")
async def read_json():
    filepath = "data/st.csv"
    df = pd.read_csv(filepath)
    df['value'] = df['value'].round(2)
    data = df.values.tolist()
    data.insert(0,df.columns.tolist())
    output = [{"data":data,"countries":df['name'].unique().tolist()}]
    return JSONResponse(content=output)


