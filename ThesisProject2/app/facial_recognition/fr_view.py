from asyncio.windows_events import NULL
from itertools import count
from turtle import back
from django.shortcuts import render
from django.views.decorators import gzip

from django.http import JsonResponse
from django.conf import settings
from ..models import FacesDB, AttendanceLog
from django.utils.timezone import localtime
from datetime import timedelta
from deepface import DeepFace

import cv2
import threading
import os
import base64
import numpy
import json
from PIL import Image


"""
!!! COMMENT ANY LINE OF CODE THAT STARTS THREADS BEFORE RUNNING MAKEMIGRATIONS !!!
!!! OTHERWISE MAKEMIGRATIONS WILL NOT END !!!
"""

#to capture video class
class VideoCameraFaceRecog(object):
    updateCamFrameThread = None
    def __init__(self):
        self._running = True
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        self.detectedEmployees = {}
        self.start()
    def __del__(self):
        self.video.release()
    def update(self):
        while self._running == True:
            (self.grabbed, self.frame) = self.video.read()
    def stop(self):
        self._running = False
    def start(self):
        self._running = True
        threading.Thread(target=self.update, args=()).start()
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
            imgWithRect = None
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
    #Thread for background faceRecognition
    semThread = threading.Lock()
    loggingIntervalMinutes = 1
    #Function to find faces in the frame, and log them to the attendance records, works if the user only has a single camera
    def findFace(self):
        if self.semThread.locked == True:
            pass
        self.semThread.acquire()
        faceArray = self.getFaces()
        #Note all detected employees
        foundEmployees = {}
        try:
            counter = 0
            for i in faceArray:
                
                #Finds face in db
                results = DeepFace.find(i, db_path = os.path.join(settings.MEDIA_ROOT, 'faces'), enforce_detection = True, silent = True)
                #Get the best result, get the filepath to the image, then trims down the path, and saves only the fileName
                bestResult = results[0].sort_values(by='VGG-Face_cosine', ascending=False)['identity'][0].partition('\media\\')[2]
                #Get current time to be inserted to database
                currentTime = localtime()
                #Get employee that is tied into the file
                employeeFace = FacesDB.objects.filter(image=bestResult, active=True)
                if not employeeFace:
                    continue
                employee = employeeFace[0].employee_id_num
                if employee.active == False:
                    continue

                #Get attendance records for the current detected employee
                empAttRecords = AttendanceLog.objects.filter(employee_id_num=employee)

                if employee.active == True:
                    #Checks if the detected employee has any records, if not, create a new record for them
                    if not empAttRecords:
                        attendanceLog = AttendanceLog()
                        attendanceLog.employee_id_num = employee
                        attendanceLog.time_in = currentTime
                        attendanceLog.save()
                        try:
                            #Get image path from results, open said image, convert it as a numpy array,
                            #and encode the numpy array to an bytearray using cv2
                            #Really retarded solution, but it works
                            imagePath = results[0].sort_values(by='VGG-Face_cosine', ascending=False)['identity'][0]
                            encodedImage = cv2.imencode('.png', numpy.asarray(Image.open(imagePath)))[1]
                        
                            foundEmployees[counter] = {
                                                      0:employee.employee_id_num, 
                                                      1:employee.first_name, 
                                                      2:employee.last_name,
                                                      3:base64.b64encode(encodedImage).decode('utf-8'),
                                                      4:currentTime.now().time(),
                                }
                        except:
                            1+1
                    else:
                        #Gets the latest record in the list of attendance records of the employee
                        latestRecord = empAttRecords.order_by('-time_in')[0]
                        #Checks if the current latest record does not have a time_out yet, and the time_in time interval has passed
                        if latestRecord.time_out == None and latestRecord.time_in + timedelta(minutes=self.loggingIntervalMinutes) <= localtime():
                            latestRecord.time_out = currentTime
                            latestRecord.save()
                            try:
                                #Get image path from results, open said image, convert it as a numpy array,
                                #and encode the numpy array to an bytearray using cv2
                                #Really retarded solution, but it works
                                imagePath = results[0].sort_values(by='VGG-Face_cosine', ascending=False)['identity'][0]
                                encodedImage = cv2.imencode('.png', numpy.asarray(Image.open(imagePath)))[1]
                        
                                foundEmployees[counter] = {
                                                          0:employee.employee_id_num, 
                                                          1:employee.first_name, 
                                                          2:employee.last_name,
                                                          3:base64.b64encode(encodedImage).decode('utf-8'),
                                                          4:currentTime.now().time(),
                                    }
                            except:
                                1+1
                        #Checks if the current latest record time_out time interval has passed, if it is, create a new record
                        if latestRecord.time_out + timedelta(minutes=self.loggingIntervalMinutes) <= localtime():
                            attendanceLog = AttendanceLog()
                            attendanceLog.employee_id_num = employee
                            attendanceLog.time_in = currentTime
                            attendanceLog.save()
                            try:
                                #Get image path from results, open said image, convert it as a numpy array,
                                #and encode the numpy array to an bytearray using cv2
                                #Really retarded solution, but it works
                                imagePath = results[0].sort_values(by='VGG-Face_cosine', ascending=False)['identity'][0]
                                encodedImage = cv2.imencode('.png', numpy.asarray(Image.open(imagePath)))[1]
                        
                                foundEmployees[counter] = {
                                                          0:employee.employee_id_num, 
                                                          1:employee.first_name, 
                                                          2:employee.last_name,
                                                          3:base64.b64encode(encodedImage).decode('utf-8'),
                                                          4:currentTime.now().time(),
                                    }
                            except:
                                1+1
                    counter += 1
            self.detectedEmployees = foundEmployees
        except:
            False
        self.semThread.release()   
cam = 0
def initializeCamera():
    global cam
    if type(cam) != VideoCameraFaceRecog:
        try:
            cam = VideoCameraFaceRecog()
        except:
            pass
#@gzip.gzip_page
def face_recog(request):
    return render(request, 'app/custom/cameraOnly.html', {'title': 'Camera'})

backupData = {}
def jsonVidImgResp(request):
    global backupData
    frame = cam.get_frame_with_rect()
    cam.findFace()

    pass2dArr = cam.detectedEmployees
    if backupData == pass2dArr:
        pass2dArr = {}
    else:
       backupData = pass2dArr

    response = {
        'frame': base64.b64encode(frame).decode('utf-8'),
        'detected_employees': pass2dArr,
        }
    return JsonResponse(response)
def jsonVidImgRespWOrigImg(request):
    frameWRect = cam.get_frame_with_rect()
    frameWORect = cam.get_frame()

    response = {'frameWRect' :base64.b64encode(frameWRect).decode('utf-8'),
                'frameWORect' :base64.b64encode(frameWORect).decode('utf-8'),
                }
    return JsonResponse(response)
