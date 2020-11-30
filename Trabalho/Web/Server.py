import asyncio
import json
import websockets


clients={}
async def receive_message(websocket, path):
  async for i in websocket:
    message = json.loads(i)
    if message['type'] == 'signup':
      if not clients.get(message['user']):
        clients[message['user']] = [websocket, message['userId']]
        await accept_username(message['user'], message['userId'])
        await listUsers()
      else:
        await reject_username(websocket, message['user'], message['userId'])
    if message['type'] == 'message':
      if message['message'][0] == "~":
        user = message['message'].split()[0][1:]
        print(user)
        await send_private(user, message)
      elif clients.get(message['user']):
        await broadcast_message(i)

async def listUsers():
  users = []
  for key in clients.keys():
    users.append(key)
  users_message = json.dumps({
    'type': 'users',
    'message': users
  })
  print("Broadcasting:", users_message)
  await broadcast_message(users_message)


async def broadcast_message(message):
  global clients
  disconnectedUsers = []
  for user in clients.keys():
    client = clients.get(user)[0]
    try:
      await client.send(message)
    except:
      disconnectedUsers.append(user)

  for user in disconnectedUsers:
    clients.pop(user)
  if len(disconnectedUsers) > 0:
    await listUsers()

async def reject_username(websocket, username,userId):
  reject_message = json.dumps({
    'type': 'reject',
    'user':username,
    'message':'Username already in use',
    'userId':userId}
  )
  await websocket.send(reject_message)


async def send_private(user,message):
  global clients
  if clients.get(user):
    client = clients.get(user)[0]
    realMessage = message['message'].split()
    print(realMessage)
    realMessage = realMessage[1:]
    print(realMessage)
    message['message'] = " ".join(realMessage)
    print("To:",user,"; Message: ", message)
    try:
      await client.send(json.dumps(message))
    except:
      clients.pop(user)
      await listUsers()


async def accept_username(username,userId):
  accept_message = json.dumps({
    'type': 'accepted',
    'user':username,
    'message':'Username accepted',
    'userId':userId}
  )
  await broadcast_message(accept_message)


start_server = websockets.serve(receive_message, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever() 