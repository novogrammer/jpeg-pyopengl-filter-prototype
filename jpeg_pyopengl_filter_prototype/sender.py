import socket
import os
import time

from dotenv import load_dotenv

from image_transfer import send_image
import cv2

load_dotenv()

MY_IP=os.getenv("FILTER_MY_IP","127.0.0.1")
MY_PORT=int(os.getenv("FILTER_MY_PORT","5000"))
FROM_FILE=bool(int(os.getenv("SENDER_FROM_FILE","1")))
JPEG_QUALITY=int(os.getenv("FILTER_JPEG_QUALITY","80"))
IMAGE_WIDTH=int(os.getenv("SENDER_IMAGE_WIDTH","480"))
FPS=int(os.getenv("SENDER_FPS","30"))
SPF=1/FPS

print(f"MY_IP: {MY_IP}")
print(f"MY_PORT: {MY_PORT}")
print(f"FROM_FILE: {FROM_FILE}")
print(f"JPEG_QUALITY: {JPEG_QUALITY}")
print(f"IMAGE_WIDTH: {IMAGE_WIDTH}")
print(f"FPS: {FPS}")



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_for_send:
  sock_for_send.connect((MY_IP, MY_PORT))

  if FROM_FILE:
    with open('sending_image.jpg', 'rb') as f:
      data = f.read()
    send_image(sock_for_send,data)
  else:
    capture=cv2.VideoCapture(0)
    previous_time=time.perf_counter()
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    while capture.isOpened():
      before_sleep_time=time.perf_counter()
      time.sleep(max(0,SPF - (before_sleep_time - previous_time)))
      previous_time=time.perf_counter()
      result_read,frame=capture.read()
      if not result_read:
        print("not result_read")
        continue
      resized_frame=cv2.resize(frame, (IMAGE_WIDTH,int(IMAGE_WIDTH / frame_width * frame_height)))
      result_encode,encoded=cv2.imencode(".jpg", resized_frame, (cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY))
      if not result_encode:
        print("not result_encode")
        continue
      data=encoded.tobytes()
      send_image(sock_for_send,data)
    capture.release()


print("Sent.")
