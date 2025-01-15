from django import forms
from .models import Student, StudentEnrollment, Grade, AcademicYear
from django import forms
from .models import FeePayment

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['amount', 'payment_mode', 'payment_date', 'remarks']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'payment_mode': forms.Select(choices=[
                ('CASH', 'Cash'),
                ('ONLINE', 'Online Transfer'),
                ('CHEQUE', 'Cheque'),
            ])
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount

class StudentAdmissionForm(forms.ModelForm):
    grade = forms.ModelChoiceField(
        queryset=Grade.objects.all(), 
        label='Class',
        empty_label="Select Class"
    )
    
    class Meta:
        model = Student
        fields = [
            'admission_number', 
            'first_name', 
            'last_name', 
            'date_of_birth', 
            'parent_name', 
            'contact_number', 
            'address'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter 10-digit mobile number'}),
        }

    def clean_admission_number(self):
        admission_number = self.cleaned_data.get('admission_number')
        if Student.objects.filter(admission_number=admission_number).exists():
            raise forms.ValidationError("This admission number already exists!")
        return admission_number

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact.isdigit() or len(contact) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit mobile number")
        return contact