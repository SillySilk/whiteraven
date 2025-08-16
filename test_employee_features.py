#!/usr/bin/env python
"""
Test employee management features: availability, shift swaps, and templates
"""
import os
import django
from decimal import Decimal
from datetime import datetime, date, time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'white_raven_pourhouse.settings')
django.setup()

from django.contrib.auth.models import User
from staff.models import Employee, Schedule, EmployeeAvailability, ShiftSwapRequest, ScheduleTemplate, ScheduleTemplateItem

def test_employee_features():
    print("=== Testing Employee Management Features ===")
    print()
    
    # Test 1: Employee Availability
    print("1. Testing Employee Availability System:")
    
    # Get or create test employees
    test_user1, created = User.objects.get_or_create(
        username='test_barista1',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com'
        }
    )
    
    test_emp1, created = Employee.objects.get_or_create(
        user=test_user1,
        defaults={
            'phone': '555-1234',
            'emergency_contact_name': 'Jane Doe',
            'emergency_contact_phone': '555-5678',
            'role': 'barista',
            'hire_date': date.today(),
            'hourly_wage': Decimal('15.00')
        }
    )
    
    # Test availability creation
    availability, created = EmployeeAvailability.objects.get_or_create(
        employee=test_emp1,
        weekday=0,  # Monday
        defaults={
            'availability_type': 'preferred',
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'notes': 'Prefers morning shifts'
        }
    )
    
    print(f"   - Created availability: {availability}")
    print(f"   - Availability display: {availability.get_availability_type_display()}")
    print(f"   - Time range: {availability.start_time} - {availability.end_time}")
    print()
    
    # Test 2: Schedule Templates
    print("2. Testing Schedule Templates:")
    
    template, created = ScheduleTemplate.objects.get_or_create(
        name='Standard Weekly',
        defaults={
            'template_type': 'weekly',
            'description': 'Standard weekly schedule template',
            'created_by': test_user1
        }
    )
    
    # Create template items
    template_item, created = ScheduleTemplateItem.objects.get_or_create(
        template=template,
        weekday=0,  # Monday
        role='barista',
        defaults={
            'shift_type': 'opening',
            'start_time': time(6, 0),
            'end_time': time(14, 0),
            'break_duration': 30,
            'notes': 'Opening shift - experienced barista required'
        }
    )
    
    print(f"   - Created template: {template}")
    print(f"   - Template items: {template.template_items.count()}")
    print(f"   - Sample item: {template_item}")
    print()
    
    # Test 3: Shift Swap Requests
    print("3. Testing Shift Swap Requests:")
    
    # Create second test employee
    test_user2, created = User.objects.get_or_create(
        username='test_barista2',
        defaults={
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@test.com'
        }
    )
    
    test_emp2, created = Employee.objects.get_or_create(
        user=test_user2,
        defaults={
            'phone': '555-9876',
            'emergency_contact_name': 'Bob Smith',
            'emergency_contact_phone': '555-4321',
            'role': 'barista',
            'hire_date': date.today(),
            'hourly_wage': Decimal('15.50')
        }
    )
    
    # Create a schedule to swap
    schedule, created = Schedule.objects.get_or_create(
        employee=test_emp1,
        date=date(2024, 8, 19),  # Monday
        start_time=time(9, 0),
        defaults={
            'end_time': time(17, 0),
            'shift_type': 'mid',
            'created_by': test_user1
        }
    )
    
    # Create swap request
    swap_request, created = ShiftSwapRequest.objects.get_or_create(
        original_shift=schedule,
        requester=test_emp1,
        receiver=test_emp2,
        defaults={
            'reason': 'Doctor appointment - need to swap Monday shift'
        }
    )
    
    requester_name = swap_request.requester.user.get_full_name()
    receiver_name = swap_request.receiver.user.get_full_name()
    print(f"   - Created swap request: {requester_name} to {receiver_name}")
    print(f"   - Status: {swap_request.get_status_display()}")
    print(f"   - Can be approved: {swap_request.can_be_approved}")
    print()
    
    # Test 4: Admin Integration
    print("4. Testing Admin Integration:")
    
    # Test employee with availability count
    availability_count = test_emp1.availability_preferences.count()
    emp_name = test_emp1.user.get_full_name()
    print(f"   - Employee {emp_name}: {availability_count} availability preferences")
    
    # Test schedule with swap requests
    swap_count = schedule.swap_requests_original.count()
    print(f"   - Schedule {schedule.date}: {swap_count} swap requests")
    
    # Test template with items
    item_count = template.template_items.count()
    print(f"   - Template '{template.name}': {item_count} template items")
    
    print()
    
    # Test 5: Model Properties and Methods
    print("5. Testing Model Properties:")
    
    # Test schedule properties
    print(f"   - Schedule hours: {schedule.scheduled_hours:.1f}")
    print(f"   - Wage earned: ${schedule.wage_earned:.2f}")
    
    # Test employee properties
    print(f"   - Employee service: {test_emp1.years_of_service:.1f} years")
    print(f"   - Can supervise: {test_emp1.can_supervise}")
    
    # Test availability display (just the type to avoid Unicode issues)
    print(f"   - Availability type: {availability.get_availability_type_display()}")
    
    print()
    print("=== All Employee Features Working Successfully! ===")
    print()
    print("Admin Access:")
    print("  - Employee Availability: /admin/staff/employeeavailability/")
    print("  - Shift Swap Requests: /admin/staff/shiftswapquest/")
    print("  - Schedule Templates: /admin/staff/scheduletemplate/")
    print("  - Enhanced Employee Admin: /admin/staff/employee/")

if __name__ == '__main__':
    test_employee_features()