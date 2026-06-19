# 🎓 Attendance Management System

A comprehensive Django-based attendance management system with role-based access control for Admin, Staff, and Students.

## ✨ Features

### 👑 Admin Features
- Dashboard with system overview
- Total Students, Staff, and Subjects count
- Today's Attendance statistics
- Students with attendance below 75%
- Students absent for 4 consecutive days
- Add/Edit/Delete Students
- Add/Edit/Delete Staff
- Create student and staff credentials
- Mark and edit attendance (anytime)
- View comprehensive attendance reports
- Notification management
- Access to Django Admin Panel

### 👨‍🏫 Staff/Teacher Features
- Dashboard with class and attendance statistics
- Add/Edit/Delete Students
- Create Student credentials and passwords
- Mark attendance for classes
- Edit attendance (within 7 working days)
- View attendance reports
- Track students below 75% attendance
- Receive and view notifications
- See pending attendance tasks

### 👨‍🎓 Student Features
- Dashboard with attendance overview
- View personal attendance percentage
- View attendance by subject
- See today's attendance status
- View attendance reports
- Receive notifications
  - Attendance below 75% alerts
  - Absent for 3 consecutive classes
  - Absent for 4 consecutive working days
- Change password

## 🗄️ Database Schema

### Student Table
- id
- name
- roll_number (unique)
- department
- semester
- user_id (OneToOne with User)

### Staff Table
- id
- name
- department
- designation
- user_id (OneToOne with User)

### Subject Table
- id
- subject_name
- subject_code
- semester

### Period Table
- id
- period_code (P1-P8)
- start_time
- end_time

### Attendance Table
- id
- student_id (ForeignKey)
- subject_id (ForeignKey)
- staff_id (ForeignKey)
- date
- period
- status (Present/Absent)
- created_at
- updated_at

### Notification Table
- id
- user_id (ForeignKey)
- title
- message
- notification_type
- is_read
- created_at

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 6.0.5
- SQLite (default)

### Installation

1. **Navigate to project directory:**
```bash
cd C:\Users\Hakesh\myenv\attendance_system_v1
```

2. **Activate virtual environment:**
```bash
.\Scripts\Activate.ps1
```

3. **Set DEBUG environment variable:**
```bash
$env:DEBUG = 'True'
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create superuser (Admin):**
```bash
python manage.py createsuperuser
```

6. **Start development server:**
```bash
python manage.py runserver
```

7. **Access the application:**
- Main URL: `http://localhost:8000/login/`
- Admin Panel: `http://localhost:8000/admin/`

## 🔐 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

## 📋 URL Routes

| URL | View | Role |
|-----|------|------|
| `/login/` | login_view | Public |
| `/logout/` | logout_view | Authenticated |
| `/dashboard/` | dashboard | Authenticated |
| `/admin/dashboard/` | admin_dashboard | Admin |
| `/staff/dashboard/` | staff_dashboard | Staff |
| `/student/dashboard/` | student_dashboard | Student |
| `/student-list/` | student_list | Staff/Admin |
| `/add-student/` | add_student | Admin |
| `/edit-student/<id>/` | edit_student | Admin |
| `/delete-student/<id>/` | delete_student | Admin |
| `/mark-attendance/` | mark_attendance | Staff/Admin |
| `/attendance-report/` | attendance_report | Authenticated |
| `/attendance-percentage/` | attendance_percentage | Student |
| `/notifications/` | notifications | Authenticated |

## 📊 Dashboard Cards

### Admin Dashboard
- **Total Students** - Count of all registered students
- **Total Staff** - Count of all registered staff
- **Total Subjects** - Count of all subjects
- **Today's Attendance** - Attendance records marked today
- **Students Below 75%** - List with percentages
- **Students Absent 4 Days** - List of students
- **Notifications** - Recent system notifications
- **Unread Notifications** - Count of unread alerts

### Staff Dashboard
- **Today's Classes** - Number of classes scheduled
- **Attendance Marked** - Records marked today
- **Pending Attendance** - Not yet marked records
- **Students Below 75%** - Alert list
- **Notifications** - Recent notifications
- **Unread Notifications** - Count

