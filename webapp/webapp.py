import asyncio
from aiohttp import web
import json
import random
import pprint

pp = pprint.PrettyPrinter(indent=4)

import networkstats

wsclients = []

async def handle(request):
    indexpage = None

    with open('index.html', 'r') as indexfile:
        indexpage=indexfile.read()
    return web.Response(text=indexpage, content_type='text/html')

async def wshandler(request):
    ws = web.WebSocketResponse(protocols=['SUPERNET'])
    await ws.prepare(request)

    wsclients.append(ws)
   
    #send an initial -  response this is not right
    async for msg in ws:
        if msg.type == web.MsgType.text:
            wsreply = json.loads(msg.data)
            print(wsreply)

            if type(wsreply) is list and len(wsreply) == 15:
                networkstats.setdscpmap(wsreply)
    
        elif msg.type == web.MsgType.binary:
            ws.send_bytes(msg.data)
        elif msg.type == web.MsgType.close:
            break
    return ws

async def updatestats(app):
    while True:
        await asyncio.sleep(1)

        interfaces = networkstats.interfaces

        #remap deques to lists
        for x in interfaces:
            if 'interfaces' in x or 'dscp' in x or 'ipproto' in x: continue

            interfaces[x]['rx'] = list(interfaces[x]['rx'])
            interfaces[x]['tx'] = list(interfaces[x]['tx'])

        # we need to handle disconnects
        closed = []
        for client in wsclients:
            if not client.closed:
                client.send_str(json.dumps(interfaces))
            else:
                closed.append(client)
        for x in closed:
            wsclients.remove(x)

async def start_background_tasks(app):
    app.loop.create_task(updatestats(app))

app = web.Application()

app.router.add_static('/d3', "d3")
app.router.add_static('/css', "css")
app.router.add_static('/js', "js")
app.router.add_static('/images', "images")

app.router.add_get('/ifstatus', wshandler)
app.router.add_get('/', handle)

app.on_startup.append(start_background_tasks)
app.on_startup.append(networkstats.start_monitoring)

web.run_app(app)
