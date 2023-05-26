"""
Definition of forms.
"""

from audioop import mul
from django import forms
from .models import Employee
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class FaceRegistrationForm(forms.Form):
    employee_id_num = forms.IntegerField(label="Employee Number", widget=forms.NumberInput({
                                   'class': 'form-control',
                                   'placeholder': 'Employee Number'}))

    first_name = forms.CharField(label="Firstname", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Lastname", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Last Name'}))
    middle_name = forms.CharField(label="Middlename", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Middle Name'}))
    contact_number = forms.CharField(label="Contact Number", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Contact Number'}))
    email_address = forms.EmailField(label="Email", max_length=254, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email address'}))

class UpdateFaceRegistrationForm(forms.Form):
    employee_id_num = forms.ModelChoiceField(label="Employee Number", queryset=Employee.objects.filter(active=True).values_list("employee_id_num", flat=True), )

    first_name = forms.CharField(label="Firstname", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Lastname", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Last Name'}))
    middle_name = forms.CharField(label="Middlename", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Middle Name'}))
    contact_number = forms.CharField(label="Contact Number", max_length=20, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Contact Number'}))
    email_address = forms.EmailField(label="Email", max_length=254, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email address'}))

class RegisterFaceForm(forms.Form):
    employee_id_num = forms.ModelChoiceField(label="Employee Number", queryset=Employee.objects.filter(active=True).values_list("employee_id_num", flat=True), )

    first_name = forms.CharField(label="Firstname", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Lastname", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Last Name'}))
    middle_name = forms.CharField(label="Middlename", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Middle Name',}))

class RemoveEmployee(forms.Form):
    employee_id_num = forms.ModelChoiceField(label="Employee Number", queryset=Employee.objects.filter(active=True).values_list("employee_id_num", flat=True), )

    first_name = forms.CharField(label="Firstname", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Lastname", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Last Name'}))
    middle_name = forms.CharField(label="Middlename", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Middle Name',}))
    contact_number = forms.CharField(label="Contact Number", max_length=20, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Contact Number'}))
    email_address = forms.EmailField(label="Email", max_length=254, disabled=True, widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email address'}))