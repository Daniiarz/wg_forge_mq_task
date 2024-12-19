import asyncio
import json
import random
import uuid
from datetime import datetime
from typing import Annotated

import aio_pika
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel


class AlertRequest(BaseModel):
    event_id: str
    timestamp: int | float
    temperature: int
    city: str


class NotificationResponse(BaseModel):
    status: str
    timestamp: int | float
    key_char: str


async def producer():
    r_conn = redis.Redis.from_pool(redis_pool)

    a = await r_conn.get('key_set')
    if a:
        print("Already generated")
        return
    key = "WG-FORGE-2025-50a97dff20c645f5954135ab17be25c8"
    e_messages = {
        uuid.uuid4().hex: i for i in key
    }
    city_choices = [
        'London',
        'Paris',
        'Berlin',
        'Madrid',
        'Rome',
        'Warsaw',
        'Prague',
        'Vienna',
        'Budapest',
    ]

    timestamp_start = int(datetime.now().timestamp())

    messages = [
        {
            'temperature': random.randint(-20, 40),
            'city': random.choice(city_choices),
            'event_id': uuid.uuid4().hex,
            'timestamp': timestamp_start + (i * random.randint(5, 10)),
        } for i in range(90000)
    ]

    vilnius_lower_than_32 = [
        {
            'temperature': random.randint(-20, 30),
            'city': 'Vilnius',
            'event_id': uuid.uuid4().hex,
            'timestamp': timestamp_start + (i * random.randint(5, 10)),
        } for i in range(0, 90000, 10)
    ]

    expected_messages = [
        {
            'temperature': random.randint(33, 40),
            'city': 'Vilnius',
            'event_id': e_id,
            'timestamp': timestamp_start + (i * 7000),
        } for i, e_id in enumerate(e_messages.keys())
    ]
    messages.extend(vilnius_lower_than_32)
    messages.extend(expected_messages)

    messages = sorted(messages, key=lambda x: x['timestamp'])

    connection = await aio_pika.connect_robust(
        host="rabbitmq",
        login="root",
        password="12345adminroot",
        port=5672,
    )
    routing_key = 'weather_queue'

    await asyncio.gather(
        *[
            r_conn.set(k, val) for (k, val) in e_messages.items()
        ]
    )
    print("Stored required messages in redis")

    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(
            'weather_queue',
            durable=True,
            arguments={"x-queue-type": "stream"},
        )
        await asyncio.gather(
            *[
                channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps(i).encode()),
                    routing_key=routing_key, )
                for i in messages
            ]
        )
        print("Published all messages")

    await r_conn.set('key_set', 1)


app = FastAPI()
redis_pool = redis.ConnectionPool.from_url("redis://redis")


async def redis_conn():
    client = redis.Redis.from_pool(redis_pool)
    yield client
    await client.close()


@app.post("/weather-alerts", response_model=NotificationResponse)
async def alerts_api(
    alert: AlertRequest,
    redis_db: Annotated[redis.Redis, Depends(redis_conn)]
) -> NotificationResponse:
    key: bytes | None = await redis_db.get(alert.event_id)
    return NotificationResponse(
        status='success',
        timestamp=alert.timestamp,
        key_char=(key and key.decode()) or chr(random.randint(0, 255)),
    )


if __name__ == "__main__":
    asyncio.run(producer())
    uvicorn.run("script:app", host="0.0.0.0", port=5000, log_level="info", workers=4)
