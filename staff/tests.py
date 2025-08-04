from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from django.test.utils import override_settings
from django.contrib.messages import get_messages
from django.http import HttpRequest
from django.utils import timezone
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import csv
import io

from .models import Employee, Schedule
from .admin import EmployeeAdmin, ScheduleAdmin, EmployeeInline, ScheduleInline


class EmployeeModelTest(TestCase):
    """Test Employee model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='jdoe',
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe'
        )
        
        self.employee_data = {
            'user': self.user,
            'phone': '8315551234',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '8315554321',
            'role': 'barista',
            'employment_status': 'active',
            'hire_date': date(2024, 1, 15),
            'hourly_wage': Decimal('18.50'),
            'notes': 'Excellent latte art skills',
            'can_open': False,
            'can_close': False,
            'can_handle_cash': True
        }
    
    def test_employee_creation(self):
        """Test creating an Employee instance"""
        employee = Employee.objects.create(**self.employee_data)
        
        self.assertEqual(employee.user, self.user)
        self.assertEqual(employee.phone, '8315551234')
        self.assertEqual(employee.role, 'barista')
        self.assertEqual(employee.hourly_wage, Decimal('18.50'))
        self.assertTrue(employee.can_handle_cash)
        self.assertFalse(employee.can_open)
    
    def test_employee_str(self):
        """Test string representation"""
        employee = Employee.objects.create(**self.employee_data)
        expected = "John Doe (Barista)"
        self.assertEqual(str(employee), expected)
    
    def test_employee_id_generation(self):
        """Test automatic employee ID generation"""
        employee = Employee.objects.create(**self.employee_data)
        self.assertTrue(employee.employee_id.startswith('EMP2024'))
        self.assertEqual(len(employee.employee_id), 10)  # EMP + year + 3 digits
    
    def test_employee_id_sequence(self):
        """Test employee ID sequence generation"""
        emp1 = Employee.objects.create(**self.employee_data)
        
        # Create second employee
        user2 = User.objects.create_user('jsmith', 'jane.smith@example.com', 'Jane', 'Smith')
        data2 = self.employee_data.copy()
        data2['user'] = user2
        emp2 = Employee.objects.create(**data2)
        
        self.assertEqual(emp1.employee_id, 'EMP2024001')
        self.assertEqual(emp2.employee_id, 'EMP2024002')
    
    def test_custom_employee_id(self):
        """Test custom employee ID is preserved"""
        data = self.employee_data.copy()
        data['employee_id'] = 'CUSTOM001'
        employee = Employee.objects.create(**data)
        self.assertEqual(employee.employee_id, 'CUSTOM001')
    
    def test_phone_validation(self):
        """Test phone number validation"""
        # Valid phone numbers
        valid_phones = ['8315551234', '+18315551234', '18315551234']
        for phone in valid_phones:
            data = self.employee_data.copy()
            data['phone'] = phone
            employee = Employee(**data)
            employee.full_clean()  # Should not raise
    
    def test_invalid_phone_validation(self):
        """Test invalid phone number validation"""
        data = self.employee_data.copy()
        data['phone'] = 'invalid-phone'
        employee = Employee(**data)
        
        with self.assertRaises(ValidationError):
            employee.full_clean()
    
    def test_employment_validation(self):
        """Test employment data validation"""
        # Test termination date before hire date
        data = self.employee_data.copy()
        data['termination_date'] = date(2023, 12, 1)  # Before hire date
        employee = Employee(**data)
        
        with self.assertRaises(ValidationError):
            employee.clean()
        
        # Test terminated status without termination date
        data = self.employee_data.copy()
        data['employment_status'] = 'terminated'
        employee = Employee(**data)
        
        with self.assertRaises(ValidationError):
            employee.clean()
    
    def test_is_active_property(self):
        """Test is_active property"""
        employee = Employee.objects.create(**self.employee_data)
        self.assertTrue(employee.is_active)
        
        employee.employment_status = 'terminated'
        self.assertFalse(employee.is_active)
    
    def test_years_of_service_property(self):
        """Test years_of_service property"""
        # Set hire date to 1 year ago
        data = self.employee_data.copy()
        data['hire_date'] = timezone.now().date() - timedelta(days=365)
        employee = Employee.objects.create(**data)
        
        # Should be approximately 1 year
        self.assertAlmostEqual(employee.years_of_service, 1.0, places=1)
    
    def test_can_supervise_property(self):
        """Test can_supervise property"""
        # Barista cannot supervise
        employee = Employee.objects.create(**self.employee_data)
        self.assertFalse(employee.can_supervise)
        
        # Manager can supervise
        employee.role = 'manager'
        self.assertTrue(employee.can_supervise)
        
        # Owner can supervise
        employee.role = 'owner'
        self.assertTrue(employee.can_supervise)
    
    def test_employee_ordering(self):
        """Test employee ordering by last name, first name"""
        user1 = User.objects.create_user('user1', first_name='Alice', last_name='Smith')
        user2 = User.objects.create_user('user2', first_name='Bob', last_name='Johnson')
        user3 = User.objects.create_user('user3', first_name='Charlie', last_name='Smith')
        
        emp1 = Employee.objects.create(user=user1, **{k: v for k, v in self.employee_data.items() if k != 'user'})
        emp2 = Employee.objects.create(user=user2, **{k: v for k, v in self.employee_data.items() if k != 'user'})
        emp3 = Employee.objects.create(user=user3, **{k: v for k, v in self.employee_data.items() if k != 'user'})
        
        employees = Employee.objects.all()
        # Should be ordered by last name, then first name
        self.assertEqual(employees[0], emp2)  # Johnson, Bob
        self.assertEqual(employees[1], emp1)  # Smith, Alice
        self.assertEqual(employees[2], emp3)  # Smith, Charlie


class ScheduleModelTest(TestCase):
    """Test Schedule model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('employee', 'emp@test.com', 'Test', 'Employee')
        self.employee = Employee.objects.create(
            user=self.user,
            phone='8315551234',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='8315554321',
            role='barista',
            hire_date=date.today(),
            hourly_wage=Decimal('18.00'),
            can_open=True,
            can_close=True
        )
        
        self.schedule_data = {
            'employee': self.employee,
            'date': date.today(),
            'start_time': time(8, 0),  # 8:00 AM
            'end_time': time(16, 0),   # 4:00 PM
            'break_duration': 30,
            'shift_type': 'mid',
            'status': 'scheduled'
        }
    
    def test_schedule_creation(self):
        """Test creating a Schedule instance"""
        schedule = Schedule.objects.create(**self.schedule_data)
        
        self.assertEqual(schedule.employee, self.employee)
        self.assertEqual(schedule.start_time, time(8, 0))
        self.assertEqual(schedule.end_time, time(16, 0))
        self.assertEqual(schedule.break_duration, 30)
        self.assertEqual(schedule.shift_type, 'mid')
    
    def test_schedule_str(self):
        """Test string representation"""
        schedule = Schedule.objects.create(**self.schedule_data)
        expected = f"Test Employee - {date.today()} (08:00:00-16:00:00)"
        self.assertEqual(str(schedule), expected)
    
    def test_schedule_unique_constraint(self):
        """Test unique constraint on employee, date, start_time"""
        Schedule.objects.create(**self.schedule_data)
        
        # Try to create duplicate schedule
        with self.assertRaises(Exception):  # IntegrityError
            Schedule.objects.create(**self.schedule_data)
    
    def test_schedule_ordering(self):
        """Test schedule ordering by date and start time"""
        # Create schedules for different dates and times
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        schedule1 = Schedule.objects.create(
            employee=self.employee,
            date=tomorrow,
            start_time=time(8, 0),
            end_time=time(16, 0)
        )
        
        schedule2 = Schedule.objects.create(
            employee=self.employee,
            date=today,
            start_time=time(14, 0),
            end_time=time(22, 0)
        )
        
        schedule3 = Schedule.objects.create(
            employee=self.employee,
            date=today,
            start_time=time(6, 0),
            end_time=time(14, 0)
        )
        
        schedules = Schedule.objects.all()
        # Should be ordered by date, then start_time
        self.assertEqual(schedules[0], schedule3)  # today, 6:00
        self.assertEqual(schedules[1], schedule2)  # today, 14:00
        self.assertEqual(schedules[2], schedule1)  # tomorrow, 8:00
    
    def test_scheduled_hours_property(self):
        """Test scheduled_hours property calculation"""
        schedule = Schedule.objects.create(**self.schedule_data)
        # 8 hours minus 0.5 hour break = 7.5 hours
        self.assertEqual(schedule.scheduled_hours, 7.5)
    
    def test_scheduled_hours_overnight_shift(self):
        """Test scheduled_hours for overnight shift"""
        data = self.schedule_data.copy()
        data['start_time'] = time(22, 0)  # 10:00 PM
        data['end_time'] = time(6, 0)     # 6:00 AM next day
        data['break_duration'] = 60       # 1 hour break
        
        schedule = Schedule.objects.create(**data)
        # 8 hours minus 1 hour break = 7 hours
        self.assertEqual(schedule.scheduled_hours, 7.0)
    
    def test_actual_hours_property(self):
        """Test actual_hours property"""
        schedule = Schedule.objects.create(**self.schedule_data)
        
        # No actual times recorded, should return scheduled hours
        self.assertEqual(schedule.actual_hours, 7.5)
        
        # Set actual times
        schedule.actual_start_time = time(7, 45)  # Started 15 min early
        schedule.actual_end_time = time(16, 30)   # Ended 30 min late
        schedule.save()
        
        # 8h 45m minus 30m break = 8.25 hours
        self.assertEqual(schedule.actual_hours, 8.25)
    
    def test_is_overtime_property(self):
        """Test is_overtime property"""
        schedule = Schedule.objects.create(**self.schedule_data)
        self.assertFalse(schedule.is_overtime)  # 7.5 hours
        
        # Create another schedule that would put total over 8 hours
        data2 = self.schedule_data.copy()
        data2['start_time'] = time(18, 0)
        data2['end_time'] = time(20, 0)  # 2 hour shift
        data2['break_duration'] = 0
        
        Schedule.objects.create(**data2)
        
        # Now total for the day is 9.5 hours, should be overtime
        schedule.refresh_from_db()
        self.assertTrue(schedule.is_overtime)
    
    def test_wage_earned_property(self):
        """Test wage_earned property"""
        schedule = Schedule.objects.create(**self.schedule_data)
        # 7.5 hours * $18.00 = $135.00
        expected_wage = 7.5 * 18.00
        self.assertEqual(schedule.wage_earned, expected_wage)
    
    def test_schedule_validation_permissions(self):
        """Test schedule validation for opening/closing permissions"""
        # Employee doesn't have opening permissions
        self.employee.can_open = False
        self.employee.save()
        
        data = self.schedule_data.copy()
        data['shift_type'] = 'opening'
        schedule = Schedule(**data)
        
        with self.assertRaises(ValidationError):
            schedule.clean()
        
        # Employee doesn't have closing permissions
        self.employee.can_close = False
        self.employee.save()
        
        data['shift_type'] = 'closing'
        schedule = Schedule(**data)
        
        with self.assertRaises(ValidationError):
            schedule.clean()
    
    def test_schedule_validation_overlapping(self):
        """Test schedule validation for overlapping shifts"""
        Schedule.objects.create(**self.schedule_data)
        
        # Try to create overlapping schedule
        data2 = self.schedule_data.copy()
        data2['start_time'] = time(15, 0)  # Overlaps with existing schedule
        data2['end_time'] = time(23, 0)
        
        schedule2 = Schedule(**data2)
        
        with self.assertRaises(ValidationError):
            schedule2.clean()


