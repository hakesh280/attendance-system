from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, F, Sum
from django.utils import timezone
from datetime import timedelta, datetime, date
from django.contrib.auth.models import User
from collections import OrderedDict

from .forms import PasswordChangeByRoleForm
from .models import (
    Student, Staff, Subject, Attendance, AttendanceAdjustment, Notification,
    Period, StaffSubjectAssignment, DaySchedule
)


# ===== DECORATORS FOR ROLE-BASED ACCESS =====

def is_admin(user):
    """Check if user is admin."""
    return user.is_staff or user.is_superuser

def is_staff_user(user):
    """Check if user is a staff member."""
    try:
        return hasattr(user, 'staff_profile') and user.staff_profile is not None
    except:
        return False

def is_student_user(user):
    """Check if user is a student."""
    try:
        return hasattr(user, 'student_profile') and user.student_profile is not None
    except:
        return False

def admin_required(view_func):
    """Decorator to check if user is admin."""
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_required(view_func):
    """Decorator to check if user is staff."""
    def wrapper(request, *args, **kwargs):
        if not (is_staff_user(request.user) or is_admin(request.user)):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    """Decorator to check if user is student."""
    def wrapper(request, *args, **kwargs):
        if not is_student_user(request.user):
            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def working_days_between(start_date, end_date):
    """Count weekdays after start_date through end_date."""
    if start_date >= end_date:
        return 0

    days = 0
    current = start_date + timedelta(days=1)
    while current <= end_date:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days


def get_attendance_stats(student):
    total_classes = Attendance.objects.filter(student=student).count()
    attended_classes = Attendance.objects.filter(
        student=student,
        status='Present'
    ).count()
    adjustment_count = AttendanceAdjustment.objects.filter(
        student=student
    ).aggregate(total=Sum('attendance_count'))['total'] or 0

    adjusted_attended = attended_classes + adjustment_count
    adjusted_total = total_classes + adjustment_count
    percentage = (adjusted_attended / adjusted_total * 100) if adjusted_total > 0 else 0

    return {
        'total_classes': total_classes,
        'attended_classes': attended_classes,
        'adjustment_count': adjustment_count,
        'adjusted_total': adjusted_total,
        'adjusted_attended': adjusted_attended,
        'attendance_percentage': round(percentage, 2),
    }


def root_view(request):
    """Always start at login; authenticated users continue to their dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


# ===== AUTHENTICATION VIEWS =====

def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'attendance/login.html')


@login_required(login_url='login')
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


# ===== DASHBOARD VIEWS =====

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard that redirects to role-specific dashboard."""
    if is_admin(request.user):
        return admin_dashboard(request)
    elif is_staff_user(request.user):
        return staff_dashboard(request)
    elif is_student_user(request.user):
        return student_dashboard(request)
    else:
        messages.error(request, "Your account is not properly configured.")
        logout(request)
        return redirect('login')


@login_required(login_url='login')
@admin_required
def admin_dashboard(request):
    """Admin dashboard with overview statistics."""
    context = {
        'total_students': Student.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_schedules': DaySchedule.objects.count(),
        'today_attendance': Attendance.objects.filter(
            date=timezone.now().date()
        ).count(),
        'students_below_75': get_students_below_75_percent(),
        'students_absent_4_days': get_students_absent_4_days(),
        'notifications': Notification.objects.filter(user=request.user).order_by('-created_at')[:5],
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'attendance/admin_dashboard.html', context)


@login_required(login_url='login')
@staff_required
def staff_dashboard(request):
    """Staff dashboard with relevant statistics."""
    if is_admin(request.user):
        return redirect('admin_dashboard')

    try:
        staff = request.user.staff_profile
    except:
        messages.error(request, "Staff profile not found.")
        logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    
    today_schedules = DaySchedule.objects.filter(staff=staff, date=today)
    
    # Get attendance marked by this staff today
    marked_today = Attendance.objects.filter(
        staff=staff,
        date=today
    ).count()
    
    context = {
        'staff': staff,
        'today_classes': today_schedules.count(),
        'attendance_marked': marked_today,
        'pending_attendance': max(
            0,
            sum(
                Student.objects.filter(
                    department=schedule.department,
                    semester=schedule.semester
                ).count()
                for schedule in today_schedules
            ) - marked_today
        ),
        'students_below_75': get_students_below_75_percent(),
        'notifications': Notification.objects.filter(user=request.user).order_by('-created_at')[:5],
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'attendance/staff_dashboard.html', context)


@login_required(login_url='login')
@student_required
def student_dashboard(request):
    """Student dashboard with attendance info."""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, "Student profile not found.")
        logout(request)
        return redirect('login')
    
    today = timezone.now().date()
    
    stats = get_attendance_stats(student)
    
    # Get today's attendance
    today_attendance = Attendance.objects.filter(
        student=student,
        date=today
    )
    
    context = {
        'student': student,
        **stats,
        'today_attendance': today_attendance,
        'notifications': Notification.objects.filter(user=request.user).order_by('-created_at')[:5],
        'unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
    }
    return render(request, 'attendance/student_dashboard.html', context)


# ===== STUDENT MANAGEMENT VIEWS =====

@login_required(login_url='login')
@staff_required
def student_list(request):
    """List all students."""
    students = Student.objects.all().order_by('name')
    context = {'students': students}
    return render(request, 'attendance/student_list.html', context)


@login_required(login_url='login')
@staff_required
def add_student(request):
    """Add a new student login (Staff/Admin)."""
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        department = request.POST.get('department')
        semester = request.POST.get('semester')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate inputs
        if not all([name, roll_number, department, semester, username, password]):
            messages.error(request, "All fields are required.")
            return render(request, 'attendance/add_student.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'attendance/add_student.html')
        
        if Student.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "Roll number already exists.")
            return render(request, 'attendance/add_student.html')
        
        try:
            # Create User
            user = User.objects.create_user(
                username=username,
                first_name=name,
                password=password
            )
            
            # Create Student
            student = Student.objects.create(
                user=user,
                name=name,
                roll_number=roll_number,
                department=department,
                semester=semester
            )
            
            messages.success(request, f"Student {student.name} added successfully!")
            return redirect('student_list')
        except Exception as e:
            messages.error(request, f"Error adding student: {str(e)}")
    
    return render(request, 'attendance/add_student.html')


@login_required(login_url='login')
@staff_required
def edit_student(request, student_id):
    """Edit student information (Admin only)."""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        department = request.POST.get('department')
        semester = request.POST.get('semester')
        
        if not all([name, roll_number, department, semester]):
            messages.error(request, "All fields are required.")
            return render(request, 'attendance/edit_student.html', {'student': student})
        
        student.name = name
        student.roll_number = roll_number
        student.department = department
        student.semester = semester
        student.save()
        
        messages.success(request, f"Student {student.name} updated successfully!")
        return redirect('student_list')
    
    return render(request, 'attendance/edit_student.html', {'student': student})


@login_required(login_url='login')
@staff_required
def change_student_password(request, student_id):
    """Staff and admin can reset a student password."""
    student = get_object_or_404(Student, id=student_id)
    form = PasswordChangeByRoleForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        student.user.set_password(form.cleaned_data['password'])
        student.user.save()
        messages.success(request, f"Password changed for {student.name}.")
        return redirect('student_list')

    return render(request, 'attendance/change_password.html', {
        'form': form,
        'target_name': student.name,
        'back_url': 'student_list',
    })


@login_required(login_url='login')
@admin_required
def delete_student(request, student_id):
    """Delete a student (Admin only)."""
    student = get_object_or_404(Student, id=student_id)
    student_name = student.name
    user = student.user
    
    student.delete()
    user.delete()
    
    messages.success(request, f"Student {student_name} deleted successfully!")
    return redirect('student_list')


