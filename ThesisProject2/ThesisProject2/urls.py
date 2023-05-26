"""
Definition of urls for ThesisProject2.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views
from app.facial_recognition import fr_view

urlpatterns = [

    path('', views.startPage, name='home'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('feed/', views.liveCamFeed, name='liveCamFeed'),

    #Views for viewing data on db
    path('employee_data/', views.viewEmployees, name='viewEmployees'),
    path('employee_data/employee_registration/', views.faceRecogForm, name='registerEmployee'),
    path('employee_data/update_employees/', views.editUser, name='updateEmployees'),
    path('employee_data/add_face/', views.uploadImages, name='uploadImages'),
    path('employee_data/remove_employee/', views.removeEmployee, name='removeEmployee'),
    path('employee_data/view_removed_employee/', views.viewRemovedEmployees, name='removedEmployees'),

    path('attendance_log/', views.attendanceLog, name='attendanceLog'),
    path('users/', views.viewUsers, name='users'),

    #Camera View
    path('camera_only/', fr_view.face_recog, name='employeeFeedView'),

    #For sending json objects with the current camera output
    path('camFrame/', fr_view.jsonVidImgResp, name='imgOutput'),
    path('camFrameOF/', fr_view.jsonVidImgRespWOrigImg, name='imgOutputWOrigFrame'),
    path('getDT/', views.getEmployeeDataUsingEmpNum, name='getEmpData'),

    #For uploading images
    path('upImg', views.insertImgArr, name='insertImgArr')


]

