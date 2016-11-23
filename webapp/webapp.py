from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "neighbour")
    text = "Hello, " + name
    return web.Response(text=indexpage, content_type='text/html')

async def wshandler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == web.MsgType.text:
            ws.send_str("Hello, {}".format(msg.data))
        elif msg.type == web.MsgType.binary:
            ws.send_bytes(msg.data)
        elif msg.type == web.MsgType.close:
            break

    return ws

indexpage = None

with open('index.html', 'r') as indexfile:
    indexpage=indexfile.read()

app = web.Application()


app.router.add_static('/d3', "d3")
app.router.add_static('/css', "css")

app.router.add_get('/echo', wshandler)
app.router.add_get('/', handle)
app.router.add_get('/{name}', handle)

web.run_app(app)
