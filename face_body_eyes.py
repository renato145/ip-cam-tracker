import os
import cv2
import numpy as np
from time import time
from urllib.request import urlopen
from argparse import ArgumentParser

BODY_DETECTOR = os.path.join(os.environ['CONDA_PREFIX'], 'share/OpenCV/haarcascades/haarcascade_fullbody.xml')
FACE_DETECTOR = os.path.join(os.environ['CONDA_PREFIX'], 'share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
EYE_DETECTOR = os.path.join(os.environ['CONDA_PREFIX'], 'share/OpenCV/haarcascades/haarcascade_eye.xml')

def show_frame(image, scaleFactor, minNeighbors):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    body_detector = cv2.CascadeClassifier(BODY_DETECTOR)
    face_detector = cv2.CascadeClassifier(FACE_DETECTOR)
    eye_detector = cv2.CascadeClassifier(EYE_DETECTOR)

    # Bodies
    boxes_body = body_detector.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors)
    for (x, y, w, h) in boxes_body:
        cv2.rectangle(image, (x, y), (x+w, y+h), (200, 0, 0), 2)

    # Faces + Eyes
    boxes_face = face_detector.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors)
    for (x,y,w,h) in boxes_face:
        cv2.rectangle(image, (x,y), (x+w,y+h), (0, 255, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = image[y:y+h, x:x+w]
        eyes = eye_detector.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0, 255, 255), 1)

    cv2.imshow('Ip-cam', image)

def build_parser():
    parser = ArgumentParser()
    parser.add_argument('-ip', metavar='xxx.xxx.xxx.xxx',
                        help='ip-cam server address',
                        default='192.168.0.28:8080')
    parser.add_argument('-scaleFactor', default=1.3)
    parser.add_argument('-minNeighbors', default=5)
    return parser

if __name__ == '__main__':
    parser = build_parser()
    options = parser.parse_args()
    hoststr = 'http://%s/video' % options.ip
    scaleFactor = float(options.scaleFactor)
    minNeighbors = int(options.minNeighbors)
    
    try:
        stream = urlopen(hoststr)
    except:
        print('Can\'t open %s.' % options.ip)
        quit()

    bytes = b''
    while True:
        t0 = time()
        bytes += stream.read(1024)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
            boxes = show_frame(image, scaleFactor, minNeighbors)
            fps = int(1 / (time() - t0))
            print('FPS = %d' % fps, end='\r')

            if cv2.waitKey(1) ==27:
                print('FPS = %d' % fps)
                exit(0)
