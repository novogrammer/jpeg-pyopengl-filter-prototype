from queue import Empty, Queue
import socket
import os
import threading
from typing import Callable, TypedDict
from dotenv import load_dotenv

from image_transfer import receive_image, send_image
import time
import io
from PIL import Image

class ImageMessage(TypedDict):
  jpeg_image: bytes


def run(callback:Callable[[Image.Image],Image.Image]|Callable[[],None]):
  load_dotenv()

  MY_IP=os.getenv("FILTER_MY_IP","127.0.0.1")
  MY_PORT=int(os.getenv("FILTER_MY_PORT","5005"))
  print(f"MY_IP: {MY_IP}")
  print(f"MY_PORT: {MY_PORT}")

  YOUR_IP=os.getenv("FILTER_YOUR_IP","127.0.0.1")
  YOUR_PORT=int(os.getenv("FILTER_YOUR_PORT","5006"))
  print(f"YOUR_IP: {YOUR_IP}")
  print(f"YOUR_PORT: {YOUR_PORT}")

  JPEG_QUALITY=int(os.getenv("FILTER_JPEG_QUALITY","80"))
  print(f"JPEG_QUALITY: {JPEG_QUALITY}")



  def receiver(received_image_queue:Queue[ImageMessage]):

    sock_for_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_for_receive.bind(("0.0.0.0", MY_PORT))

    sock_for_receive.listen(1)

    print("Waiting for connection...")

    while True:
      conn_for_receive, addr = sock_for_receive.accept()
      print(f"Connected by {addr}")

      while True:

        received_data=receive_image(conn_for_receive)
        if received_data is None:
          print("Client disconnected.")
          conn_for_receive.close()
          break
        print("Received.")

        received_image_queue.put(
          ImageMessage(jpeg_image=received_data)
        )
        
      print("Waiting for next connection...")
  def sender(sending_image_queue:Queue[ImageMessage]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_for_send:
      sock_for_send.connect((YOUR_IP, YOUR_PORT))

      while True:
        try:
          sending_image_message=sending_image_queue.get(False)
          sending_data=sending_image_message["jpeg_image"]
          send_image(sock_for_send,sending_data)
          print("Sent.")

        except Empty:
          pass



    pass

  received_image_queue:Queue[ImageMessage]=Queue()

  receiver_thread = threading.Thread(target=receiver, args=(received_image_queue,))
  # メインスレッドの終了と同時に強制終了
  receiver_thread.daemon = True
  receiver_thread.start()

  sending_image_queue:Queue[ImageMessage]=Queue()

  sender_thread = threading.Thread(target=sender, args=(sending_image_queue,))
  # メインスレッドの終了と同時に強制終了
  sender_thread.daemon = True
  sender_thread.start()


  while True:

    try:
      received_image_message=received_image_queue.get(False)
      received_data=received_image_message["jpeg_image"]

      time_begin=time.perf_counter()

      image_before = Image.open(io.BytesIO(received_data))

      image_after=callback(image_before)
      image_after = image_after.convert("RGB")

      print("Filtered.")

      output_buffer = io.BytesIO()
      image_after.save(output_buffer, format="JPEG")

      time_end=time.perf_counter()

      print("Encoded.")
      print(f"process time: {time_end-time_begin}")
      sending_data=output_buffer.getvalue()
      sending_image_queue.put(
        ImageMessage(jpeg_image=sending_data)
      )

    except Empty:
      pass
    callback(None)



