from asyncio.windows_events import NULL
from django.shortcuts import render
from django.views.decorators import gzip

from django.http import JsonResponse

from deepface import DeepFace
import numpy as np
import cv2
import threading
import os
import base64
import json


"""
!!! COMMENT ANY LINE OF CODE THAT STARTS THREADS BEFORE RUNNING MAKEMIGRATIONS !!!
!!! OTHERWISE MAKEMIGRATIONS WILL NOT END !!!
"""

#to capture video class
class VideoCameraFaceRecog(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()
    def __del__(self):
        self.video.release()
    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

    def get_frame(self):
        image = self.frame
        _, self.pngImg = cv2.imencode('.png', image)
        return self.pngImg

    def get_frame_with_rect(self):
        image = self.frame

        #Tries to detect if a face is in the frame...
        #If a face is detected, the program will draw rectangles on them
        #If not, the program will draw an unmodified frame
        try:
            #Detects the faces in the current frame, returns a dictionary with imagedata(?), the rect with the face, and the confidence level(?)
            results = DeepFace.extract_faces(image, enforce_detection = True)

            imgWithRect = NULL

            for i in results:
                faceRect = i['facial_area']
        
                imgWithRect = cv2.rectangle(image, (faceRect.get('x'), faceRect.get('y')), (faceRect.get('w') + faceRect.get('x'), faceRect.get('h') + faceRect.get('y')), (0,255,0), 1)
        
            _, self.pngImgWRect = cv2.imencode('.png', imgWithRect)
        except:
            _, self.pngImgWRect = cv2.imencode('.png', image)
        
        #Returns an byte array(?)
        return self.pngImgWRect

    def getFaces(self):
        #Returns an array containing all faces in the current frame
        #If no faces are detected, returns an empty array

        image = self.frame
        try: 
            faces = DeepFace.extract_faces(image, enforce_detection = True)
            #Creates an array that contains images of the faces cropped out of the current frame
            extractedFaces = []
            for i in faces:
                faceRect = i['facial_area']
                extractedFaces.append(image[faceRect.get('y'):faceRect.get('y') + faceRect.get('h'), 
                                            faceRect.get('x'):faceRect.get('x') + faceRect.get('w')])

            return extractedFaces
        except:
            return []
    def findFace(faceArray):
        #Finds the faces in the faceArray on the db, resource intensive process, must run on separate thread
        try:
            for i in faceArray:
                #Finds face in db
                results = DeepFace.find(i, db_path = os.path.dirname(__file__) + '\\testface\\', enforce_detection = True, silent = True)
        except:
            print("test")
            

            
cam = 0
def startCamera():
    global cam
    try:
        cam = VideoCameraFaceRecog()
    except:
        pass

#@gzip.gzip_page
def face_recog(request):
    startCamera()
    return render(request, 'app/custom/cameraOnly.html')

def jsonVidImgResp(request):
    frame = cam.get_frame_with_rect()

    response = {'frame' :base64.b64encode(frame).decode('utf-8')}
    return JsonResponse(response)
def jsonVidImgRespWOrigImg(request):
    frameWRect = cam.get_frame_with_rect()
    frameWORect = cam.get_frame()

    response = {'frameWRect' :base64.b64encode(frameWRect).decode('utf-8'),
                'frameWORect' :base64.b64encode(frameWORect).decode('utf-8'),
                }
    return JsonResponse(response)
