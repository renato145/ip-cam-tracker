import os
import cv2
import numpy as np
from time import time
from urllib.request import urlopen
from argparse import ArgumentParser
from imutils.object_detection import non_max_suppression

def show_frame(image, hog):
    (rects, weights) = hog.detectMultiScale(image, winStride=(8, 8),
        padding=(8, 8), scale=1.1)

    # With nms
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

    # No nms
    # for (x, y, w, h) in rects:
    #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow('Ip-cam', image)

def build_parser():
    parser = ArgumentParser()
    parser.add_argument('-ip', metavar='xxx.xxx.xxx.xxx',
                        help='ip-cam server address',
                        default='192.168.0.28:8080')
    return parser

if __name__ == '__main__':
    parser = build_parser()
    options = parser.parse_args()
    hoststr = 'http://%s/video' % options.ip
    
    try:
        stream = urlopen(hoststr)
    except:
        print('Can\'t open %s.' % options.ip)
        quit()

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    bytes = b''
    while True:
        t0 = time()
        bytes += stream.read(1024)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            show_frame(image, hog)
            fps = int(1 / (time() - t0))
            print('FPS = %d' % fps, end='\r')

            if cv2.waitKey(1) ==27:
                print('FPS = %d' % fps)
                exit(0)