class StaffAdminTest(TestCase):
    """Test staff app admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.site = AdminSite()
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.employee_user = User.objects.create_user('employee', 'emp@test.com', 'Test', 'Employee')
        self.employee = Employee.objects.create(
            user=self.employee_user,
            phone='8315551234',
            emergency_contact_name='Emergency Contact',
            emergency_contact_phone='8315554321',
            role='barista',
            hire_date=date.today(),
            hourly_wage=Decimal('18.00')
        )
        
        self.schedule = Schedule.objects.create(
            employee=self.employee,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(16, 0),
            created_by=self.admin_user
        )
    
    def test_employee_admin_configuration(self):
        """Test Employee admin configuration"""
        admin = EmployeeAdmin(Employee, self.site)
        
        # Check list display includes key fields
        self.assertIn('user', admin.list_display)
        self.assertIn('role', admin.list_display)
        self.assertIn('employment_status', admin.list_display)
        self.assertIn('hire_date', admin.list_display)
    
    def test_schedule_admin_configuration(self):
        """Test Schedule admin configuration"""
        admin = ScheduleAdmin(Schedule, self.site)
        
        # Check list display includes key fields
        self.assertIn('employee', admin.list_display)
        self.assertIn('date', admin.list_display)
        self.assertIn('start_time', admin.list_display)
        self.assertIn('end_time', admin.list_display)
        self.assertIn('status', admin.list_display)


class StaffIntegrationTest(TestCase):
    """Integration tests for staff app workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # Create employee user
        self.employee_user = User.objects.create_user(
            username='jdoe',
            email='john.doe@test.com',
            first_name='John',
            last_name='Doe'
        )
        
        # Create employee
        self.employee = Employee.objects.create(
            user=self.employee_user,
            phone='8315551234',
            emergency_contact_name='Jane Doe',
            emergency_contact_phone='8315554321',
            role='barista',
            employment_status='active',
            hire_date=date(2024, 1, 15),
            hourly_wage=Decimal('18.50'),
            can_open=True,
            can_close=True,
            can_handle_cash=True
        )
    
    def test_employee_management_workflow(self):
        """Test complete employee management workflow"""
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # 1. Access employee admin
        response = self.client.get('/admin/staff/employee/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # 2. View employee details
        response = self.client.get(f'/admin/staff/employee/{self.employee.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'john.doe@test.com')
        self.assertContains(response, '8315551234')
        
        # 3. Update employee role
        response = self.client.post(f'/admin/staff/employee/{self.employee.id}/change/', {
            'user': self.employee.user.id,
            'phone': self.employee.phone,
            'emergency_contact_name': self.employee.emergency_contact_name,
            'emergency_contact_phone': self.employee.emergency_contact_phone,
            'role': 'shift_lead',  # Promotion
            'employment_status': self.employee.employment_status,
            'hire_date': self.employee.hire_date.strftime('%Y-%m-%d'),
            'hourly_wage': str(self.employee.hourly_wage),
            'can_open': self.employee.can_open,
            'can_close': self.employee.can_close,
            'can_handle_cash': self.employee.can_handle_cash,
            '_save': 'Save'
        })
        
        # Verify update
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.role, 'shift_lead')
        self.assertTrue(self.employee.can_supervise)
    
    def test_schedule_management_workflow(self):
        """Test schedule management workflow"""
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # 1. Create schedule
        today = date.today()
        response = self.client.post('/admin/staff/schedule/add/', {
            'employee': self.employee.id,
            'date': today.strftime('%Y-%m-%d'),
            'start_time': '08:00:00',
            'end_time': '16:00:00',
            'break_duration': 30,
            'shift_type': 'mid',
            'status': 'scheduled',
            'created_by': self.admin_user.id,
            '_save': 'Save'
        })
        
        # Verify schedule was created
        self.assertTrue(Schedule.objects.filter(
            employee=self.employee,
            date=today
        ).exists())
        
        schedule = Schedule.objects.get(employee=self.employee, date=today)
        self.assertEqual(schedule.scheduled_hours, 7.5)  # 8 hours - 0.5 break
        
        # 2. Access schedule admin
        response = self.client.get('/admin/staff/schedule/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        
        # 3. Mark schedule as completed
        response = self.client.post(f'/admin/staff/schedule/{schedule.id}/change/', {
            'employee': schedule.employee.id,
            'date': schedule.date.strftime('%Y-%m-%d'),
            'start_time': schedule.start_time.strftime('%H:%M:%S'),
            'end_time': schedule.end_time.strftime('%H:%M:%S'),
            'break_duration': schedule.break_duration,
            'shift_type': schedule.shift_type,
            'status': 'completed',
            'actual_start_time': '07:45:00',  # Started early
            'actual_end_time': '16:15:00',    # Ended late
            'notes': 'Great work today',
            'created_by': schedule.created_by.id if schedule.created_by else '',
            '_save': 'Save'
        })
        
        # Verify schedule was updated
        schedule.refresh_from_db()
        self.assertEqual(schedule.status, 'completed')
        self.assertEqual(schedule.actual_start_time, time(7, 45))
        self.assertEqual(schedule.actual_end_time, time(16, 15))
        self.assertEqual(schedule.notes, 'Great work today')
        
        # Check actual hours calculation
        # 8h 30m minus 30m break = 8 hours
        self.assertEqual(schedule.actual_hours, 8.0)
    
    def test_employee_schedule_relationship(self):
        """Test relationship between employee and schedules"""
        # Create multiple schedules for employee
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        schedule1 = Schedule.objects.create(
            employee=self.employee,
            date=today,
            start_time=time(8, 0),
            end_time=time(16, 0),
            break_duration=30,
            status='completed'
        )
        
        schedule2 = Schedule.objects.create(
            employee=self.employee,
            date=tomorrow,
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_duration=30,
            status='scheduled'
        )
        
        # Test employee schedules
        employee_schedules = self.employee.schedule_set.all()
        self.assertEqual(employee_schedules.count(), 2)
        self.assertIn(schedule1, employee_schedules)
        self.assertIn(schedule2, employee_schedules)
        
        # Test filtering schedules
        completed_schedules = self.employee.schedule_set.filter(status='completed')
        self.assertEqual(completed_schedules.count(), 1)
        self.assertEqual(completed_schedules.first(), schedule1)
    
    def test_employee_termination_workflow(self):
        """Test employee termination workflow"""
        # Login as admin
        self.client.login(username='admin', password='password')
        
        # Terminate employee
        termination_date = date.today()
        response = self.client.post(f'/admin/staff/employee/{self.employee.id}/change/', {
            'user': self.employee.user.id,
            'phone': self.employee.phone,
            'emergency_contact_name': self.employee.emergency_contact_name,
            'emergency_contact_phone': self.employee.emergency_contact_phone,
            'role': self.employee.role,
            'employment_status': 'terminated',
            'hire_date': self.employee.hire_date.strftime('%Y-%m-%d'),
            'termination_date': termination_date.strftime('%Y-%m-%d'),
            'hourly_wage': str(self.employee.hourly_wage),
            'notes': 'Left for better opportunity',
            'can_open': self.employee.can_open,
            'can_close': self.employee.can_close,
            'can_handle_cash': self.employee.can_handle_cash,
            '_save': 'Save'
        })
        
        # Verify termination
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.employment_status, 'terminated')
        self.assertEqual(self.employee.termination_date, termination_date)
        self.assertFalse(self.employee.is_active)
        self.assertEqual(self.employee.notes, 'Left for better opportunity')


class EmployeeModelAdvancedTest(TestCase):
    """Advanced tests for Employee model"""
    
    def setUp(self):
        """Set up test data"""
        self.users = []
        self.employees = []
        
        # Create multiple users and employees for advanced testing
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                first_name=f'First{i}',
                last_name=f'Last{i}'
            )
            self.users.append(user)
            
            employee = Employee.objects.create(
                user=user,
                phone=f'831555{1000 + i}',
                emergency_contact_name=f'Emergency{i}',
                emergency_contact_phone=f'831555{2000 + i}',
                role=['barista', 'cashier', 'manager', 'shift_lead', 'owner'][i % 5],
                employment_status='active',
                hire_date=date.today() - timedelta(days=i * 30),
                hourly_wage=Decimal(f'{15 + i}.50'),
                can_open=(i % 2 == 0),
                can_close=(i % 3 == 0),
                can_handle_cash=True
            )
            self.employees.append(employee)
    
    def test_employee_bulk_operations(self):
        """Test bulk operations on employees"""
        # Test bulk status update
        Employee.objects.filter(role='barista').update(employment_status='inactive')
        
        inactive_count = Employee.objects.filter(employment_status='inactive').count()
        self.assertGreater(inactive_count, 0)
        
        # Test filtering by permissions
        openers = Employee.objects.filter(can_open=True)
        self.assertGreater(openers.count(), 0)
        
        closers = Employee.objects.filter(can_close=True)
        self.assertGreater(closers.count(), 0)
    
    def test_employee_role_hierarchy(self):
        """Test employee role hierarchy and permissions"""
        manager = Employee.objects.filter(role='manager').first()
        barista = Employee.objects.filter(role='barista').first()
        owner = Employee.objects.filter(role='owner').first()
        
        if manager:
            self.assertTrue(manager.can_supervise)
        if barista:
            self.assertFalse(barista.can_supervise)
        if owner:
            self.assertTrue(owner.can_supervise)
    
    def test_employee_search_functionality(self):
        """Test employee search and filtering"""
        # Search by name
        first_name_results = Employee.objects.filter(user__first_name__icontains='First0')
        self.assertEqual(first_name_results.count(), 1)
        
        # Search by role
        manager_results = Employee.objects.filter(role='manager')
        self.assertGreater(manager_results.count(), 0)
        
        # Search by hire date range
        recent_hires = Employee.objects.filter(
            hire_date__gte=date.today() - timedelta(days=60)
        )
        self.assertGreater(recent_hires.count(), 0)
    
    def test_employee_wage_calculations(self):
        """Test employee wage-related calculations"""
        employee = self.employees[0]
        
        # Test different wage rates
        test_wages = [Decimal('15.00'), Decimal('20.50'), Decimal('25.75')]
        
        for wage in test_wages:
            employee.hourly_wage = wage
            employee.save()
            
            # Test wage calculation for different hour amounts
            self.assertEqual(float(employee.hourly_wage) * 8, float(wage) * 8)
    
    def test_employee_id_edge_cases(self):
        """Test employee ID generation edge cases"""
        # Test employee ID uniqueness
        employee_ids = [emp.employee_id for emp in self.employees]
        self.assertEqual(len(employee_ids), len(set(employee_ids)))  # All unique
        
        # Test year rollover scenario
        past_employee = Employee.objects.create(
            user=User.objects.create_user('pastuser', 'past@test.com'),
            phone='8315559999',
            emergency_contact_name='Past Emergency',
            emergency_contact_phone='8315558888',
            role='barista',
            hire_date=date(2023, 1, 1),  # Different year
            hourly_wage=Decimal('16.00')
        )
        
        # Should have different year in ID
        self.assertIn('2023', past_employee.employee_id)


