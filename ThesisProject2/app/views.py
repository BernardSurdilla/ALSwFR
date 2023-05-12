"""
Definition of views.
"""

from datetime import datetime
import json
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse

from django.contrib import messages
from .forms import FaceRegistrationForm, UpdateFaceRegistrationForm
from .models import Employee, FacesDB, AttendanceLog
from django.contrib.auth.models import User

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

#Requests for returning data from database
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

def getEmployeeDataUsingEmpNum(request):
    if request.method == 'POST':
        employee = Employee()
        empNum = employee.employee_number = request.POST.get('employee_number')
        query_results = Employee.objects.filter(employee_number=empNum)
        print(query_results)

        response = {
            'succ':'succ'
            }
        return JsonResponse(response)

def editUser(request):
    query_results = Employee.objects.values('employee_number')[0]

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
    """
    {{ form.employee_number }}
    {{ form.first_name }}
    {{ form.middle_name }}
    {{ form.last_name }}
    {{ form.contact_number }}
    {{ form.email_address }}
    """
    if request.method == 'POST':
        form = FaceRegistrationForm()
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
            return render(request, 'app/custom/registrationForm.html', {'form': form})
        else:
            messages.error(request, 'Invalid data input! Try again.')
    else:
        form = FaceRegistrationForm()
    return render(request, 'app/custom/registrationForm.html', {'form': form})

def insertImgArr(request):
    pass