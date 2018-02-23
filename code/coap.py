import json
import datetime
import random
import sys
import subprocess
from aiocoap import *

from time import sleep
import asyncio

#api = 'https://nb-iot-sensorserver.herokuapp.com/'
#api = 'coap://158.39.77.97:8020/'
api = 'coap://localhost:8020/'

async def main(displayName, id):
    count = 0

    context = await Context.create_client_context()
    uri = api + id
    print(uri)
    while True:
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        if count == 5:
            coverage = 0

            data = {'displayName': displayName, 'type': 'coverage', 'timestamp': timestamp, 'coverage': coverage}
            binary = json.dumps(data)
            b = bytearray()
            b.extend(map(ord, binary))

            request = Message(code=POST, payload=b, uri=uri)
            await context.request(request).response
            count = 0
        else:
            count += 1
            data = {'displayName': displayName, 'type': 'keep-alive', 'timestamp': timestamp}
            binary = json.dumps(data)
            b = bytearray()
            b.extend(map(ord, binary))

            request = Message(code=POST, payload=b, uri=uri)
            await context.request(request).response

        sleep(5)


if __name__ == "__main__":
    arguments = sys.argv[1:]
    asyncio.get_event_loop().run_until_complete(main(arguments[0], arguments[1]))
