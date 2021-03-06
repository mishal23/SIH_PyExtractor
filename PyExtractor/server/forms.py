from datetime import date
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from server.models import DEPARTMENTS, asset, CHOICE, Account


def validate_username_available(username):
    """ validator that throws an error if the given username already exists."""

    if User.objects.filter(username__icontains=username).count():
        raise forms.ValidationError("This email is already registered")


def validate_username_exists(username):
    """ validator that throws an error if the given username doesn't exists."""

    if not User.objects.filter(username__icontains=username).count():
        raise forms.ValidationError("This email does not exist")


def setup_field(field, placeholder=None):
    """
    This configures the given field to play nice with the bootstrap theme. Additionally, you can add
    an additional argument to set a placeholder text on the field.
    """
    field.widget.attrs['class'] = 'form-control'
    if placeholder is not None:
        field.widget.attrs['placeholder'] = placeholder


class BasicForm(forms.Form):
    def disable_field(self, field):
        """
        marks field as disabled
        :param field: name of the field
        """
        self.fields[field].widget.attrs['disabled'] = ""

    def mark_error(self, field, description):
        """
        Marks the given field as errous. The given description is displayed when the form it generated
        :param field: name of the field
        :param description: The error description
        """
        self._errors[field] = self.error_class([description])
        del self.cleaned_data[field]

    def clear_errors(self):
        self._errors = {}


class LoginForm(BasicForm):
    email = forms.EmailField(max_length=50,validators=[validate_username_exists])
    setup_field(email,'Enter Email here')
    password = forms.CharField(max_length=50,widget=forms.PasswordInput())
    setup_field(password,'Enter password here')

    def clean(self):
        """
        This is to make sure the password is valid for the given email.
        """
        cleaned_data = super(LoginForm,self).clean()
        username = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                self.mark_error('password', 'Incorrect password')
        return cleaned_data


class UserRegistrationForm(BasicForm):
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")
    employee = forms.ChoiceField(required=False, choices=Account.EMPLOYEE_TYPES)
    setup_field(employee)

    def clean(self):
        """
        This is to make sure both passwords fields have the same values in them. If they don't mark
        them as errous.
        """
        cleaned_data = super(UserRegistrationForm,self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second and password_first!=password_second:
            self.mark_error('password_second', 'Passwords do not match')
        return cleaned_data


class AccountRegisterForm(BasicForm):
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")

    def clean(self):
        """This is to make sure both passwords fields have the same values in them. If they don't mark
        them as erroneous."""
        cleaned_data = super(AccountRegisterForm, self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second and password_first!=password_second:
            self.mark_error('password_second','Passwords do not match')
        return cleaned_data


class UploadForm(BasicForm):
    file = forms.FileField()
    setup_field(file,'Choose a zip')


class QueryForm(BasicForm):
    latitude = forms.CharField(required=True, max_length=50)
    setup_field(latitude,'Enter the latitude')
    longitude = forms.CharField(required=True, max_length=50)
    setup_field(longitude,'Enter the longitude')
    
    distance = forms.CharField(required=True, max_length=50)
    setup_field(distance,'Enter the distance(in km)')	

    department = forms.ChoiceField(choices=DEPARTMENTS)
    setup_field(department,'Select the department')

    year = forms.CharField(required=False,max_length=4)
    setup_field(year, 'Enter the start year')

    input_text_type = forms.CharField(required=False, max_length=50)
    setup_field(input_text_type,'Enter the type of asset')
    input_text_capacity = forms.CharField(required=False, max_length=50)
    setup_field(input_text_capacity,'Enter the capacity')

    def assign(self, query):
        query.department = self.cleaned_data['department']
        query.latitude = self.cleaned_data['latitude']
        query.longitude = self.cleaned_data['longitude']
        query.distance = self.cleaned_data['distance']
        query.year = self.cleaned_data['year']
        if self.cleaned_data['input_text_type'] == None:
            query.input_text_type = None
        else:
            query.input_text_type = self.cleaned_data['input_text_type']
        if self.cleaned_data['input_text_capacity'] == None:
            query.input_text_capacity = None
        else:
            query.input_text_capacity = self.cleaned_data['input_text_capacity']
 

class AssetForm(BasicForm):
    img_name = forms.CharField(required=True,max_length=50)
    setup_field(img_name,'Enter the Image name')   
    img_path = forms.CharField(required=True,max_length=50)
    setup_field(img_path,'Enter the image path')
    latitude = forms.CharField(required=True,max_length=50)
    setup_field(latitude,'Enter the latitude')
    longitude = forms.CharField(required=True,max_length=50)
    setup_field(longitude,'Enter the longitude')

    extracted_text = forms.CharField(required=False,max_length=500)
    setup_field(extracted_text, 'Enter the extracted text')
    department = forms.ChoiceField(choices=DEPARTMENTS)
    setup_field(department,'Enter the department')

    input_text_type = forms.CharField(required=False, max_length=50)
    setup_field(input_text_type,'Enter the type of asset')
    input_text_capacity = forms.CharField(required=False, max_length=50)
    setup_field(input_text_capacity,'Enter the capacity')

    def assign(self, query):
        query.img_name = self.cleaned_data['img_name']
        query.img_path = self.cleaned_data['img_path']
        query.latitude = self.cleaned_data['latitude']
        query.longitude = self.cleaned_data['longitude']
        query.extracted_text = self.cleaned_data['extracted_text']
        query.department = self.cleaned_data['department']
        if self.cleaned_data['input_text_type'] == None:
            query.input_text_type = None
        else:
            query.input_text_type = self.cleaned_data['input_text_type']
        if self.cleaned_data['input_text_capacity'] == None:
            query.input_text_capacity = None
        else:
            query.input_text_capacity = self.cleaned_data['input_text_capacity']
 