import cv2
import sys
import socketio
import requests

from pytz import timezone
from datetime import datetime
from libraries.centroidtracker import CentroidTracker
from libraries.trackableobject import TrackableObject
from libraries.classNames import Classnames

venue = ""
typeModel = ""

PATH_CAM = "rtsp://admin:admin1234@192.168.2.201/cam/realmonitor?channel=1&subtype=0"
SOCKET_LINK = "http://116.193.191.157:8081"
SAVED_COUNT = 'http://116.193.191.157:8081/database/history/HKCCTV_DH001/guest_count/get_all'

configPath = "models/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightPath = "models/frozen_inference_graph.pb"

classNames = []
classFile = "models/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

tracker = CentroidTracker(maxDisappeared=80, maxDistance=90)

net = cv2.dnn_DetectionModel(weightPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0/127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, thres, nms, draw=True, objects=[]):

    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                if (draw):
                    detecbox.append(box)
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
    return img

def mainInit(setVanue, setType):
    venue = setVanue
    typeModel = setType

if __name__ == "__main__":
    # mainInit()
    H = None
    W = None

    people_in = 0
    people_out = 0
    hour = 0

    trackableObjects = {}

    while True:
        try:
            succes, img = cap.read()
            (H,W) = img.shape[:2]

            detecbox = []

            result = getObjects(img, 0.5, 0.2, objects=['person'])
            obj = tracker.update(detecbox)
            for(objId, centroid) in obj.items():
                to = trackableObjects.get(objId, None)

                if to is None:
                    to = TrackableObject(obj, centroid)
                else:
                    y = [c[0] for c in to.centroids]
                    to.centroids.append(centroid)

                    if not to.counted:
                        if y[0] < W//2 and centroid[0] > W//2:
                            people_in += 1
                            to.counted = True
                        elif y[0] > W//2 and centroid[0] < W//2:
                            people_out += 1
                            to.counted = True
                
                trackableObjects[objId] = to

            cv2.putText(img,"Masuk : "+str(people_in),(30,30),
                    cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0),1)
            cv2.putText(img,"Keluar : "+str(people_out),(30,50),
                    cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0),1)
            print("People in : {} | People out : {}".format(people_in, people_out))
            cv2.imshow("Output",img)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        except Exception as e:
            cap = cv2.VideoCapture(PATH_CAM)
            cap.set(cv2.CAP_PROP_BUFFERSIZE,  0)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            print("Error : ", e)
            error_status = True
            continue

    cap.release()
    cv2.destroyAllWindows()