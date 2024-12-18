## Forge intro task Message Brokers

Purpose of this task is to create a simple consumer using RabbitMQ, 
example itself won't go further than hello world in the examples of the RabbitMQ tutorial. The goal is to obtain 
specific key that will show that task completed successfully.

We will try to simulate a real-world scenario where we have a weather data server that writes weather 
data across the Europe capital cities. The data is written in JSON format and looks like this:
```
{
  "city": "Vilnius",
  "temperature": 32, // temperature in celsius and will 
  "event_id": "fd48d596-783c-40dc-85df-ca7ed6ffaa2d",
  "timestamp": "1733752033"
}
```
Your task is to create a consumer that listens to the weather data stream and monitors temperatures for Vilnius.
If the temperature **exceeds 31°C**, call /weather-alerts API with alert message identical to the one received
from the stream to notify citizens about the heatwave.  

An API will return pieces of a key string for correct alerts. Avoid sending all messages to the alerts API,
as this will generate a 100k-long invalid string.

Example of the message that you will receive from a response:
```
{
  "status": "success",
  "timestamp": "1733752033"
  "key_char: "W"
}
{
  "status": "success",
  "timestamp": "1733752063"
  "key_char: "G"
}
```

**Task:**
* Create a consumer that will listen to the weather data stream and monitor the temperature in Vilnius. All the weather
data is written to the **_weather_stream_**.
* Call api and send alert messages to the **/weather-alerts** API, **If the temperature in Vilnius goes above 31 degrees**
* Overall architecture should look like this:
    ```
    weather_stream -> consumer(this part is on you, produce messages that meet criteria) -> call api /weather-alerts API
    
    collect key_char when you reach 46 symbols you can stop consuming messages and print key to check if its correct
    ```
  
    notification_results -> consumer(collect parts of the key, no need to send anything)
    ```
* We recommend using the official RabbitMQ client for Python (pika, aio_pika), but you can use any other library that support RabbitMQ 
streams.

**Important:**
* Consuming from the stream can be achieved by passing parameters:
  ```python
    channel.basic_qos(
        prefetch_count=10, 
    )
    channel.basic_consume(
        queue='weather_stream',
        on_message_callback=callback,
        auto_ack=True,
        arguments={'x-stream-offset': 'first'} # this will consume messages from the beginning
    )
  ```
* If you consumed all the messages and no other messages are coming from weather stream, 
reconnect to the stream and start consuming messages again.
* Each message got random timestamp and event_id, so you can't just send the same message to the alerts API. No
need to store messages somewhere else, purpose of this task is to show that you can build pipelines and react messages
with code
* If you are not sure about something, feel free to ask questions

**Just to make sure that you are on the right track, here are some HINTS:**
* Key length is 46 characters, It should look something like this WG-FORGE-{other_part_of_the_key_just_for_example}
* If you got all the 46 symbols correctly, but still its not working, try to order them by a timestamp is ascending order
this way you will get the correct key
