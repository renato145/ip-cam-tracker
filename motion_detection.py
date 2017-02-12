import os
import cv2
import datetime
import imutils
import numpy as np
from time import time
from urllib.request import urlopen
from argparse import ArgumentParser

def show_frame(image, firstFrame):
    text = "Unoccupied"
    frame = imutils.resize(image, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 500:
            continue
 
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
 
    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)

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

    first_frame = None
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
            
            if first_frame is None:            
                first_frame = imutils.resize(image, width=500)
                first_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
                first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)

            show_frame(image, first_frame)
            fps = int(1 / (time() - t0))
            print('FPS = %d' % fps, end='\r')

            if cv2.waitKey(1) ==27:
                print('FPS = %d' % fps)
                exit(0)
