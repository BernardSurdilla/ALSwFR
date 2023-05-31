"""
Definition of views.
"""

import base64
import os
import string
import random
import json
from PIL import Image
import cv2
import numpy
from time import sleep
from types import NoneType

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required

from .forms import FaceRegistrationForm, UpdateFaceRegistrationForm, RegisterFaceForm, RemoveEmployee, RestoreRemovedEmployee
from .models import Employee, FacesDB, AttendanceLog
from app.facial_recognition import fr_view

creationYear = 2023

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Encountered an error? Contact the following people.',
        }
    )
def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'A.L.S.W.F.R',
        }
    )

@login_required
def liveCamFeed(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/custom/liveCamFeed.html',
        {
            'title':'Live Feed',
        }
    )

#Requests for returning data from database with html page
@login_required
@permission_required("app.check_user_records")
def viewUsers(request):
    query_results = User.objects.all()
    return render(
        request, 
        'app/custom/viewUsers.html', 
        {
            'title':'Users',
            'table_data': query_results,
        }
    )
@login_required
@permission_required("app.check_employee_data")
def viewEmployees(request):
    query_results = Employee.objects.filter(active = True)
    return render(
        request, 
        'app/custom/viewEmployees.html', 
        {
            'title':'Employees',
            'table_data': query_results,
        }
    )
@login_required
@permission_required("app.check_removed_user_records")
def viewRemovedEmployees(request):
    query_results = Employee.objects.filter(active = False)
    return render(
        request, 
        'app/custom/removedEmployees.html', 
        {
            'title':'Removed Employees',
            'table_data': query_results,
        }
    )
@login_required
@permission_required("app.check_attendance_records")
def attendanceLog(request):
    query_results = AttendanceLog.objects.all()
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/custom/attendanceLog.html',
        {
            'title':'Attendance Log',
            'table_data': query_results,
        }
    )

#Requests for returning data from database with html page, and editing data
@login_required
@permission_required("app.edit_employee_data")
def editUser(request):
    if request.method == 'POST':
        form = UpdateFaceRegistrationForm()
        if request.POST.get('employee_id_num') and request.POST.get('first_name') and request.POST.get('middle_name') and request.POST.get('last_name') and request.POST.get('contact_number') and request.POST.get('email_address'):
            employee = Employee()
            employee.employee_id_num = request.POST.get('employee_id_num')
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.middle_name = request.POST.get('middle_name')
            employee.contact_number = request.POST.get('contact_number')
            employee.email_address = request.POST.get('email_address')
            
            employee.save()
            messages.success(request, 'Employee successfully registered!')
            return render(request, 'app/custom/updateForm.html', {'title': 'Edit Employee Data', 'form': form})
        else:
            messages.error(request, 'Invalid data input! Try again.')
    else:
        form = UpdateFaceRegistrationForm()

    return render(request, 'app/custom/updateForm.html', {'title': 'Edit Employee Data', 'form': form})
@login_required
@permission_required("app.edit_employee_data")
def faceRecogForm(request):
    #The view for user registration
    if request.method == 'POST':
        form = FaceRegistrationForm()
        employee = Employee()
        employee.employee_id_num = request.POST.get('employee_id_num')
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.middle_name = request.POST.get('middle_name')
        employee.contact_number = request.POST.get('contact_number')
        employee.email_address = request.POST.get('email_address')
        employee.save()

        messages.success(request, 'Employee successfully registered!')
        return render(request, 'app/custom/registrationForm.html', {'title': 'Register Employee', 'form': form})
    else:
        form = FaceRegistrationForm()

    return render(request, 'app/custom/registrationForm.html', {'title': 'Register Employee', 'form': form})