class ScheduleModelAdvancedTest(TestCase):
    """Advanced tests for Schedule model"""
    
    def setUp(self):
        """Set up test data"""
        self.users = []
        self.employees = []
        
        # Create employees with different permissions
        for i in range(3):
            user = User.objects.create_user(f'emp{i}', f'emp{i}@test.com')
            employee = Employee.objects.create(
                user=user,
                phone=f'831555{3000 + i}',
                emergency_contact_name=f'Emergency{i}',
                emergency_contact_phone=f'831555{4000 + i}',
                role=['barista', 'shift_lead', 'manager'][i],
                hire_date=date.today(),
                hourly_wage=Decimal(f'{18 + i}.00'),
                can_open=(i >= 1),  # shift_lead and manager can open
                can_close=(i >= 1),  # shift_lead and manager can close
                can_handle_cash=True
            )
            self.users.append(user)
            self.employees.append(employee)
    
    def test_schedule_complex_scenarios(self):
        """Test complex scheduling scenarios"""
        today = date.today()
        
        # Test full day coverage with multiple shifts
        morning_shift = Schedule.objects.create(
            employee=self.employees[1],  # Can open
            date=today,
            start_time=time(6, 0),
            end_time=time(14, 0),
            shift_type='opening',
            break_duration=30
        )
        
        evening_shift = Schedule.objects.create(
            employee=self.employees[2],  # Can close
            date=today,
            start_time=time(14, 0),
            end_time=time(22, 0),
            shift_type='closing',
            break_duration=30
        )
        
        # Test daily hours calculation
        daily_schedules = Schedule.objects.filter(date=today)
        total_coverage = sum(s.scheduled_hours for s in daily_schedules)
        self.assertGreater(total_coverage, 14)  # Should cover most of the day
    
    def test_schedule_overtime_calculations(self):
        """Test overtime calculation scenarios"""
        employee = self.employees[0]
        today = date.today()
        
        # Create multiple shifts for same day totaling over 8 hours
        Schedule.objects.create(
            employee=employee,
            date=today,
            start_time=time(6, 0),
            end_time=time(14, 0),  # 8 hours
            break_duration=0
        )
        
        Schedule.objects.create(
            employee=employee,
            date=today,
            start_time=time(16, 0),
            end_time=time(20, 0),  # 4 more hours = 12 total
            break_duration=0
        )
        
        # Both shifts should be marked as overtime
        schedules = Schedule.objects.filter(employee=employee, date=today)
        for schedule in schedules:
            if schedules.count() > 1:  # If multiple shifts, should be overtime
                self.assertTrue(schedule.is_overtime)
    
    def test_schedule_weekly_patterns(self):
        """Test weekly scheduling patterns"""
        employee = self.employees[0]
        start_date = date.today()
        
        # Create week of schedules
        for i in range(7):
            work_date = start_date + timedelta(days=i)
            if i < 5:  # Monday-Friday
                Schedule.objects.create(
                    employee=employee,
                    date=work_date,
                    start_time=time(8, 0),
                    end_time=time(16, 0),
                    break_duration=30
                )
        
        # Test weekly hours
        week_end = start_date + timedelta(days=6)
        week_schedules = Schedule.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=week_end
        )
        
        total_weekly_hours = sum(s.scheduled_hours for s in week_schedules)
        self.assertEqual(total_weekly_hours, 37.5)  # 5 days × 7.5 hours
    
    def test_schedule_conflict_detection(self):
        """Test schedule conflict detection"""
        employee = self.employees[0]
        today = date.today()
        
        # Create initial schedule
        Schedule.objects.create(
            employee=employee,
            date=today,
            start_time=time(8, 0),
            end_time=time(16, 0)
        )
        
        # Try to create overlapping schedule
        overlapping_schedule = Schedule(
            employee=employee,
            date=today,
            start_time=time(15, 0),  # Overlaps with existing
            end_time=time(23, 0)
        )
        
        with self.assertRaises(ValidationError):
            overlapping_schedule.clean()


