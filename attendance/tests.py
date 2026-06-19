from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DaySchedule, Staff, StaffSubjectAssignment, Student, Subject


class RouteSmokeTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='pass12345',
            email='admin@example.com',
            first_name='Admin',
        )
        self.staff_user = User.objects.create_user(
            username='staff_user',
            password='pass12345',
            first_name='Staff',
        )
        self.student_user = User.objects.create_user(
            username='student_user',
            password='pass12345',
            first_name='Student',
        )

        self.staff = Staff.objects.create(
            user=self.staff_user,
            name='Staff User',
            department='CSE',
            designation='Teacher',
        )
        self.student = Student.objects.create(
            user=self.student_user,
            name='Student User',
            roll_number='CSE001',
            department='CSE',
            semester=1,
        )
        self.subject = Subject.objects.create(
            subject_name='Programming',
            subject_code='CSE101',
            semester=1,
        )
        StaffSubjectAssignment.objects.create(
            staff=self.staff,
            subject=self.subject,
            department='CSE',
            semester=1,
        )
        DaySchedule.objects.create(
            date=timezone.localdate(),
            department='CSE',
            semester=1,
            period='P1',
            subject=self.subject,
            staff=self.staff,
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_admin_main_pages_render(self):
        self.client.login(username='admin_user', password='pass12345')

        for url_name in [
            'dashboard',
            'admin_dashboard',
            'student_list',
            'staff_list',
            'day_schedule',
            'mark_attendance',
            'attendance_report',
            'notifications',
        ]:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_admin_staff_dashboard_redirects_without_logout(self):
        self.client.login(username='admin_user', password='pass12345')

        response = self.client.get(reverse('staff_dashboard'))

        self.assertRedirects(response, reverse('admin_dashboard'))
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_staff_main_pages_render(self):
        self.client.login(username='staff_user', password='pass12345')

        for url_name in [
            'dashboard',
            'staff_dashboard',
            'student_list',
            'mark_attendance',
            'attendance_report',
            'notifications',
        ]:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_staff_cannot_view_student_percentage(self):
        self.client.login(username='staff_user', password='pass12345')

        response = self.client.get(reverse('attendance_percentage'))

        self.assertRedirects(response, reverse('dashboard'))

    def test_student_main_pages_render(self):
        self.client.login(username='student_user', password='pass12345')

        for url_name in [
            'dashboard',
            'student_dashboard',
            'attendance_report',
            'attendance_percentage',
            'notifications',
        ]:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
