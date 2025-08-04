from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time, timedelta


class Employee(models.Model):
    """
    Employee information extending Django's User model
    for White Raven Pourhouse staff management
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('shift_lead', 'Shift Lead'),
        ('barista', 'Barista'),
        ('cashier', 'Cashier'),
        ('kitchen', 'Kitchen Staff'),
        ('part_time', 'Part-time'),
        ('intern', 'Intern'),
    ]
    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        help_text="Django user account for this employee"
    )
    
    employee_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        help_text="Internal employee ID (auto-generated)"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=20,
        help_text="Employee contact phone number"
    )
    
    emergency_contact_name = models.CharField(
        max_length=100,
        help_text="Emergency contact full name"
    )
    
    emergency_contact_phone = models.CharField(
        validators=[phone_regex], 
        max_length=20,
        help_text="Emergency contact phone number"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='barista',
        help_text="Employee role/position"
    )
    
    employment_status = models.CharField(
        max_length=15,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active',
        help_text="Current employment status"
    )
    
    hire_date = models.DateField(
        help_text="Date when employee was hired"
    )
    
    termination_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when employment ended (if applicable)"
    )
    
    hourly_wage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Hourly wage rate"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this employee"
    )
    
    can_open = models.BooleanField(
        default=False,
        help_text="Employee is authorized to open the store"
    )
    
    can_close = models.BooleanField(
        default=False,
        help_text="Employee is authorized to close the store"
    )
    
    can_handle_cash = models.BooleanField(
        default=True,
        help_text="Employee is authorized to handle cash transactions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate employee ID if not provided"""
        if not self.employee_id:
            # Generate employee ID: EMP + hire year + sequence number
            year = self.hire_date.year if self.hire_date else timezone.now().year
            last_emp = Employee.objects.filter(
                employee_id__startswith=f'EMP{year}'
            ).order_by('employee_id').last()
            
            if last_emp:
                try:
                    last_num = int(last_emp.employee_id[-3:])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.employee_id = f'EMP{year}{new_num:03d}'
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate employee data"""
        if self.termination_date and self.hire_date:
            if self.termination_date < self.hire_date:
                raise ValidationError("Termination date cannot be before hire date")
        
        if self.employment_status == 'terminated' and not self.termination_date:
            raise ValidationError("Termination date is required when status is 'terminated'")
    
    @property
    def is_active(self):
        """Check if employee is currently active"""
        return self.employment_status == 'active'
    
    @property
    def years_of_service(self):
        """Calculate years of service"""
        end_date = self.termination_date or timezone.now().date()
        return (end_date - self.hire_date).days / 365.25
    
    @property
    def can_supervise(self):
        """Check if employee can supervise (manager or owner)"""
        return self.role in ['owner', 'manager', 'shift_lead']


class Schedule(models.Model):
    """
    Work schedules for employees
    """
    SHIFT_TYPE_CHOICES = [
        ('opening', 'Opening Shift'),
        ('mid', 'Mid Shift'),
        ('closing', 'Closing Shift'),
        ('full', 'Full Day'),
        ('split', 'Split Shift'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('called_in_sick', 'Called In Sick'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        help_text="Employee assigned to this shift"
    )
    
    date = models.DateField(
        help_text="Date of the scheduled shift"
    )
    
    start_time = models.TimeField(
        help_text="Shift start time"
    )
    
    end_time = models.TimeField(
        help_text="Shift end time"
    )
    
    break_duration = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Break duration in minutes"
    )
    
    shift_type = models.CharField(
        max_length=10,
        choices=SHIFT_TYPE_CHOICES,
        default='mid',
        help_text="Type of shift"
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='scheduled',
        help_text="Current status of this shift"
    )
    
    actual_start_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Actual time employee started (if different from scheduled)"
    )
    
    actual_end_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Actual time employee finished (if different from scheduled)"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes about this shift"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules',
        help_text="Who created this schedule entry"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        ordering = ['date', 'start_time']
        unique_together = ['employee', 'date', 'start_time']
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.date} ({self.start_time}-{self.end_time})"
    
    def clean(self):
        """Validate schedule data"""
        if self.start_time and self.end_time:
            # Handle overnight shifts
            if self.start_time >= self.end_time:
                # Assume it's an overnight shift
                pass
            
            # Check for overlapping shifts for the same employee
            overlapping = Schedule.objects.filter(
                employee=self.employee,
                date=self.date
            ).exclude(pk=self.pk)
            
            for shift in overlapping:
                if (self.start_time < shift.end_time and self.end_time > shift.start_time):
                    raise ValidationError(
                        f"This shift overlaps with existing shift: {shift.start_time}-{shift.end_time}"
                    )
        
        # Check if employee has required permissions for opening/closing shifts
        if self.shift_type == 'opening' and not self.employee.can_open:
            raise ValidationError(f"{self.employee.user.get_full_name()} is not authorized to work opening shifts")
        
        if self.shift_type == 'closing' and not self.employee.can_close:
            raise ValidationError(f"{self.employee.user.get_full_name()} is not authorized to work closing shifts")
    
    @property
    def scheduled_hours(self):
        """Calculate scheduled hours for this shift"""
        if not self.start_time or not self.end_time:
            return 0
        
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time)
        
        # Handle overnight shifts
        if self.end_time <= self.start_time:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        hours = duration.total_seconds() / 3600
        
        # Subtract break time
        break_hours = self.break_duration / 60
        return max(0, hours - break_hours)
    
    @property
    def actual_hours(self):
        """Calculate actual hours worked (if recorded)"""
        if not self.actual_start_time or not self.actual_end_time:
            return self.scheduled_hours
        
        start_datetime = datetime.combine(self.date, self.actual_start_time)
        end_datetime = datetime.combine(self.date, self.actual_end_time)
        
        # Handle overnight shifts
        if self.actual_end_time <= self.actual_start_time:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        hours = duration.total_seconds() / 3600
        
        # Subtract break time
        break_hours = self.break_duration / 60
        return max(0, hours - break_hours)
    
    @property
    def is_overtime(self):
        """Check if this shift puts employee over 8 hours for the day"""
        # Get all shifts for this employee on this date
        day_shifts = Schedule.objects.filter(
            employee=self.employee,
            date=self.date,
            status__in=['scheduled', 'confirmed', 'completed']
        )
        
        total_hours = sum(shift.scheduled_hours for shift in day_shifts)
        return total_hours > 8
    
    @property
    def wage_earned(self):
        """Calculate wages earned for this shift"""
        hours = self.actual_hours if self.status == 'completed' else self.scheduled_hours
        return hours * float(self.employee.hourly_wage)