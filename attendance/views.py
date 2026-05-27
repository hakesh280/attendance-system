from django.shortcuts import render, redirect
from .models import Student
from .models import Attendance
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'attendance/index.html')


def add_student(request):
    if request.method == "POST":
        name = request.POST.get('name')
        usn = request.POST.get('usn')
        department = request.POST.get('department')
        semester = request.POST.get('semester')

        Student.objects.create(
            name=name,
            usn=usn,
            department=department,
            semester=semester,
        )

    return render(request, 'attendance/add_student.html')
def mark_attendance(request):

    students = Student.objects.all()

    if request.method == "POST":

        student_id = request.POST.get('student')

        date = request.POST.get('date')

        status = request.POST.get('status')

        student = Student.objects.get(id=student_id)

        Attendance.objects.create(
            student=student,
            date=date,
            status=status
        )

    return render(request, 'attendance/mark_attendance.html', {
        'students': students
    })
def attendance_report(request):

    attendance_data = Attendance.objects.all()

    return render(request, 'attendance/attendance_report.html', {
        'attendance_data': attendance_data
    })
def attendance_percentage(request):

    students = Student.objects.all()

    data = []

    for student in students:

        total = Attendance.objects.filter(student=student).count()

        present = Attendance.objects.filter(
            student=student,
            status='Present'
        ).count()

        if total > 0:
            percentage = (present / total) * 100
        else:
            percentage = 0

        data.append({
            'name': student.name,
            'percentage': round(percentage, 2)
        })

    return render(request, 'attendance/attendance_percentage.html', {
        'data': data
    })
@login_required(login_url='/login/')
def dashboard(request):

    total_students = Student.objects.count()

    total_attendance = Attendance.objects.count()

    present_count = Attendance.objects.filter(
        status='Present'
    ).count()

    absent_count = Attendance.objects.filter(
        status='Absent'
    ).count()

    return render(request, 'attendance/dashboard.html', {

        'total_students': total_students,

        'total_attendance': total_attendance,

        'present_count': present_count,

        'absent_count': absent_count

    })
def student_list(request):

    query = request.GET.get('q')

    if query:

        students = Student.objects.filter(
            name__icontains=query
        )

    else:

        students = Student.objects.all()

    return render(request,
                  'attendance/student_list.html',
                  {
                      'students': students
                  })


def delete_student(request, id):

    student = Student.objects.get(id=id)

    student.delete()

    return redirect('/student-list/')
def edit_student(request, id):

    student = Student.objects.get(id=id)

    if request.method == "POST":

        student.name = request.POST.get('name')

        student.usn = request.POST.get('usn')

        student.department = request.POST.get('department')

        student.semester = request.POST.get('semester')

        student.save()

        return redirect('/student-list/')

    return render(request, 'attendance/edit_student.html', {
        'student': student
    })
def login_page(request):

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/dashboard/')

        else:

            return render(request,
                          'attendance/login.html',
                          {'error': 'Invalid Username or Password'})

    return render(request, 'attendance/login.html')