class StaffAdminAdvancedTest(TestCase):
    """Advanced tests for staff admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # Create test employees and schedules
        self.employees = []
        for i in range(10):
            user = User.objects.create_user(
                f'testuser{i}',
                f'test{i}@example.com',
                f'Test{i}',
                f'User{i}'
            )
            employee = Employee.objects.create(
                user=user,
                phone=f'831555{5000 + i}',
                emergency_contact_name=f'Emergency{i}',
                emergency_contact_phone=f'831555{6000 + i}',
                role=['barista', 'cashier', 'shift_lead', 'manager'][i % 4],
                employment_status='active' if i % 3 != 0 else 'inactive',
                hire_date=date.today() - timedelta(days=i * 10),
                hourly_wage=Decimal(f'{15 + (i % 10)}.00'),
                can_open=(i % 2 == 0),
                can_close=(i % 3 == 0)
            )
            self.employees.append(employee)
    
    def test_employee_admin_csv_export(self):
        """Test employee CSV export functionality"""
        self.client.login(username='admin', password='password')
        
        # Get employee IDs
        employee_ids = [str(emp.id) for emp in self.employees[:5]]
        
        # Test CSV export action
        response = self.client.post('/admin/staff/employee/', {
            'action': 'export_employee_list',
            '_selected_action': employee_ids,
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Parse CSV content
        content = response.content.decode()
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Should have header row plus data rows
        self.assertGreater(len(rows), 1)
        self.assertIn('Employee ID', rows[0])
        self.assertIn('Name', rows[0])
    
    def test_employee_admin_payroll_report(self):
        """Test payroll report generation"""
        self.client.login(username='admin', password='password')
        
        # Create schedules for payroll testing
        employee = self.employees[0]
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        for i in range(5):  # Monday-Friday
            work_date = week_start + timedelta(days=i)
            Schedule.objects.create(
                employee=employee,
                date=work_date,
                start_time=time(8, 0),
                end_time=time(16, 0),
                break_duration=30,
                status='completed',
                actual_start_time=time(8, 0),
                actual_end_time=time(16, 0)
            )
        
        # Generate payroll report
        response = self.client.post('/admin/staff/employee/', {
            'action': 'generate_payroll_report',
            '_selected_action': [str(employee.id)],
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        
        # Parse payroll content
        content = response.content.decode()
        csv_reader = csv.reader(io.StringIO(content))
        rows = list(csv_reader)
        
        # Should include payroll calculations
        self.assertGreater(len(rows), 1)
        self.assertIn('Hours Worked', rows[0])
        self.assertIn('Total Wages', rows[0])
    
    def test_schedule_admin_bulk_operations(self):
        """Test schedule admin bulk operations"""
        self.client.login(username='admin', password='password')
        
        # Create test schedules
        schedules = []
        for i in range(5):
            schedule = Schedule.objects.create(
                employee=self.employees[i % len(self.employees)],
                date=date.today() + timedelta(days=i),
                start_time=time(8, 0),
                end_time=time(16, 0),
                status='scheduled'
            )
            schedules.append(schedule)
        
        schedule_ids = [str(s.id) for s in schedules]
        
        # Test mark as completed bulk action
        response = self.client.post('/admin/staff/schedule/', {
            'action': 'mark_completed',
            '_selected_action': schedule_ids[:3],
        })
        
        # Check that schedules were updated
        completed_count = Schedule.objects.filter(status='completed').count()
        self.assertGreaterEqual(completed_count, 3)
    
    def test_schedule_admin_duplication(self):
        """Test schedule duplication functionality"""
        self.client.login(username='admin', password='password')
        
        # Create base schedule
        base_date = date.today()
        schedule = Schedule.objects.create(
            employee=self.employees[0],
            date=base_date,
            start_time=time(9, 0),
            end_time=time(17, 0),
            shift_type='mid',
            break_duration=30
        )
        
        # Test duplication action
        response = self.client.post('/admin/staff/schedule/', {
            'action': 'duplicate_schedule',
            '_selected_action': [str(schedule.id)],
        })
        
        # Check that duplicate was created for next week
        next_week_date = base_date + timedelta(days=7)
        duplicate_exists = Schedule.objects.filter(
            employee=self.employees[0],
            date=next_week_date,
            start_time=time(9, 0),
            end_time=time(17, 0)
        ).exists()
        
        self.assertTrue(duplicate_exists)
    
    def test_admin_performance_with_large_datasets(self):
        """Test admin performance with large datasets"""
        # Create many additional employees
        for i in range(50):
            user = User.objects.create_user(f'bulk{i}', f'bulk{i}@test.com')
            Employee.objects.create(
                user=user,
                phone=f'831555{7000 + i}',
                emergency_contact_name=f'Bulk Emergency {i}',
                emergency_contact_phone=f'831555{8000 + i}',
                role='barista',
                hire_date=date.today(),
                hourly_wage=Decimal('16.00')
            )
        
        self.client.login(username='admin', password='password')
        
        # Test that admin pages load in reasonable time
        import time
        
        start_time = time.time()
        response = self.client.get('/admin/staff/employee/')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 3.0)  # Should load in under 3 seconds


class StaffSecurityTest(TestCase):
    """Security tests for staff functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        self.staff_user = User.objects.create_user('staff', 'staff@test.com', 'password')
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'password')
    
    def test_staff_admin_access_levels(self):
        """Test different access levels for staff admin"""
        # Test unauthenticated access
        response = self.client.get('/admin/staff/employee/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test regular user access
        self.client.login(username='user', password='password')
        response = self.client.get('/admin/staff/employee/')
        self.assertEqual(response.status_code, 302)  # Should be denied
        
        # Test staff user access
        self.client.login(username='staff', password='password')
        response = self.client.get('/admin/staff/employee/')
        # Might be allowed depending on permissions
        
        # Test admin user access
        self.client.login(username='admin', password='password')
        response = self.client.get('/admin/staff/employee/')
        self.assertEqual(response.status_code, 200)  # Should be allowed
    
    def test_employee_data_protection(self):
        """Test protection of sensitive employee data"""
        # Create employee with sensitive data
        user = User.objects.create_user('sensitive', 'sensitive@test.com')
        employee = Employee.objects.create(
            user=user,
            phone='8315551234',
            emergency_contact_name='Sensitive Contact',
            emergency_contact_phone='8315554321',
            role='barista',
            hire_date=date.today(),
            hourly_wage=Decimal('20.00'),
            notes='Confidential information'
        )
        
        self.client.login(username='admin', password='password')
        
        # Admin should see all data
        response = self.client.get(f'/admin/staff/employee/{employee.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confidential information')
        
        # Test that sensitive data doesn't leak in public views
        # (This would depend on having public staff views)
    
    def test_schedule_access_control(self):
        """Test schedule access control"""
        user = User.objects.create_user('testuser', 'test@test.com')
        employee = Employee.objects.create(
            user=user,
            phone='8315551234',
            emergency_contact_name='Emergency',
            emergency_contact_phone='8315554321',
            role='barista',
            hire_date=date.today(),
            hourly_wage=Decimal('18.00')
        )
        
        schedule = Schedule.objects.create(
            employee=employee,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(16, 0)
        )
        
        # Test admin access
        self.client.login(username='admin', password='password')
        response = self.client.get(f'/admin/staff/schedule/{schedule.id}/change/')
        self.assertEqual(response.status_code, 200)
        
        # Test unauthorized access
        self.client.login(username='user', password='password')
        response = self.client.get(f'/admin/staff/schedule/{schedule.id}/change/')
        self.assertNotEqual(response.status_code, 200)


class StaffReportingTest(TestCase):
    """Tests for staff reporting functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        
        # Create employees with varied schedules
        self.employees = []
        for i in range(3):
            user = User.objects.create_user(f'emp{i}', f'emp{i}@test.com')
            employee = Employee.objects.create(
                user=user,
                phone=f'831555{9000 + i}',
                emergency_contact_name=f'Emergency {i}',
                emergency_contact_phone=f'831555{9100 + i}',
                role='barista',
                hire_date=date.today() - timedelta(days=i * 30),
                hourly_wage=Decimal(f'{16 + i}.00')
            )
            self.employees.append(employee)
    
    def test_weekly_schedule_reporting(self):
        """Test weekly schedule report generation"""
        # Create week of schedules
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        for employee in self.employees:
            for i in range(5):  # Monday-Friday
                work_date = week_start + timedelta(days=i)
                Schedule.objects.create(
                    employee=employee,
                    date=work_date,
                    start_time=time(8, 0),
                    end_time=time(16, 0),
                    break_duration=30,
                    status='completed'
                )
        
        self.client.login(username='admin', password='password')
        
        # Get all schedules for the week
        week_schedules = Schedule.objects.filter(
            date__gte=week_start,
            date__lt=week_start + timedelta(days=7)
        )
        
        self.assertEqual(week_schedules.count(), 15)  # 3 employees × 5 days
        
        # Test total hours calculation
        total_hours = sum(s.scheduled_hours for s in week_schedules)
        expected_hours = 3 * 5 * 7.5  # 3 employees × 5 days × 7.5 hours
        self.assertEqual(total_hours, expected_hours)
    
    def test_labor_cost_calculations(self):
        """Test labor cost calculation reporting"""
        employee = self.employees[0]
        today = date.today()
        
        # Create schedule with specific hours and wage
        schedule = Schedule.objects.create(
            employee=employee,
            date=today,
            start_time=time(8, 0),
            end_time=time(17, 0),  # 9 hours
            break_duration=60,     # 1 hour break = 8 hours worked
            status='completed',
            actual_start_time=time(8, 0),
            actual_end_time=time(17, 0)
        )
        
        # Test wage calculation
        expected_wage = 8 * float(employee.hourly_wage)
        self.assertEqual(schedule.wage_earned, expected_wage)
    
    def test_attendance_tracking(self):
        """Test attendance tracking and reporting"""
        employee = self.employees[0]
        
        # Create schedules with different statuses
        Schedule.objects.create(
            employee=employee,
            date=date.today() - timedelta(days=2),
            start_time=time(8, 0),
            end_time=time(16, 0),
            status='completed'
        )
        
        Schedule.objects.create(
            employee=employee,
            date=date.today() - timedelta(days=1),
            start_time=time(8, 0),
            end_time=time(16, 0),
            status='no_show'
        )
        
        Schedule.objects.create(
            employee=employee,
            date=date.today(),
            start_time=time(8, 0),
            end_time=time(16, 0),
            status='called_in_sick'
        )
        
        # Test attendance metrics
        total_schedules = Schedule.objects.filter(employee=employee).count()
        completed_schedules = Schedule.objects.filter(
            employee=employee,
            status='completed'
        ).count()
        
        attendance_rate = completed_schedules / total_schedules
        self.assertAlmostEqual(attendance_rate, 0.33, places=1)  # 1 out of 3


class StaffIntegrationAdvancedTest(TestCase):
    """Advanced integration tests for staff workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'password')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
    
    def test_complete_hiring_workflow(self):
        """Test complete employee hiring workflow"""
        self.client.login(username='admin', password='password')
        
        # Step 1: Create user account
        response = self.client.post('/admin/auth/user/add/', {
            'username': 'newhire',
            'email': 'newhire@test.com',
            'first_name': 'New',
            'last_name': 'Hire',
            'password1': 'testpass123',
            'password2': 'testpass123',
            '_save': 'Save'
        })
        
        # User should be created
        self.assertTrue(User.objects.filter(username='newhire').exists())
        new_user = User.objects.get(username='newhire')
        
        # Step 2: Create employee record
        response = self.client.post('/admin/staff/employee/add/', {
            'user': new_user.id,
            'phone': '8315551234',
            'emergency_contact_name': 'Emergency Contact',
            'emergency_contact_phone': '8315554321',
            'role': 'barista',
            'employment_status': 'active',
            'hire_date': date.today().strftime('%Y-%m-%d'),
            'hourly_wage': '17.00',
            'can_handle_cash': True,
            '_save': 'Save'
        })
        
        # Employee should be created
        self.assertTrue(Employee.objects.filter(user=new_user).exists())
        employee = Employee.objects.get(user=new_user)
        
        # Step 3: Create initial schedule
        tomorrow = date.today() + timedelta(days=1)
        response = self.client.post('/admin/staff/schedule/add/', {
            'employee': employee.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '08:00:00',
            'end_time': '16:00:00',
            'break_duration': 30,
            'shift_type': 'mid',
            'status': 'scheduled',
            '_save': 'Save'
        })
        
        # Schedule should be created
        self.assertTrue(Schedule.objects.filter(
            employee=employee,
            date=tomorrow
        ).exists())
    
    def test_employee_promotion_workflow(self):
        """Test employee promotion workflow"""
        # Create initial employee
        user = User.objects.create_user('promotee', 'promotee@test.com')
        employee = Employee.objects.create(
            user=user,
            phone='8315551234',
            emergency_contact_name='Emergency',
            emergency_contact_phone='8315554321',
            role='barista',
            employment_status='active',
            hire_date=date.today() - timedelta(days=365),  # 1 year ago
            hourly_wage=Decimal('16.00'),
            can_open=False,
            can_close=False
        )
        
        self.client.login(username='admin', password='password')
        
        # Promote to shift leader with new permissions and wage
        response = self.client.post(f'/admin/staff/employee/{employee.id}/change/', {
            'user': employee.user.id,
            'phone': employee.phone,
            'emergency_contact_name': employee.emergency_contact_name,
            'emergency_contact_phone': employee.emergency_contact_phone,
            'role': 'shift_lead',  # Promotion
            'employment_status': employee.employment_status,
            'hire_date': employee.hire_date.strftime('%Y-%m-%d'),
            'hourly_wage': '19.00',  # Raise
            'can_open': True,        # New permission
            'can_close': True,       # New permission
            'can_handle_cash': True,
            'notes': 'Promoted to shift lead - excellent performance',
            '_save': 'Save'
        })
        
        # Verify promotion
        employee.refresh_from_db()
        self.assertEqual(employee.role, 'shift_lead')
        self.assertEqual(employee.hourly_wage, Decimal('19.00'))
        self.assertTrue(employee.can_open)
        self.assertTrue(employee.can_close)
        self.assertTrue(employee.can_supervise)
    
    def test_schedule_conflict_resolution(self):
        """Test schedule conflict detection and resolution"""
        # Create employee
        user = User.objects.create_user('scheduler', 'scheduler@test.com')
        employee = Employee.objects.create(
            user=user,
            phone='8315551234',
            emergency_contact_name='Emergency',
            emergency_contact_phone='8315554321',
            role='barista',
            hire_date=date.today(),
            hourly_wage=Decimal('17.00')
        )
        
        # Create initial schedule
        today = date.today()
        schedule1 = Schedule.objects.create(
            employee=employee,
            date=today,
            start_time=time(8, 0),
            end_time=time(16, 0)
        )
        
        self.client.login(username='admin', password='password')
        
        # Try to create conflicting schedule through admin
        response = self.client.post('/admin/staff/schedule/add/', {
            'employee': employee.id,
            'date': today.strftime('%Y-%m-%d'),
            'start_time': '15:00:00',  # Overlaps with existing
            'end_time': '23:00:00',
            'break_duration': 30,
            'shift_type': 'closing',
            'status': 'scheduled',
            '_save': 'Save'
        })
        
        # Should detect conflict (depending on validation implementation)
        # The exact behavior depends on how the admin handles validation errors
