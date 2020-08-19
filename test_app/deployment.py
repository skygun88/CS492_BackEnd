import warnings
import os, sys

import threading
warnings.filterwarnings("ignore")

from GANModel import FaceTranslationGANInferenceModel

from face_toolbox_keras.models.verifier.face_verifier import FaceVerifier
from face_toolbox_keras.models.parser import face_parser
from face_toolbox_keras.models.detector import face_detector
from face_toolbox_keras.models.detector.iris_detector import IrisDetector

from utils import utils
from PIL import Image
import numpy as np

from time import time

import socket
import threading

model = FaceTranslationGANInferenceModel()
print("----- Model Prepared -----")

fv = FaceVerifier(classes=512)
fp = face_parser.FaceParser()
fd = face_detector.FaceAlignmentDetector()
idet = IrisDetector()
# # # idet.set_detector(fd)
print("----- Keras Modules Prepared -----")

fns_tmp = [f"/home/ubuntu/CS492_BackEnd/test_app/template/{tmp}" for tmp in sorted(os.listdir("template")) if tmp.split(".")[1] in ["png", "jpeg", "jpg"]]

srcs = []
masks = []
aligned_ims = []
x0s, y0s, x1s, y1s = [], [], [], []
landmarks_s = []

for i, fn_tmp in enumerate(fns_tmp):
  src, mask, aligned_im, (x0, y0, x1, y1), landmarks = utils.get_src_inputs(fn_tmp, fd, fp, idet)  
  
  srcs.append(src)
  masks.append(mask)
  aligned_ims.append(aligned_im)

  x0s.append(x0)
  y0s.append(y0)
  x1s.append(x1)
  y1s.append(y1)

  landmarks_s.append(landmarks)

  print(f"-- Template {i} --")
print("----- Template Prepared -----")


sucess = "/0"
fail = "/1"

HOST = ''
PORT = 46000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

while True:
  client_socket, addr = server_socket.accept()
  print('Connected by', addr)

  data = client_socket.recv(1024).decode()
  path = data.split("/")[0]
  templateId = int(data.split("/")[1])
  print('Received from', addr)
  print(path, templateId)

  fn_tar = "/home/ubuntu/CS492_BackEnd/media/temp/" + path
  tmp_num = templateId

  src, mask, aligned_im, x0, y0, x1, y1, landmarks = srcs[tmp_num], masks[tmp_num], aligned_ims[tmp_num], x0s[tmp_num], y0s[tmp_num], x1s[tmp_num], y1s[tmp_num], landmarks_s[tmp_num]
  start = time()

  try:
    tar, emb_tar = utils.get_tar_inputs(fn_tar, fd, fv)
  except:
    continue

  try:
    out = model.inference(src, mask, tar, emb_tar)
    result_face = np.squeeze(((out[0] + 1) * 255 / 2).astype(np.uint8))
    result_img = utils.post_process_result(fns_tmp[tmp_num], fd, result_face, aligned_im, src, x0, y0, x1, y1, landmarks)

  except:
    continue

  try:
    img = Image.fromarray(result_img, 'RGB')
    img_path = '/home/ubuntu/CS492_BackEnd/media/temp/result.png'
    img.save(img_path)

  except:
    continue

  end = time()

  print("time elapsed: ", end - start)
  print(img_path)

  client_socket.sendall(img_path.encode())
  client_socket.close()

server_socket.close()