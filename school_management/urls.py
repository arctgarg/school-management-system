from django.urls import path
from . import views

app_name = 'school_management'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('student/add/', views.StudentAdmissionView.as_view(), name='student_admission'),
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('student/<int:pk>/fee/', views.StudentFeeView.as_view(), name='student_fee_detail'),
    path('student/<int:enrollment_id>/collect-fee/', views.CollectFeeView.as_view(), name='collect_fee'),
    path('student/<int:pk>/profile/', views.StudentProfileView.as_view(), name='student_profile'),
    path('reports/', views.ReportsDashboardView.as_view(), name='reports_dashboard'),
]