# ===== STAFF MANAGEMENT VIEWS =====

@login_required(login_url='login')
@admin_required
def staff_list(request):
    """List all staff members."""
    staff_members = Staff.objects.prefetch_related('subject_assignments__subject').order_by('name')
    return render(request, 'attendance/staff_list.html', {'staff_members': staff_members})


def save_staff_assignments(staff, request):
    """Replace staff subject assignments from repeated form rows."""
    subject_ids = request.POST.getlist('assignment_subject')
    departments = request.POST.getlist('assignment_department')
    semesters = request.POST.getlist('assignment_semester')

    staff.subject_assignments.all().delete()
    for subject_id, department, semester in zip(subject_ids, departments, semesters):
        if not all([subject_id, department, semester]):
            continue
        try:
            semester_value = int(semester)
        except ValueError:
            continue
        StaffSubjectAssignment.objects.get_or_create(
            staff=staff,
            subject_id=subject_id,
            department=department.strip(),
            semester=semester_value
        )


@login_required(login_url='login')
@admin_required
def add_staff(request):
    """Admin can add staff and assign handled subjects."""
    subjects = Subject.objects.all().order_by('semester', 'subject_name')
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        designation = request.POST.get('designation') or 'Teacher'
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not all([name, department, username, password]):
            messages.error(request, "Name, department, username, and password are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(username=username, first_name=name, password=password)
            staff = Staff.objects.create(
                user=user,
                name=name,
                department=department,
                designation=designation
            )
            save_staff_assignments(staff, request)
            messages.success(request, f"Staff {staff.name} added successfully.")
            return redirect('staff_list')

    return render(request, 'attendance/add_staff.html', {
        'subjects': subjects,
        'assignment_rows': range(4),
    })


@login_required(login_url='login')
@admin_required
def edit_staff(request, staff_id):
    """Admin can update staff profile and handled subjects."""
    staff = get_object_or_404(Staff, id=staff_id)
    subjects = Subject.objects.all().order_by('semester', 'subject_name')

    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        designation = request.POST.get('designation') or 'Teacher'

        if not all([name, department]):
            messages.error(request, "Name and department are required.")
        else:
            staff.name = name
            staff.department = department
            staff.designation = designation
            staff.user.first_name = name
            staff.user.save()
            staff.save()
            save_staff_assignments(staff, request)
            messages.success(request, f"Staff {staff.name} updated successfully.")
            return redirect('staff_list')

    assignments = list(staff.subject_assignments.select_related('subject'))
    while len(assignments) < 4:
        assignments.append(None)
    return render(request, 'attendance/edit_staff.html', {
        'staff': staff,
        'subjects': subjects,
        'assignments': assignments,
    })


@login_required(login_url='login')
@admin_required
def change_staff_password(request, staff_id):
    """Admin can reset staff passwords."""
    staff = get_object_or_404(Staff, id=staff_id)
    form = PasswordChangeByRoleForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        staff.user.set_password(form.cleaned_data['password'])
        staff.user.save()
        messages.success(request, f"Password changed for {staff.name}.")
        return redirect('staff_list')

    return render(request, 'attendance/change_password.html', {
        'form': form,
        'target_name': staff.name,
        'back_url': 'staff_list',
    })


# ===== SCHEDULE VIEWS =====

@login_required(login_url='login')
@admin_required
def day_schedule(request):
    """Admin creates class-wise period schedules for each day."""
    subjects = Subject.objects.all().order_by('semester', 'subject_name')
    staff_members = Staff.objects.all().order_by('name')
    schedules = DaySchedule.objects.select_related('subject', 'staff').order_by('-date', 'department', 'semester', 'period')

    if request.method == 'POST':
        schedule_date = request.POST.get('date')
        department = request.POST.get('department')
        semester = request.POST.get('semester')
        period = request.POST.get('period')
        subject_id = request.POST.get('subject')
        staff_id = request.POST.get('staff')

        if not all([schedule_date, department, semester, period, subject_id, staff_id]):
            messages.error(request, "All schedule fields are required.")
        else:
            subject = get_object_or_404(Subject, id=subject_id)
            staff = get_object_or_404(Staff, id=staff_id)
            if not StaffSubjectAssignment.objects.filter(
                staff=staff,
                subject=subject,
                department=department,
                semester=semester
            ).exists():
                messages.error(request, "Selected staff is not assigned to this subject/class.")
            else:
                DaySchedule.objects.update_or_create(
                    date=schedule_date,
                    department=department,
                    semester=semester,
                    period=period,
                    defaults={'subject': subject, 'staff': staff}
                )
                messages.success(request, "Day schedule saved.")
                return redirect('day_schedule')

    return render(request, 'attendance/day_schedule.html', {
        'subjects': subjects,
        'staff_members': staff_members,
        'schedules': schedules[:50],
        'period_choices': Period.PERIOD_CHOICES,
    })


@login_required(login_url='login')
@admin_required
def delete_day_schedule(request, schedule_id):
    """Admin can remove a scheduled period."""
    schedule = get_object_or_404(DaySchedule, id=schedule_id)
    schedule.delete()
    messages.success(request, "Scheduled period deleted.")
    return redirect('day_schedule')


# ===== ATTENDANCE VIEWS =====

@login_required(login_url='login')
@staff_required
def mark_attendance(request):
    """Mark attendance from an admin-created date/class/period schedule."""
    selected_date = request.GET.get('date') or request.POST.get('date') or timezone.localdate().isoformat()
    selected_class = request.GET.get('class') or request.POST.get('class')
    selected_schedule_id = request.GET.get('schedule') or request.POST.get('schedule')
    schedule_query = DaySchedule.objects.select_related('subject', 'staff')

    if not is_admin(request.user):
        staff_profile = getattr(request.user, 'staff_profile', None)
        schedule_query = schedule_query.filter(staff=staff_profile)

    if selected_date:
        schedule_query = schedule_query.filter(date=selected_date)

    class_rows = DaySchedule.objects.filter(date=selected_date).values('department', 'semester').distinct().order_by('department', 'semester')
    if not is_admin(request.user):
        class_rows = class_rows.filter(staff=getattr(request.user, 'staff_profile', None))
    class_options = [
        {
            'department': row['department'],
            'semester': row['semester'],
            'value': f"{row['department']}-{row['semester']}",
        }
        for row in class_rows
    ]

    schedules = schedule_query
    selected_department = None
    selected_semester = None
    if selected_class and '-' in selected_class:
        selected_department, selected_semester = selected_class.rsplit('-', 1)
        schedules = schedules.filter(department=selected_department, semester=selected_semester)

    selected_schedule = None
    students = Student.objects.none()
    if selected_schedule_id:
        selected_schedule = get_object_or_404(schedules, id=selected_schedule_id)
        students = Student.objects.filter(
            department=selected_schedule.department,
            semester=selected_schedule.semester
        ).order_by('name')
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        status = request.POST.get('status')
        
        if not all([selected_schedule_id, student_id, status]):
            messages.error(request, "Select date, class, period, student, and status.")
        else:
            try:
                selected_schedule = get_object_or_404(schedules, id=selected_schedule_id)
                student = Student.objects.get(
                    id=student_id,
                    department=selected_schedule.department,
                    semester=selected_schedule.semester
                )
                
                attendance_date = selected_schedule.date
                existing = Attendance.objects.filter(
                    student=student,
                    subject=selected_schedule.subject,
                    date=attendance_date,
                    period=selected_schedule.period
                ).first()

                if existing and not is_admin(request.user):
                    elapsed_working_days = working_days_between(existing.date, timezone.localdate())
                    if elapsed_working_days > 7:
                        messages.error(request, "Staff can change attendance only within 7 working days. Contact admin.")
                        return redirect('attendance_report')

                attendance, created = Attendance.objects.update_or_create(
                    student=student,
                    subject=selected_schedule.subject,
                    date=attendance_date,
                    period=selected_schedule.period,
                    defaults={
                        'status': status,
                        'staff': selected_schedule.staff,
                        'changed_by': request.user if existing else None,
                        'changed_at': timezone.now() if existing else None,
                    }
                )
                
                action = "created" if created else "updated"
                messages.success(request, f"Attendance {action} successfully!")
                
                # Create notification
                if created:
                    Notification.objects.create(
                        user=selected_schedule.staff.user,
                        title="Attendance Marked",
                        message=f"Attendance marked for {student.name} - {selected_schedule.period}",
                        notification_type='attendance_marked'
                    )
            except Exception as e:
                messages.error(request, f"Error marking attendance: {str(e)}")
    
    context = {
        'class_options': class_options,
        'schedules': schedules,
        'selected_date': selected_date,
        'selected_class': selected_class,
        'selected_schedule_id': selected_schedule_id,
        'selected_schedule': selected_schedule,
        'students': students,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required(login_url='login')
@admin_required
def edit_attendance(request, attendance_id):
    """Admin/super admin can change any attendance record with an opinion."""
    attendance = get_object_or_404(Attendance, id=attendance_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        opinion = request.POST.get('opinion', '').strip()

        if status not in dict(Attendance.STATUS):
            messages.error(request, "Invalid attendance status.")
        elif not opinion:
            messages.error(request, "Opinion is required when admin changes attendance.")
        else:
            attendance.status = status
            attendance.change_opinion = opinion
            attendance.changed_by = request.user
            attendance.changed_at = timezone.now()
            attendance.save()
            messages.success(request, "Attendance changed with admin opinion.")
            return redirect('attendance_report')

    return render(request, 'attendance/edit_attendance.html', {'attendance': attendance})


@login_required(login_url='login')
@admin_required
def add_attendance_adjustment(request):
    """Grant extra attendance count to a student with an admin opinion."""
    if request.method != 'POST':
        return redirect('attendance_report')

    student_id = request.POST.get('student')
    attendance_count = request.POST.get('attendance_count')
    opinion = request.POST.get('opinion', '').strip()

    if not all([student_id, attendance_count, opinion]):
        messages.error(request, "Student, attendance count, and opinion are required.")
        return redirect('attendance_report')

    try:
        count = int(attendance_count)
    except ValueError:
        messages.error(request, "Attendance count must be a number.")
        return redirect('attendance_report')

    if count <= 0:
        messages.error(request, "Attendance count must be greater than zero.")
        return redirect('attendance_report')

    student = get_object_or_404(Student, id=student_id)
    AttendanceAdjustment.objects.create(
        student=student,
        attendance_count=count,
        opinion=opinion,
        created_by=request.user
    )
    messages.success(request, f"{count} attendance credit(s) added for {student.name}.")
    return redirect('attendance_report')


@login_required(login_url='login')
def attendance_report(request):
    """View attendance report based on role."""
    if is_admin(request.user) or is_staff_user(request.user):
        attendance = Attendance.objects.all().order_by('-date', '-period')
        if is_staff_user(request.user) and not is_admin(request.user):
            attendance = attendance.filter(staff=request.user.staff_profile)
        selected_date = request.GET.get('date')
        if selected_date:
            attendance = attendance.filter(date=selected_date)
        students = Student.objects.all().order_by('name')
        adjustments = AttendanceAdjustment.objects.select_related('student', 'created_by')[:20]
    elif is_student_user(request.user):
        # Show only this student's attendance
        try:
            student = request.user.student_profile
            attendance = Attendance.objects.filter(student=student).order_by('-date', '-period')
            selected_date = request.GET.get('date')
            if selected_date:
                attendance = attendance.filter(date=selected_date)
            students = []
            adjustments = AttendanceAdjustment.objects.filter(student=student).select_related('created_by')[:20]
        except:
            messages.error(request, "Student profile not found.")
            return redirect('login')
    else:
        return redirect('login')
    
    context = {
        'attendance': attendance,
        'students': students,
        'adjustments': adjustments,
    }
    return render(request, 'attendance/attendance_report.html', context)


@login_required(login_url='login')
@student_required
def attendance_percentage(request):
    """View attendance percentage for student."""
    try:
        student = request.user.student_profile
    except:
        messages.error(request, "Student profile not found.")
        return redirect('login')
    
    stats = get_attendance_stats(student)
    
    # Get subject-wise attendance
    subject_rows = Attendance.objects.filter(
        student=student
    ).values('subject__subject_name').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='Present'))
    )
    subject_attendance = []
    for row in subject_rows:
        total = row['total']
        present = row['present']
        row['percentage'] = round((present / total * 100), 2) if total else 0
        subject_attendance.append(row)

    selected_day = request.GET.get('day')
    day_attendance = None
    if selected_day:
        try:
            selected_date = datetime.strptime(selected_day, '%Y-%m-%d').date()
            day_attendance = Attendance.objects.filter(
                student=student,
                date=selected_date
            ).order_by('period')
        except ValueError:
            selected_day = None

    weeks = OrderedDict()
    records = Attendance.objects.filter(student=student).order_by('-date', 'period')
    for record in records:
        week_start = record.date - timedelta(days=record.date.weekday())
        week_end = week_start + timedelta(days=6)
        key = week_start.isoformat()
        if key not in weeks:
            weeks[key] = {
                'start': week_start,
                'end': week_end,
                'days': OrderedDict(),
            }
        day_key = record.date.isoformat()
        if day_key not in weeks[key]['days']:
            weeks[key]['days'][day_key] = {
                'date': record.date,
                'total': 0,
                'present': 0,
            }
        weeks[key]['days'][day_key]['total'] += 1
        if record.status == 'Present':
            weeks[key]['days'][day_key]['present'] += 1
    
    context = {
        'student': student,
        **stats,
        'subject_attendance': subject_attendance,
        'weeks': weeks.values(),
        'selected_day': selected_day,
        'day_attendance': day_attendance,
        'adjustments': AttendanceAdjustment.objects.filter(student=student),
    }
    return render(request, 'attendance/attendance_percentage.html', context)


