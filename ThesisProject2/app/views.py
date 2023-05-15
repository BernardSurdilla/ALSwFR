"""
Definition of views.
"""

import base64
import os
import string
import random
from time import sleep

from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import FaceRegistrationForm, UpdateFaceRegistrationForm
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
def startPage(request):
    
    fr_view.startCamera()
    """Renders the startPage html."""
    assert isinstance(request, HttpRequest)

    cameraOnly = request.user.has_perm("be_camera")

    return render(
        request,
        'app/custom/startPage.html',
        {
            'title':'A.L.S.W.F.R',
        }
    )

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
def viewEmployees(request):
    query_results = Employee.objects.all()
    return render(
        request, 
        'app/custom/viewEmployees.html', 
        {
            'title':'Employees',
            'table_data': query_results,
        }
    )
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
def employeeData(request):
    """Renders the startPage html."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/custom/employeeData.html',
        {
            'title':'Employee Data',
        }
    )

#Requests for returning data from database with html page, and editing data
def editUser(request):
    query_results = Employee.objects.values('employee_id_num')[0]

    """
    {{ form.employee_number }}
    {{ form.first_name }}
    {{ form.middle_name }}
    {{ form.last_name }}
    {{ form.contact_number }}
    {{ form.email_address }}
    """
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
            return render(request, 'app/custom/updateForm.html', {'form': form})
        else:
            messages.error(request, 'Invalid data input! Try again.')
    else:
        form = UpdateFaceRegistrationForm()

    return render(request, 'app/custom/updateForm.html', {'form': form})
def faceRecogForm(request):
    if request.method == 'POST':
        form = FaceRegistrationForm()
        if request.POST.getlist('capturedImages[]'):
            employee = Employee()
            employee.employee_id_num = request.POST.get('employee_id_num')
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.middle_name = request.POST.get('middle_name')
            employee.contact_number = request.POST.get('contact_number')
            employee.email_address = request.POST.get('email_address')
            employee.save()

            #Insert Images into facedb table
            facedb = FacesDB()
            imgArr = request.POST.getlist('capturedImages[]')
            tempPath = settings.TEMP_IMG_FOLDER
            if imgArr:
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
                    facedb.employee_id_num = employee
                    facedb.image.save(str(res) + '.png', open(tempImgFilePath, 'rb'))
                    facedb.save()       

            messages.success(request, 'Employee successfully registered!')
            return render(request, 'app/custom/registrationForm.html', {'form': form})
        else:
            messages.error(request, 'Invalid data input! Try again.')
    else:
        form = FaceRegistrationForm()
    return render(request, 'app/custom/registrationForm.html', {'form': form})
def insertImgArr(request):
    if request.method == 'POST':
        #Get the image array and employee id passed
        imgArr = request.POST.getlist('capturedImages[]')
        emp_id = request.POST.get('employee_id_num')

        tempPath = settings.TEMP_IMG_FOLDER
        if imgArr:
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
                facedb.employee_id_num = Employee.objects.get(employee_id_num=emp_id)
                facedb.image.save(str(res) + '.png', open(tempImgFilePath, 'rb'))
                facedb.save()       
    pass

#Json Requests
def getEmployeeDataUsingEmpNum(request):
    if request.method == 'GET':
        cur_employee_id_num = request.GET.get('employee_id_num')
        if cur_employee_id_num:
            query_results = Employee.objects.filter(employee_id_num=cur_employee_id_num)[0]
            response = {
                'first_name': query_results.first_name,
                'middle_name': query_results.middle_name,
                'last_name': query_results.last_name,
                'contact_number': query_results.contact_number,
                'email': query_results.email_address,
                }
            return JsonResponse(response)
        else:
            return JsonResponse({})
    """
    if request.method == 'POST':
        employee = Employee()
        empNum = employee.employee_number = request.POST.get('employee_number')
        query_results = Employee.objects.filter(employee_number=empNum)

        response = {
            'succ':'succ'
            }
        return JsonResponse(response)
    """