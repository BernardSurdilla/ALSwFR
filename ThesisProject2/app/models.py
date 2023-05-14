"""
Definition of models.
"""

from django.db import models

# Create your models here.
"""
Definition of models.
"""

from django.db import models

# Create your models here.
class AppPerms(models.Model):
    ...
    class Meta:
        permissions = [
            ("edit_attendance_records", "Can change the attendance records"),
            ("check_attendance_records", "Can check the attendance records"),
            
            ("edit_user_records", "Can change the registered users"),
            ("check_user_records", "Can check the registered users"),

            ("edit_employee_data", "Can change the employee data"),
            ("check_employee_data", "Can check the employee data"),

            ("check_camera", "Can check the feed connected cameras to the network"),
            ("be_camera", "Can be a camera in the network"),

        ]

class Employee(models.Model):
    employee_id_num = models.BigIntegerField(primary_key=True, max_length=30)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField(max_length=254, blank=True)

class FacesDB(models.Model):
    employee_id_num = models.ForeignKey(Employee, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='faces/%Y/%m/%d')

class AttendanceLog(models.Model):
    employee_id_num = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_in = models.DateTimeField(blank=False)
    time_out = models.DateTimeField(blank=True)