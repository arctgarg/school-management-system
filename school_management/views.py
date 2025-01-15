from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .models import Student, FeePayment, AcademicYear
from .forms import StudentAdmissionForm
from .models import StudentEnrollment
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView
from .models import Student, Grade
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import FeePaymentForm
from .models import StudentEnrollment, FeePayment
import datetime

from django.views.generic import DetailView
from django.db.models import Sum
from .models import Student, StudentEnrollment

from django.views.generic import TemplateView
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from datetime import datetime
from .models import Student, Grade, StudentEnrollment, FeePayment, AcademicYear

from django.views.generic import TemplateView
from django.db.models import Count, Sum, F, Q, DecimalField
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import datetime
from .models import Student, Grade, StudentEnrollment, FeePayment, AcademicYear
from django.db.models.functions import Cast, Coalesce 

from django.views.generic import TemplateView
from django.db.models import Count, Sum, F, Q, DecimalField
from django.db.models.functions import Cast, Coalesce 
from django.utils import timezone
from datetime import datetime
import json
from .models import Student, Grade, StudentEnrollment, FeePayment, AcademicYear

class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'school_management/reports_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = AcademicYear.objects.filter(is_active=True).first()
        
        # Get selected year from query params, default to current year
        selected_year_id = self.request.GET.get('academic_year', current_year.id if current_year else None)
        selected_grade = self.request.GET.get('grade')
        
        context['selected_year'] = selected_year_id
        context['selected_grade'] = selected_grade
        context['academic_years'] = AcademicYear.objects.all().order_by('-start_date')
        context['grades'] = Grade.objects.all()
        
        # Class-wise student count
        class_stats = Grade.objects.annotate(
            student_count=Count('studentenrollment',
                filter=Q(studentenrollment__academic_year_id=selected_year_id)),
            total_fee=Sum('studentenrollment__total_fee',
                filter=Q(studentenrollment__academic_year_id=selected_year_id)),
            collected_fee=Sum('studentenrollment__feepayment__amount',
                filter=Q(studentenrollment__academic_year_id=selected_year_id))
        ).values('name', 'student_count', 'total_fee', 'collected_fee')
        
        context['class_stats'] = class_stats
        
        # Prepare chart data
        context['class_stats_data'] = json.dumps({
            'labels': [stat['name'] for stat in class_stats],
            'totalFee': [float(stat['total_fee'] or 0) for stat in class_stats],
            'collectedFee': [float(stat['collected_fee'] or 0) for stat in class_stats]
        })
        
        # Monthly fee collection data
        monthly_collection = FeePayment.objects.filter(
            enrollment__academic_year_id=selected_year_id
        ).annotate(
            month=Cast('payment_date__month', output_field=DecimalField())
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        context['monthly_collection'] = monthly_collection
        context['monthly_collection_data'] = json.dumps({
            'labels': [datetime.strptime(str(m['month']), "%m").strftime("%B") for m in monthly_collection],
            'values': [float(m['total']) for m in monthly_collection]
        })
        
        # Rest of your existing context data
        context['total_students'] = StudentEnrollment.objects.filter(
            academic_year_id=selected_year_id
        ).count()
        
        context['total_fee'] = StudentEnrollment.objects.filter(
            academic_year_id=selected_year_id
        ).aggregate(total=Sum('total_fee'))['total'] or 0
        
        context['total_collected'] = FeePayment.objects.filter(
            enrollment__academic_year_id=selected_year_id
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return context

class StudentProfileView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'school_management/student_profile.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get all enrollments ordered by academic year
        enrollments = student.studentenrollment_set.all().order_by(
            '-academic_year__start_date'
        ).select_related('grade', 'academic_year')
        
        # Calculate fee details for each enrollment
        enrollment_details = []
        for enrollment in enrollments:
            fee_paid = enrollment.feepayment_set.aggregate(
                total_paid=Sum('amount'))['total_paid'] or 0
            
            enrollment_details.append({
                'enrollment': enrollment,
                'fee_paid': fee_paid,
                'fee_balance': enrollment.total_fee - fee_paid,
                'payments': enrollment.feepayment_set.all().order_by('-payment_date')[:5]  # Last 5 payments
            })
        
        context['enrollment_details'] = enrollment_details
        return context

class StudentFeeView(LoginRequiredMixin, DetailView):
    model = StudentEnrollment
    template_name = 'school_management/student_fee_detail.html'
    context_object_name = 'enrollment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_object()
        
        # Calculate fee details
        context['total_fee'] = enrollment.total_fee
        context['fee_paid'] = enrollment.feepayment_set.aggregate(
            total_paid=Sum('amount'))['total_paid'] or 0
        context['fee_balance'] = enrollment.total_fee - context['fee_paid']
        
        # Calculate monthly installments
        context['monthly_installment'] = enrollment.total_fee / 12
        
        # Get payment history
        context['payments'] = enrollment.feepayment_set.all().order_by('-payment_date')
        
        # Calculate monthly status
        current_month = datetime.now().month
        expected_payment = (enrollment.total_fee / 12) * current_month
        context['payment_status'] = "Up to date" if context['fee_paid'] >= expected_payment else "Pending"
        
        return context

class CollectFeeView(LoginRequiredMixin, CreateView):
    model = FeePayment
    form_class = FeePaymentForm
    template_name = 'school_management/collect_fee.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment_id = self.kwargs.get('enrollment_id')
        enrollment = get_object_or_404(StudentEnrollment, id=enrollment_id)
        context['enrollment'] = enrollment
        context['fee_paid'] = enrollment.feepayment_set.aggregate(
            total_paid=Sum('amount'))['total_paid'] or 0
        context['fee_balance'] = enrollment.total_fee - context['fee_paid']
        return context
    
    def form_valid(self, form):
        enrollment_id = self.kwargs.get('enrollment_id')
        enrollment = get_object_or_404(StudentEnrollment, id=enrollment_id)
        
        # Set the enrollment and generate receipt number
        form.instance.enrollment = enrollment
        form.instance.receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{enrollment.id}"
        
        response = super().form_valid(form)
        messages.success(self.request, 'Fee payment recorded successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('school_management:student_fee_detail', 
                          kwargs={'pk': self.kwargs.get('enrollment_id')})

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'school_management/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_year = AcademicYear.objects.filter(is_active=True).first()
        
        # Get total students
        context['total_students'] = Student.objects.filter(is_active=True).count()
        
        # Fix the aggregation query
        fee_total = FeePayment.objects.filter(
            enrollment__academic_year=current_year
        ).aggregate(
            total_amount=Sum('amount')  # Give it a specific name
        )
        context['total_fee_collected'] = fee_total['total_amount'] or 0
        
        return context
    

class StudentAdmissionView(LoginRequiredMixin, CreateView):
    form_class = StudentAdmissionForm
    template_name = 'school_management/student_admission.html'
    success_url = reverse_lazy('school_management:dashboard')

    def form_valid(self, form):
        form.instance.admission_date = timezone.now().date()
        
        response = super().form_valid(form)

        # Get the current academic year
        current_year = AcademicYear.objects.filter(is_active=True).first()
        
        # Create student enrollment
        StudentEnrollment.objects.create(
            student=self.object,  # newly created student
            academic_year=current_year,
            grade=form.cleaned_data['grade'],
            total_fee=form.cleaned_data['grade'].annual_fee,
            fee_concession=0  # default value, can be updated later
        )
        
        messages.success(self.request, f'Student {self.object.first_name} admitted successfully!')
        return response
    
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'school_management/student_list.html'
    context_object_name = 'students'
    
    def get_queryset(self):
        queryset = Student.objects.filter(is_active=True)
        
        # Get filter parameters
        grade_id = self.request.GET.get('grade')
        academic_year_id = self.request.GET.get('academic_year')
        
        if grade_id and academic_year_id:
            queryset = queryset.filter(
                studentenrollment__grade_id=grade_id,
                studentenrollment__academic_year_id=academic_year_id
            )
        elif academic_year_id:
            queryset = queryset.filter(
                studentenrollment__academic_year_id=academic_year_id
            )
        elif grade_id:
            queryset = queryset.filter(
                studentenrollment__grade_id=grade_id,
                studentenrollment__academic_year__is_active=True
            )
        else:
            queryset = queryset.filter(
                studentenrollment__academic_year__is_active=True
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = Grade.objects.all()
        context['academic_years'] = AcademicYear.objects.all().order_by('-start_date')
        context['selected_grade'] = self.request.GET.get('grade')
        context['selected_year'] = self.request.GET.get('academic_year')
        return context