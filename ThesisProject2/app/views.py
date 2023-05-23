"""
Definition of views.
"""

import base64
import os
import string
import random
from time import sleep
from types import NoneType

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import FaceRegistrationForm, UpdateFaceRegistrationForm, RegisterFaceForm
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
    #The view for user registration
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

            messages.success(request, 'Employee successfully registered!')
            return render(request, 'app/custom/registrationForm.html', {'form': form})
        else:
            messages.error(request, 'Invalid data input! Try again.')
    else:
        form = FaceRegistrationForm()
    return render(request, 'app/custom/registrationForm.html', {'form': form})
def insertImgArr(request):
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
                messages.success(request, 'Employee successfully registered!')
        else:
            messages.error(request, 'Invalid data input! Try again.')
    pass
def uploadImages(request):
    form = RegisterFaceForm()
    return render(
        request, 
        'app/custom/uploadImages.html', 
        {
            'form': form,
        }
    )
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
            'num_of_employees': str(Employee.objects.all().count()),
            'last_detect_type':ltAttEntType,
            'last_detect_time':ltAttEntTime,
            'last_detect_name':ltAttEntName,
        }
    )

#Json Requests
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