### Student Dashboard
- **Attendance Percentage** - Overall attendance %
- **Total Classes** - Total classes attended
- **Attended Classes** - Number of present marks
- **Today's Attendance** - Today's status
- **Notifications** - Recent alerts
- **Unread Notifications** - Count

## 🔔 Notification System

### Notification Types

1. **✅ Attendance Marked Successfully**
   - Visible to: Staff/Admin
   - Triggered: When attendance is marked
   
2. **⚠️ Student Absent for 3 Consecutive Classes**
   - Visible to: Student, Staff, Admin
   - Triggered: Automatically detected
   
3. **🚨 Student Absent for 4 Consecutive Working Days**
   - Visible to: Student, Staff, Admin
   - Triggered: Automatically detected
   
4. **⚠️ Attendance Below 75%**
   - Visible to: Student (highlighted for Staff/Admin)
   - Triggered: When attendance drops below 75%

## 🔒 Security Features

- ✅ Login required for all pages
- ✅ Role-based access control (RBAC)
- ✅ Staff can only edit attendance within 7 working days
- ✅ Admin can edit attendance anytime
- ✅ CSRF protection on all forms
- ✅ Secure password hashing
- ✅ Session management
- ✅ Unique constraints on roll numbers

## 🎨 UI/UX Features

- **Responsive Design** - Works on desktop and mobile
- **Bootstrap 5** - Modern, clean interface
- **Font Awesome Icons** - Intuitive icons
- **Dark Navigation** - Professional navbar
- **Sidebar Navigation** - Quick access to features
- **Color-coded Alerts** - Success, warning, error messages
- **Stat Cards** - Visual data representation
- **Data Tables** - Sortable and filterable
- **Form Validation** - Client and server-side

## 📁 Project Structure

```
attendance_system_v1/
├── attendance/
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   └── attendance/
│   │       ├── login.html
│   │       ├── admin_dashboard.html
│   │       ├── staff_dashboard.html
│   │       ├── student_dashboard.html
│   │       ├── student_list.html
│   │       ├── add_student.html
│   │       ├── edit_student.html
│   │       ├── mark_attendance.html
│   │       ├── attendance_report.html
│   │       ├── attendance_percentage.html
│   │       └── notifications.html
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── attendance_system/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── static/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

## 🛠️ Tech Stack

- **Backend**: Django 6.0.5
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Icons**: Font Awesome 6.4
- **Python Version**: 3.13+

## 📝 Development Notes

### To Add a New User via Admin Panel:

1. Go to `http://localhost:8000/admin/`
2. Login with admin credentials
3. Navigate to Users
4. Create a new user with username and password
5. Assign a Staff or Student profile to the user

### To Mark Attendance:

1. Login as Staff/Admin
2. Go to "Mark Attendance"
3. Select Student, Subject, Date, Period, and Status
4. Click Mark
5. Student will receive notification

### To View Reports:

- **Admin/Staff**: See all students' attendance
- **Student**: See only their own attendance

## 🔧 Customization

### Modify Periods:
Edit the Period model in `models.py`:
```python
PERIOD_CHOICES = (
    ("P1", "Period 1 (9:00-10:00)"),
    # Add more periods
)
```

### Change Attendance Threshold:
In `views.py`, modify the `get_students_below_75_percent()` function:
```python
if percentage < 75:  # Change this value
```

### Add Custom Notifications:
Update the `NOTIFICATION_TYPES` in the Notification model.

## 📞 Support

For issues or questions:
1. Check Django logs: `python manage.py runserver --verbosity 2`
2. Verify database migrations: `python manage.py migrate --plan`
3. Check admin panel for data integrity
4. Review error messages in browser console

## 📜 License

This project is provided as-is for educational purposes.

## 🎯 Future Enhancements

- [ ] Email notifications
- [ ] SMS alerts for low attendance
- [ ] Bulk attendance import/export (CSV)
- [ ] API for mobile app
- [ ] Advanced analytics and reports
- [ ] QR code attendance
- [ ] Biometric integration
- [ ] Parent notifications
- [ ] Holiday management
- [ ] Leave management

---

**Created**: June 12, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready
