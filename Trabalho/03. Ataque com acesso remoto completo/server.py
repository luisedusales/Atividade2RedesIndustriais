import socket
import subprocess
import selectors
import threading
import random

clients = {}

def send_command():
  print("Connected clients:", clients.keys())
  try:
    client = int(input("Select client:"))
    if clients.get(client):
      command = input("Input command:")
      clients.get(client)[0].sendall(str.encode(command))
  except:
    print("Invalid client")
  finally:
    return send_command()

inputThread = threading.Thread(target=send_command)
inputThread.daemon = True

sel = selectors.DefaultSelector()

def accept(sock, mask):
    global clients
    identifier = random.randint(0,10000)
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr, 'identifier:', identifier)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)
    clients[identifier]=[conn,addr]

def read(conn, mask):
    try:
      data = conn.recv(1024)  # Should be ready
      if data:
        for key in clients.keys():
          if clients.get(key)[0] == conn:
            client = clients.get(key)
            print("Client:", key," Address(IP,port):",client[1], " sent data:")
        print()
        print(repr(data))
      else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()
    except:
      identifier=''
      for key in clients.keys():
        if clients.get(key)[0] == conn:
          print("Client ", key," disconnected.")
          identifier = key
          break
      if identifier != '':
        clients.pop(identifier,None)

    
HOST = ''
PORT = 33777
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

def run_server():
  while True:
    events = sel.select()
    for key, mask in events:
      callback = key.data
      callback(key.fileobj, mask)

serverThread = threading.Thread(target=run_server)
serverThread.start()
inputThread.start()