@login_required
@permission_required("app.edit_employee_data")
def uploadImages(request):
    form = RegisterFaceForm()

    if request.method == 'POST':
        emp_id = 0
        #Check if employeeId is valid
        try:
            emp_id = int(request.POST.get('employee_id_num'))
        except:
            pass

        #Get the image array and employee id passed
        imgArr = request.POST.getlist('capturedImages[]')
        tempPath = settings.TEMP_IMG_FOLDER

        #Get employee instance
        curEmployeeQuerySet = Employee.objects.filter(employee_id_num=emp_id)

        #Check if imgArr and curEmployeeQuerySet is not empty
        if imgArr and curEmployeeQuerySet:
            curEmployee = curEmployeeQuerySet[0]
            facedb = FacesDB()

            for img in imgArr:
            
                #Remove the header of the data ex. "data:image/png;base64"
                trimmedData = img.partition(',')[2]

                tempImgFilePath = os.path.join(tempPath, 'ayaya.png')
                with open(tempImgFilePath, 'wb') as f:
                    f.write(base64.b64decode(trimmedData))

                #Generate a random file name for security
                res = ''.join(random.choices(string.ascii_uppercase +
                                    string.digits, k=6))

                #Insert images to database
                facedb = FacesDB()
                facedb.employee_id_num = curEmployee
                facedb.image.save(str(res) + '.png', open(tempImgFilePath, 'rb'))
                facedb.save()
                messages.success(request, 'Employee face successfully uploaded!')
                return render(request, 'app/custom/uploadImages.html', {'title': 'Register Employee Face', 'form': form,})
        else:
            messages.error(request, 'Invalid data input! Try again.')
            return render(request, 'app/custom/uploadImages.html', {'title': 'Register Employee Face', 'form': form,})
    return render(request, 'app/custom/uploadImages.html', {'title': 'Register Employee Face', 'form': form,})

@login_required
@permission_required("app.edit_employee_data")
def removeEmployee(request):
    form = RemoveEmployee()
    if request.method == 'POST':
        employee_id_number = request.POST.get('employee_id_num')
        if Employee.objects.filter(employee_id_num=employee_id_number, active=True):
            empInst = Employee.objects.filter(employee_id_num=employee_id_number, active=True)[0]
            empInst.active = False
            empInst.save()
            messages.success(request, 'Employee successfully removed!')
            return render(request,'app/custom/removeEmployee.html',{'title': 'Remove Employee', 'form': form,})
    else:
        return render(request,'app/custom/removeEmployee.html',{'title': 'Remove Employee', 'form': form,})

    return render(request,'app/custom/removeEmployee.html',{'title': 'Remove Employee', 'form': form,})
@login_required
@permission_required("app.edit_employee_data")
def removeFace(request):
    form = RemoveEmployee()
    if request.method == 'POST':
        employee_id_number = request.POST.get('employee_id_num')
        faceIdList = request.POST.getlist('employee_face_id[]')

        if Employee.objects.filter(employee_id_num=employee_id_number, active=True):
            empInst = Employee.objects.filter(employee_id_num=employee_id_number, active=True)[0]
            
            for imageId in faceIdList:
                empFace = FacesDB.objects.filter(employee_id_num = empInst, id=imageId)[0]

                empFace.active = False
                empFace.save()

            messages.success(request, 'Employee face successfully removed!')
            return render(request,'app/custom/removeImage.html',{'title': 'Remove Employee Face', 'form': form,})
    else:
        return render(request,'app/custom/removeImage.html',{'title': 'Remove Employee Face', 'form': form,})

    return render(request,'app/custom/removeImage.html',{'title': 'Remove Employee Face', 'form': form,})

@login_required
@permission_required("app.edit_removed_user_records")
def restoreRemovedEmployee(request):
    form = RestoreRemovedEmployee()
    if request.method == 'POST':
        employee_id_number = request.POST.get('employee_id_num')
        if Employee.objects.filter(employee_id_num=employee_id_number, active=False):
            empInst = Employee.objects.filter(employee_id_num=employee_id_number, active=False)[0]
            empInst.active = True
            empInst.save()
            messages.success(request, 'Employee successfully restored!')
            return render(request,'app/custom/restoreRemovedEmployee.html',{'title': 'Removed Employees', 'form': form,})
    else:
        return render(request,'app/custom/restoreRemovedEmployee.html',{'title': 'Removed Employees', 'form': form,})

    return render(request,'app/custom/restoreRemovedEmployee.html',{'title': 'Removed Employees', 'form': form,})
