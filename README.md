Forge into task Message Brokers

Purpose: To learn about message brokers and how they can be used to create a distributed system.

Task is to create a simple consumer and producer using RabbitMQ, 
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
Your part in this scenario is to create a consumer that will listen to the weather data queue 
and monitor the temperature, specifically Vilnius. If the temperature in Vilnius goes above 31 degrees,
you need to send an alert message to notify Vilnius citizens about the heatwave. Message that 
you will send should be exactly the same that you received from the weather data queue. Another queue will contain results 
of notifications that were sent to the citizens, if you sent correct message to the citizens, you will receive
a piece of a key string that you need to obtain. Just as an advice, do not send all the messages to alerts queue,  this 
way you will get 100k long string that won't be correct.
Example of the message that you will receive in the results queue:
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
Ending message will contain /r/n as a key_char, which mark that all the required messages are received, and 
you got all the key parts. Ending message will look like this:
```
{
  "status": "success",
  "timestamp": "1733752093"
  "key_char: "/r/n"
}
```

This repository will contain rabbitmq server running in docker container exposed on port 56721 that need you connect to.
Consumers on other side are ready to listen to your alerts and will send notification results accordingly.

****

**Requirements:**
* Docker
* Docker-compose
* Any client that can connect to RabbitMQ server (recommended to use python)

**How to start the server**
* Clone this repository
* Install docker and docker-compose if you don't have them, you can find the installation guide [here](https://docs.docker.com/get-docker/)
* Run the following command in the root folder of the repository:
    ```
    docker-compose up
    ```
* Server will start, and you can connect to the RabbitMQ server on port 56721
* In case you experience some unexpected behavior, you can restart the server with the following command:
    ```
    docker-compose down -v
    docker-compose up
    ```

**Task:**
* Create a consumer that will listen to the weather data queue and monitor the temperature in Vilnius. All the weather
data is written to the **_weather_queue_** queue.
* Create producer that will send an alert message with routing key **_alerts_queue_**, **If the temperature in Vilnius goes above 31 degrees**
* Create another consumer that will listen to the **_notification_results_** queue and will receive the key parts that you need to obtain.
No matter whether you send correct message or not you will receive key_char, so double check which messages you are sending to **_alerts_queue_**.
* Once you will receive /r/n as a key_char, you have obtained all the key parts, and you can stop the code.
* Overall architecture should look like this:
    ```
    weather_queue -> consumer(this part is on you, produce messages that meet criteria) -> alerts_queue
  
    notification_results -> consumer(collect parts of the key, no need to send anything)
    ```
* You don't need to edit any other files in this repository and no need to run your code in docker container,
just make sure that you can connect to the rabbitmq server that is running in docker container on port 56721.
* Server folder contains required files for the server, you need to create your own separate folder for the client code.

**Important:**
* If you consumed all the messages and no other messages are coming from weather queue, 
just restart the server with rabbitmq container, this will reset the messages and you can start again.
* Each message got random timestamp and event_id, so you can't just send the same message to the alerts queue. No
need to store messages somewhere else, purpose of this task is to show that you can build pipeline automated pipeline
* If you are using docker, make sure that you have enough resources allocated to the docker,

**Just to make sure that you are on the right track, here are some HINTS:**
* Key length is 46 characters
* It should look something like this WG-FORGE-{other_part_of_the_key_just_for_example}
* If you got all the 46 symbols correctly, but still its not working, try to order them by a timestamp is ascending order
this way you will get the correct key