# ===== NOTIFICATION VIEWS =====

@login_required(login_url='login')
def notifications(request):
    """View all notifications for user."""
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    context = {'notifications': user_notifications}
    return render(request, 'attendance/notifications.html', context)


# ===== HELPER FUNCTIONS =====

def get_students_below_75_percent():
    """Get list of students with attendance below 75%."""
    students_below_75 = []
    
    for student in Student.objects.all():
        total_classes = Attendance.objects.filter(student=student).count()
        attended_classes = Attendance.objects.filter(
            student=student,
            status='Present'
        ).count()
        
        if total_classes > 0:
            percentage = (attended_classes / total_classes) * 100
            if percentage < 75:
                students_below_75.append({
                    'student': student,
                    'percentage': round(percentage, 2)
                })
    
    return students_below_75


def get_students_absent_4_days():
    """Get list of students absent for 4 consecutive working days."""
    # This is a simplified version - can be enhanced based on working days definition
    students_absent = []
    
    for student in Student.objects.all():
        # Get last 4 days of attendance
        last_4_days = Attendance.objects.filter(
            student=student
        ).order_by('-date')[:4]
        
        if last_4_days.count() == 4:
            all_absent = all(att.status == 'Absent' for att in last_4_days)
            if all_absent:
                students_absent.append(student)
    
    return students_absent
