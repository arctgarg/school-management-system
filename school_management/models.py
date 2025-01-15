from django.db import models
from django.utils import timezone

class AcademicYear(models.Model):
    name = models.CharField(max_length=20)  # e.g., "2023-2024"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Grade 1", "Grade 2"
    annual_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Student(models.Model):
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    admission_date = models.DateField()
    parent_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.admission_number} - {self.first_name} {self.last_name}"

class StudentEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    fee_concession = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['student', 'academic_year']

    @property
    def net_fee(self):
        return self.total_fee - self.fee_concession

    @property
    def monthly_installment(self):
        return self.net_fee / 12

class FeePayment(models.Model):
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)  # e.g., "Cash", "Online"
    receipt_number = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.enrollment.student}" 