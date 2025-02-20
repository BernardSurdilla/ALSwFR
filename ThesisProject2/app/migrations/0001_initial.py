# Generated by Django 4.1.7 on 2023-05-06 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppPerms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': [('edit_attendance_records', 'Can change the attendance records'), ('check_attendance_records', 'Can check the attendance records'), ('edit_user_records', 'Can change the registered users'), ('check_user_records', 'Can check the registered users'), ('edit_employee_data', 'Can change the employee data'), ('check_employee_data', 'Can check the employee data'), ('check_camera', 'Can check the feed connected cameras to the network'), ('be_camera', 'Can be a camera in the network')],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('employee_number', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=20)),
                ('middle_name', models.CharField(blank=True, max_length=20)),
                ('contact_number', models.CharField(blank=True, max_length=20)),
                ('email_address', models.EmailField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FacesDB',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='faces/%Y/%m/%d')),
                ('employee_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.employee')),
            ],
        ),
    ]
