import os
import cv2
import numpy as np
from time import time
from urllib.request import urlopen
from argparse import ArgumentParser

def show_frame(image):
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
            show_frame(image)
            fps = int(1 / (time() - t0))
            print('FPS = %d' % fps, end='\r')

            if cv2.waitKey(1) ==27:
                print('FPS = %d' % fps)
                exit(0)
