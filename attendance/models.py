from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    """Student model representing a student user."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    roll_number = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    department = models.CharField(
        max_length=100
    )

    semester = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
    
class Staff(models.Model):
    """Staff model representing a teacher/staff user."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )

    name = models.CharField(
        max_length=100
    )

    department = models.CharField(
        max_length=100
    )

    designation = models.CharField(
        max_length=100,
        default="Teacher"
    )

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    """Subject model for courses/subjects."""
    subject_name = models.CharField(
        max_length=100
    )

    subject_code = models.CharField(
        max_length=20
    )

    semester = models.IntegerField()

    def __str__(self):
        return self.subject_name


class StaffSubjectAssignment(models.Model):
    """Subject ownership by staff for a department and semester."""
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='staff_assignments'
    )
    department = models.CharField(max_length=100)
    semester = models.IntegerField()

    class Meta:
        unique_together = ('staff', 'subject', 'department', 'semester')
        ordering = ['department', 'semester', 'subject__subject_name']

    def __str__(self):
        return f"{self.staff.name} - {self.subject.subject_name} ({self.department} Sem {self.semester})"


class Period(models.Model):
    """Period model representing class periods."""
    PERIOD_CHOICES = (
        ("P1", "Period 1 (9:00-10:00)"),
        ("P2", "Period 2 (10:00-11:00)"),
        ("P3", "Period 3 (11:00-12:00)"),
        ("P4", "Period 4 (12:00-1:00)"),
        ("P5", "Period 5 (1:30-2:30)"),
        ("P6", "Period 6 (2:30-3:30)"),
        ("P7", "Period 7 (3:30-4:30)"),
        ("P8", "Period 8 (4:30-5:30)"),
    )

    period_code = models.CharField(
        max_length=2,
        choices=PERIOD_CHOICES,
        unique=True
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.get_period_code_display()


class DaySchedule(models.Model):
    """Admin-created class/period schedule for a day."""
    date = models.DateField()
    department = models.CharField(max_length=100)
    semester = models.IntegerField()
    period = models.CharField(
        max_length=2,
        choices=Period.PERIOD_CHOICES
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='day_schedules'
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='day_schedules'
    )

    class Meta:
        unique_together = ('date', 'department', 'semester', 'period')
        ordering = ['date', 'department', 'semester', 'period']

    def __str__(self):
        return f"{self.date} - {self.department} Sem {self.semester} {self.period}"
    
class Attendance(models.Model):
    """Attendance model for tracking student attendance."""
    STATUS = (
        ("Present", "Present"),
        ("Absent", "Absent"),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='attendance_marked'
    )

    date = models.DateField()

    period = models.CharField(
        max_length=2,
        choices=(
            ("P1", "Period 1"),
            ("P2", "Period 2"),
            ("P3", "Period 3"),
            ("P4", "Period 4"),
            ("P5", "Period 5"),
            ("P6", "Period 6"),
            ("P7", "Period 7"),
            ("P8", "Period 8"),
        )
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    change_opinion = models.TextField(
        blank=True
    )

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_changes'
    )

    changed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('student', 'subject', 'date', 'period')
        ordering = ['-date', '-period']

    def __str__(self):
        return f"{self.student.name} - {self.date} ({self.period})"


class AttendanceAdjustment(models.Model):
    """Admin-approved extra attendance credits for special cases."""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_adjustments'
    )

    attendance_count = models.PositiveIntegerField()

    opinion = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendance_adjustments_created'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} +{self.attendance_count}"
    
class Notification(models.Model):
    """Notification model for system notifications."""
    NOTIFICATION_TYPES = (
        ('attendance_marked', 'Attendance Marked'),
        ('absent_3_days', 'Absent for 3 Consecutive Classes'),
        ('absent_4_days', 'Absent for 4 Consecutive Working Days'),
        ('low_attendance', 'Attendance Below 75%'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(
        max_length=100
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='other'
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
