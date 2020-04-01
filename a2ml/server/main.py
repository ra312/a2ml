from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, PlainTextResponse

import asyncio
import uuid
import websockets

from a2ml.server.tasks import process_transaction
from a2ml.server.notification import AsyncReceiver

app = FastAPI()

def log(*args):
    print(*args)

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/test")
async def get():
    await asyncio.sleep(1)
    return HTMLResponse(html)

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

@app.get("/start_transaction", response_class=PlainTextResponse)
def start_transaction():
    id = str(uuid.uuid4())
    process_transaction.delay(id)
    return id

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Server test</h1>
        <div>
            <li>It starts some process on server side</li>
            <li>Get an id</li>
            <li>Open websocket connection</li>
            <li>Get updates</li>
            <li>Closes websocket when server reports done</li>
        </div>
        <strong>
            Click several times to spawn more transactions
        </strong>
        <form>
            <button type="button" onclick="sendMessage(event)" style="font-size: 20px; margin: 10px;">Start transaction</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = null;

            function httpGet(theUrl) {
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
                xmlHttp.send( null );
                return xmlHttp.responseText;
            }

            function sendMessage(event) {
                var id = httpGet("http://localhost:8000/start_transaction");
                ws = new WebSocket("ws://localhost:8000/ws?id=" + id);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };

                event.preventDefault()
                return false;
            }
        </script>
    </body>
</html>
"""

@app.websocket("/ws")
# id - id of transaction
async def websocket_endpoint(websocket: WebSocket, id: str = None):
    try:
        if id:
            await websocket.accept()
            await websocket.send_json({"message": f"Tracking transaction: {id}"}, mode="text")

            with AsyncReceiver(id) as notificator:
                try:
                    while True:
                        try:
                            # Periodically iterrupt waiting of message from subscription
                            # to check is websocket is still alive or not
                            reply = await asyncio.wait_for(notificator.get_message(), timeout=5.0)
                            log("Received: ", repr(reply))
                            await websocket.send_json({"message": reply}, mode="text")
                        except asyncio.TimeoutError:
                            await websocket.send_json({"type": "ping"}, mode="text")
                except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
                    log(f"WebSocket {id} disconnected: {str(e)}")
    finally:
        log('WebSocket stopped')
        await websocket.close()
