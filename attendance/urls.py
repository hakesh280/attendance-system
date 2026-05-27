from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-student/', views.add_student, name='add_student'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-report/', views.attendance_report, name='attendance_report'),
   path('attendance-percentage/', views.attendance_percentage, name='attendance_percentage'),
   path('dashboard/', views.dashboard, name='dashboard'),
   path('student-list/', views.student_list, name='student_list'),
   path('delete-student/<int:id>/', views.delete_student, name='delete_student'),
   path('edit-student/<int:id>/', views.edit_student, name='edit_student'),
path('login/', views.login_page, name='login'),

]