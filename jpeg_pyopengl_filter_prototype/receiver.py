import socket
import os
from dotenv import load_dotenv

from image_transfer import receive_image

load_dotenv()


YOUR_IP=os.getenv("FILTER_YOUR_IP","127.0.0.1")
YOUR_PORT=int(os.getenv("FILTER_YOUR_PORT","5006"))
TO_FILE=bool(int(os.getenv("RECEIVER_TO_FILE","1")))

print(f"YOUR_IP: {YOUR_IP}")
print(f"YOUR_PORT: {YOUR_PORT}")
print(f"TO_FILE: {TO_FILE}")


sock_for_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_for_receive.bind(("0.0.0.0", YOUR_PORT))

sock_for_receive.listen(1)

print("Waiting for connection...")

file_count = 0

while True:
  conn_for_receive, addr = sock_for_receive.accept()
  print(f"Connected by {addr}")

  while True:
    file_count += 1
    filename = f'received_image_{file_count}.jpg'

    data=receive_image(conn_for_receive)
    if data is None:
      print("Client disconnected.")
      conn_for_receive.close()
      break
    print("Received.")
    if TO_FILE:
      with open(filename, 'wb') as f:
        f.write(data)
    
  print("Waiting for next connection...")
