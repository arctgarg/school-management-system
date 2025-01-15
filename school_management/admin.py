from django.contrib import admin
from .models import AcademicYear, Grade, Student, StudentEnrollment, FeePayment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'first_name', 'last_name', 'is_active')
    search_fields = ('admission_number', 'first_name', 'last_name')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'grade', 'total_fee', 'fee_concession', 'net_fee')
    list_filter = ('academic_year', 'grade')

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'payment_date', 'amount', 'receipt_number')
    list_filter = ('payment_date', 'payment_mode')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'annual_fee')

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')