import struct
import socket
from typing import Optional

def send_image(sock:socket.socket,data:bytes)->None:
    size = len(data)
    sock.send(struct.pack('!I', size))
    sock.sendall(data)

def receive_image(conn:socket.socket)->Optional[bytes]:
  data = conn.recv(4)
  if not data:
    return None
  size = struct.unpack('!I', data)[0]

  data = b''
  while len(data) < size:
    packet = conn.recv(size - len(data))
    if not packet:
      return None
    data += packet
  return data