@login_required
@permission_required("app.edit_removed_user_records")
def recoverRemovedFace(request):
    form = RemoveEmployee()
    if request.method == 'POST':
        employee_id_number = request.POST.get('employee_id_num')
        faceIdList = request.POST.getlist('employee_face_id[]')

        if Employee.objects.filter(employee_id_num=employee_id_number, active=True):
            empInst = Employee.objects.filter(employee_id_num=employee_id_number, active=True)[0]
            
            for imageId in faceIdList:
                empFace = FacesDB.objects.filter(employee_id_num = empInst, id=imageId)[0]

                empFace.active = True
                empFace.save()

            messages.success(request, 'Employee face successfully recovered!')
            return render(request,'app/custom/restoreRemovedEmployee.html',{'title': 'Recover Remove Employee Face', 'form': form,})
    return render(request,'app/custom/restoreRemovedEmployee.html',{'title': 'Recover Removed Employee Face', 'form': form,})


def startPage(request):
    
    fr_view.initializeCamera()
    ltAttEntTime = ""
    ltAttEntName = ""
    ltAttEntType = ""
    

    ltTimeInRow = AttendanceLog.objects.all().order_by('-time_in')[0]
    ltTimeOutRow = AttendanceLog.objects.all().order_by('-time_out')[0]

    if ltTimeInRow.time_in > ltTimeOutRow.time_out:
        ltAttEntTime = ltTimeInRow.time_in 
        ltAttEntName = ltTimeInRow.employee_id_num.first_name + " " + ltTimeInRow.employee_id_num.last_name
        ltAttEntType = "Time-In"
    else:
        ltAttEntTime = ltTimeOutRow.time_out
        ltAttEntName = ltTimeOutRow.employee_id_num.first_name + " " + ltTimeOutRow.employee_id_num.last_name
        ltAttEntType = "Time-Out"

    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/custom/startPage.html',
        {
            'title':'A.L.S.W.F.R',
            'num_of_employees': str(Employee.objects.filter(active=True).count()),
            'last_detect_type':ltAttEntType,
            'last_detect_time':ltAttEntTime,
            'last_detect_name':ltAttEntName,
        }
    )

#Json Requests
@login_required
def getEmployeeDataUsingEmpNum(request):
    if request.method == 'GET':
        employeeIdNum = request.GET.get('employee_number')

        if type(employeeIdNum) != NoneType:
            try:
                employeeInstance = Employee.objects.filter(employee_id_num=int(employeeIdNum))[0]

                response = {
                    'first_name': employeeInstance.first_name,
                    'middle_name': employeeInstance.middle_name,
                    'last_name': employeeInstance.last_name,
                    'contact_number': employeeInstance.contact_number,
                    'email': employeeInstance.email_address,
                    }
                return JsonResponse(response)
            except:
                placeholder = 'N/A'
                response = {
                    'first_name': placeholder,
                    'middle_name': placeholder,
                    'last_name': placeholder,
                    'contact_number': placeholder,
                    'email': placeholder,
                    }
                return JsonResponse(response)
def getImages(request):
    if request.method == 'GET':
        employeeIdNum = request.GET.get('employee_number')
        results = {}

        if type(employeeIdNum) != NoneType:
            try:
                employeeInstance = Employee.objects.filter(employee_id_num=int(employeeIdNum))[0]
                employeeFaces = FacesDB.objects.filter(employee_id_num = employeeInstance, active=True)
                counter = 0

                for face in employeeFaces:
                    results[counter] = {
                        'id':face.id,
                        'filepath':base64.b64encode(cv2.imencode('.png', numpy.asarray(Image.open(str(face.image.file))))[1]).decode('utf-8'),
                        }
                    counter += 1
            except:
                return JsonResponse(results)
            
        return JsonResponse(results)
def getRemovedImages(request):
    if request.method == 'GET':
        employeeIdNum = request.GET.get('employee_number')
        results = {}

        if type(employeeIdNum) != NoneType:
            try:
                employeeInstance = Employee.objects.filter(employee_id_num=int(employeeIdNum))[0]
                employeeFaces = FacesDB.objects.filter(employee_id_num = employeeInstance, active=False)
                counter = 0

                for face in employeeFaces:
                    results[counter] = {
                        'id':face.id,
                        'filepath':base64.b64encode(cv2.imencode('.png', numpy.asarray(Image.open(str(face.image.file))))[1]).decode('utf-8'),
                        }
                    counter += 1
            except:
                return JsonResponse(results)
            
        return JsonResponse(results)