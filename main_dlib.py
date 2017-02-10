import cv2
import dlib
import numpy as np
from time import time
from urllib.request import urlopen
from argparse import ArgumentParser

face_detector = dlib.get_frontal_face_detector()

def show_frame(image, scaleFactor, minNeighbors):
    dlib_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detected_faces = face_detector(dlib_img, 0)

    # Faces
    for i, face_rect in enumerate(detected_faces):
        cv2.rectangle(image,
                      (face_rect.left(), face_rect.top()),
                      (face_rect.right(), face_rect.bottom()),
                      (0, 255, 0), 2)

    cv2.imshow('Ip-cam', image)

def build_parser():
    parser = ArgumentParser()
    parser.add_argument('-ip', metavar='xxx.xxx.xxx.xxx',
                        help='ip-cam server address',
                        default='192.168.0.28:8080')
    parser.add_argument('-scaleFactor', default=1.1)
    parser.add_argument('-minNeighbors', default=4)
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
