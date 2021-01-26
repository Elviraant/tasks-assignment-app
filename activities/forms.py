from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
from datetime import date

default_errors = {
    'required': 'Η συμπλήρωση του πεδίου είναι υποχρεωτική',
    'invalid': 'Η τιμή δεν είναι έγκυρη'
}

def min_date_validator(value):
    if (value is not None):
        if (value < date.today()):
            raise ValidationError('Η ημερομηνία πρέπει να είναι μετά τις ' + date.today().strftime('%m/%d/%Y'))
    else:
        raise ValidationError('Η συμπλήρωση του πεδίου είναι υποχρεωτική')

class LoginForm(AuthenticationForm):
    username = forms.CharField( label='', error_messages=default_errors,
                                widget=forms.TextInput(attrs={'class': 'fadeIn second', 'placeholder': 'Όνομα Χρήστη'}))
    password = forms.CharField( label='', error_messages=default_errors,
                                widget=forms.PasswordInput(attrs={'class': 'fadeIn third', 'placeholder': 'Κωδικός Πρόσβασης'}))

class EditForm(forms.Form):
    title = forms.CharField( label='Τίτλος', error_messages=default_errors,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Τίτλος'}))
    description = forms.CharField( label='Περιγραφή', required = False, error_messages=default_errors,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Περγραφή', }) )
    deadline = forms.DateField( label='Προθεσμία', validators=[min_date_validator], error_messages=default_errors,
                                widget=forms.DateInput(attrs={'type':'date', 'class': 'form-control', 'placeholder': 'Προθεσμία', 'onclick': 'dateFunction()' }))
    receiver = forms.IntegerField( label='Έχετε αναθέσει την αρμοδιότητα στο χρήστη', required = False, error_messages=default_errors,
                                  widget=forms.Select(attrs={'class': 'form-control', }))

    def __init__(self, *args, employee=None, **kwargs):

        self.parent_project_date=kwargs.pop('parent_project_date')
        super(EditForm, self).__init__(*args,**kwargs)

        if (self.parent_project_date is not None):
            self.update_deadline_max(self.parent_project_date)

        if (employee is not None):
            self.set_receiver_choices(employee.receiver_choices())

    def clean(self):
        cleaned_data = super(EditForm, self).clean()

        deadline = cleaned_data.get('deadline')
        parent_project_date = self.parent_project_date
        if (parent_project_date is not None):
            if (deadline > self.parent_project_date):
                raise ValidationError("Προθεσμία: Η ημερομηνία πρέπει να είναι πριν τις " + self.parent_project_date.strftime('%m/%d/%Y'))

    def update_deadline_max(self, max):
        self.fields['deadline'].widget.attrs.update({ 'max': max })

    def set_receiver_choices(self, choices):
        self.fields['receiver'].widget.choices = choices


class SelectForm(forms.Form):
    project_task_id = forms.IntegerField(label='Επιλέξτε μια αρμοδιότητα για να την τροποποιήσετε',
                                         error_messages=default_errors,
                                         widget=forms.Select(attrs={'class': 'form-control',}))

    def set_choices(self, choices):
        self.fields['project_task_id'].widget.choices = choices
