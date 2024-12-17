import asyncio
import json
import random
import uuid
from datetime import datetime
from hashlib import md5

import aio_pika
import uvicorn
from fastapi import FastAPI
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


KEY = "WG-FORGE-2025-50a97dff20c645f5954135ab17be25c8"
E_MESSAGES = {
    md5(i.encode()).hexdigest(): i for i in KEY
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
        'temperature': random.randint(32, 40),
        'city': 'Vilnius',
        'event_id': e_id,
        'timestamp': timestamp_start + (i * 7000),
    } for i, (e_id, _) in enumerate(E_MESSAGES.items())
]
messages.extend(vilnius_lower_than_32)
messages.extend(expected_messages)

MESSAGES = sorted(messages, key=lambda x: x['timestamp'])


async def producer(msg: list[dict]):
    connection = await aio_pika.connect_robust(
        host="rabbitmq",
        login="root",
        password="12345adminroot",
        port=5672,
    )
    routing_key = 'weather_queue'
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
                for i in msg
            ]
        )
        print("Published all messages")


app = FastAPI()


@app.post("/weather-alerts", response_model=NotificationResponse)
async def alerts_api(alert: AlertRequest) -> NotificationResponse:
    print(E_MESSAGES)
    if alert.event_id in E_MESSAGES:
        return NotificationResponse(
            status='success',
            timestamp=alert.timestamp,
            key_char=E_MESSAGES.get(alert.event_id),
        )
    return NotificationResponse(
        status='success',
        timestamp=alert.timestamp,
        key_char=chr(random.randint(0, 255)),
    )


if __name__ == "__main__":
    asyncio.run(producer(MESSAGES))
    uvicorn.run("script:app", host="0.0.0.0", port=5000, log_level="info", workers=4)
