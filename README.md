# PY-PROCON
## The POC publish/subscribe

The Py-procon is a mini project (POC) publish/subscribe like redis.This code make by Python and socket network programing concept. 

## Features

- Publish payload to topic
- Subscribe topics
- Unsubscribe topic
- Set payload to topic by key
- Get payload from topic by key
- Push payload to topic
- Pop payload from topic
- List range payload from topic

## Tech

- [Python] - Required version 3+
- [Socket] - Create statefull connection with TCP Protocol
- [Theading] - Handle connection in multitread
- [Mutex] - Resource locking


## Installation

Py-procon requires [Python](https://www.python.org/downloads/) v3.8+ to run.

## Development

First : Run server

```sh
python3 src/server.py
```

Second : Run client

```sh
python src/client.py
```

## Patterns

- <PUBLISH<>topic<>payload>
- <SUBSCRIBE<>["topic"]>
- <UNSUBSCRIBE<>topic>
- <SET<>topic<>key<>payload>
- <GET<>topic<>key>
- <PUSH<>topic<>payload>
- <POP<>topic>
- <RANGE<>topic<>start<>stop>

## Author

@Pinyoo Thotaboot