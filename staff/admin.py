from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Employee, Schedule, EmployeeAvailability, ShiftSwapRequest, ScheduleTemplate, ScheduleTemplateItem


class EmployeeInline(admin.StackedInline):
    """
    Inline admin for employee information within User admin
    """
    model = Employee
    extra = 0
    can_delete = False
    verbose_name_plural = 'Employee Information'
    
    fieldsets = (
        ('Employee Details', {
            'fields': ('employee_id', 'role', 'employment_status')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Employment Information', {
            'fields': ('hire_date', 'termination_date', 'hourly_wage')
        }),
        ('Permissions', {
            'fields': ('can_open', 'can_close', 'can_handle_cash')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('employee_id',)


class UserAdmin(BaseUserAdmin):
    """
    Extend the default User admin to include employee information
    """
    inlines = (EmployeeInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


class ScheduleInline(admin.TabularInline):
    """
    Inline admin for schedules within employee admin
    """
    model = Schedule
    extra = 0
    fields = ('date', 'start_time', 'end_time', 'shift_type', 'status', 'break_duration')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Only show upcoming schedules by default"""
        qs = super().get_queryset(request)
        # Show schedules for the next 30 days
        future_date = datetime.now().date() + timedelta(days=30)
        return qs.filter(date__gte=datetime.now().date(), date__lte=future_date)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for employee management
    """
    list_display = (
        'employee_display_name',
        'employee_id', 
        'role', 
        'employment_status',
        'hire_date',
        'years_of_service_display',
        'permissions_display',
        'wage_display'
    )
    
    list_filter = (
        'role', 
        'employment_status',
        'hire_date',
        'can_open',
        'can_close',
        'can_handle_cash'
    )
    
    search_fields = (
        'user__first_name', 
        'user__last_name', 
        'user__username',
        'employee_id',
        'phone'
    )
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Employee Information', {
            'fields': ('employee_id', 'role', 'employment_status')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'termination_date', 'hourly_wage')
        }),
        ('Permissions & Capabilities', {
            'fields': ('can_open', 'can_close', 'can_handle_cash')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('employee_id', 'created_at', 'updated_at')
    
    inlines = [ScheduleInline]
    
    # Bulk actions
    actions = ['activate_employees', 'deactivate_employees', 'export_employee_list', 'generate_payroll_report']
    
    def employee_display_name(self, obj):
        """Display employee name with link to user admin"""
        name = obj.user.get_full_name() or obj.user.username
        user_url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', user_url, name)
    employee_display_name.short_description = 'Name'
    employee_display_name.admin_order_field = 'user__last_name'
    
    def years_of_service_display(self, obj):
        """Display years of service with color coding"""
        years = obj.years_of_service
        if years < 1:
            color = '#ff6b6b'  # Red for new employees
            text = f'{years:.1f} years (New)'
        elif years < 3:
            color = '#4ecdc4'  # Teal for experienced
            text = f'{years:.1f} years'
        else:
            color = '#45b7d1'  # Blue for veterans
            text = f'{years:.1f} years (Veteran)'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    years_of_service_display.short_description = 'Service'
    
    def permissions_display(self, obj):
        """Display permissions as badges"""
        badges = []
        if obj.can_open:
            badges.append('<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">OPEN</span>')
        if obj.can_close:
            badges.append('<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">CLOSE</span>')
        if obj.can_handle_cash:
            badges.append('<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">CASH</span>')
        
        return format_html(' '.join(badges)) if badges else '-'
    permissions_display.short_description = 'Permissions'
    
    def wage_display(self, obj):
        """Display hourly wage"""
        return f'${obj.hourly_wage:.2f}/hr'
    wage_display.short_description = 'Wage'
    wage_display.admin_order_field = 'hourly_wage'
    
    def activate_employees(self, request, queryset):
        """Bulk action to activate employees"""
        updated = queryset.update(employment_status='active')
        self.message_user(request, f'{updated} employees activated.')
    activate_employees.short_description = "Activate selected employees"
    
    def deactivate_employees(self, request, queryset):
        """Bulk action to deactivate employees"""
        updated = queryset.update(employment_status='inactive')
        self.message_user(request, f'{updated} employees deactivated.')
    deactivate_employees.short_description = "Deactivate selected employees"
    
    def export_employee_list(self, request, queryset):
        """Export employee list to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employee_list.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'Name', 'Role', 'Status', 'Hire Date', 'Hourly Wage', 'Phone', 'Can Open', 'Can Close', 'Can Handle Cash'])
        
        for employee in queryset:
            writer.writerow([
                employee.employee_id,
                employee.user.get_full_name() or employee.user.username,
                employee.get_role_display(),
                employee.get_employment_status_display(),
                employee.hire_date.strftime('%Y-%m-%d'),
                f'${employee.hourly_wage:.2f}',
                employee.phone,
                'Yes' if employee.can_open else 'No',
                'Yes' if employee.can_close else 'No',
                'Yes' if employee.can_handle_cash else 'No',
            ])
        
        return response
    export_employee_list.short_description = "Export selected employees to CSV"
    
    def generate_payroll_report(self, request, queryset):
        """Generate payroll report for selected employees"""
        import csv
        from django.http import HttpResponse
        from datetime import datetime, timedelta
        
        # Get current week
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payroll_report_{week_start}_to_{week_end}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Employee ID', 'Name', 'Role', 'Hours Worked', 'Hourly Wage', 'Total Wages', 'Overtime Hours', 'Overtime Pay'])
        
        for employee in queryset:
            # Get schedules for this week
            week_schedules = Schedule.objects.filter(
                employee=employee,
                date__gte=week_start,
                date__lte=week_end,
                status='completed'
            )
            
            total_hours = sum(schedule.actual_hours for schedule in week_schedules)
            regular_hours = min(total_hours, 40)
            overtime_hours = max(0, total_hours - 40)
            
            regular_pay = regular_hours * float(employee.hourly_wage)
            overtime_pay = overtime_hours * float(employee.hourly_wage) * 1.5
            total_pay = regular_pay + overtime_pay
            
            writer.writerow([
                employee.employee_id,
                employee.user.get_full_name() or employee.user.username,
                employee.get_role_display(),
                f'{total_hours:.2f}',
                f'${employee.hourly_wage:.2f}',
                f'${total_pay:.2f}',
                f'{overtime_hours:.2f}',
                f'${overtime_pay:.2f}',
            ])
        
        return response
    generate_payroll_report.short_description = "Generate payroll report for selected employees"
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('user')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for schedule management
    """
    list_display = (
        'employee_name',
        'date',
        'shift_time_display',
        'shift_type',
        'status',
        'hours_display',
        'wage_display'
    )
    
    list_filter = (
        'date',
        'shift_type',
        'status',
        'employee__role',
        'employee__employment_status'
    )
    
    search_fields = (
        'employee__user__first_name',
        'employee__user__last_name',
        'employee__employee_id'
    )
    
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Schedule Details', {
            'fields': ('employee', 'date', 'shift_type')
        }),
        ('Time Information', {
            'fields': ('start_time', 'end_time', 'break_duration')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'actual_start_time', 'actual_end_time')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Administration', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Bulk actions
    actions = ['mark_completed', 'mark_confirmed', 'duplicate_schedule', 'export_schedule_report']
    
    def employee_name(self, obj):
        """Display employee name with link"""
        name = obj.employee.user.get_full_name() or obj.employee.user.username
        emp_url = reverse('admin:staff_employee_change', args=[obj.employee.pk])
        return format_html('<a href="{}">{}</a>', emp_url, name)
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__user__last_name'
    
    def shift_time_display(self, obj):
        """Display shift time with duration"""
        hours = obj.scheduled_hours
        return f'{obj.start_time} - {obj.end_time} ({hours:.1f}h)'
    shift_time_display.short_description = 'Shift Time'
    
    def hours_display(self, obj):
        """Display scheduled vs actual hours"""
        scheduled = obj.scheduled_hours
        actual = obj.actual_hours
        
        if obj.status == 'completed' and actual != scheduled:
            diff = actual - scheduled
            color = '#28a745' if diff > 0 else '#dc3545'
            return format_html(
                '{:.1f}h <span style="color: {};">({:+.1f})</span>',
                actual, color, diff
            )
        return f'{scheduled:.1f}h'
    hours_display.short_description = 'Hours'
    
    def wage_display(self, obj):
        """Display calculated wages for this shift"""
        wages = obj.wage_earned
        if obj.is_overtime:
            return format_html(
                '<span style="color: #ff6b6b; font-weight: bold;">${:.2f} (OT)</span>',
                wages
            )
        return f'${wages:.2f}'
    wage_display.short_description = 'Wages'
    
    def mark_completed(self, request, queryset):
        """Bulk action to mark schedules as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} schedules marked as completed.')
    mark_completed.short_description = "Mark selected schedules as completed"
    
    def mark_confirmed(self, request, queryset):
        """Bulk action to mark schedules as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} schedules marked as confirmed.')
    mark_confirmed.short_description = "Mark selected schedules as confirmed"
    
    def duplicate_schedule(self, request, queryset):
        """Duplicate selected schedules for next week"""
        from datetime import timedelta
        
        duplicated = 0
        for schedule in queryset:
            new_date = schedule.date + timedelta(days=7)
            
            # Check if schedule already exists for this employee on the new date
            existing = Schedule.objects.filter(
                employee=schedule.employee,
                date=new_date,
                start_time=schedule.start_time
            ).exists()
            
            if not existing:
                Schedule.objects.create(
                    employee=schedule.employee,
                    date=new_date,
                    start_time=schedule.start_time,
                    end_time=schedule.end_time,
                    break_duration=schedule.break_duration,
                    shift_type=schedule.shift_type,
                    status='scheduled',
                    notes=f'Duplicated from {schedule.date}',
                    created_by=request.user
                )
                duplicated += 1
        
        self.message_user(request, f'{duplicated} schedules duplicated for next week.')
    duplicate_schedule.short_description = "Duplicate selected schedules for next week"
    
    def export_schedule_report(self, request, queryset):
        """Export schedule report to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="schedule_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Employee', 'Role', 'Shift Type', 'Start Time', 'End Time', 'Hours', 'Status', 'Wages'])
        
        total_hours = 0
        total_wages = 0
        
        for schedule in queryset.order_by('date', 'start_time'):
            hours = schedule.actual_hours if schedule.status == 'completed' else schedule.scheduled_hours
            wages = schedule.wage_earned
            
            total_hours += hours
            total_wages += wages
            
            writer.writerow([
                schedule.date.strftime('%Y-%m-%d'),
                schedule.employee.user.get_full_name() or schedule.employee.user.username,
                schedule.employee.get_role_display(),
                schedule.get_shift_type_display(),
                schedule.start_time.strftime('%H:%M'),
                schedule.end_time.strftime('%H:%M'),
                f'{hours:.2f}',
                schedule.get_status_display(),
                f'${wages:.2f}',
            ])
        
        # Add totals row
        writer.writerow([])
        writer.writerow(['TOTALS', '', '', '', '', '', f'{total_hours:.2f}', '', f'${total_wages:.2f}'])
        
        return response
    export_schedule_report.short_description = "Export selected schedules to CSV"
    
    def save_model(self, request, obj, form, change):
        """Auto-set created_by field"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Optimize queryset and show recent schedules by default"""
        qs = super().get_queryset(request).select_related('employee__user')
        # Show schedules from 7 days ago to 30 days in the future by default
        if not request.GET.get('date__gte') and not request.GET.get('date__lte'):
            start_date = datetime.now().date() - timedelta(days=7)
            end_date = datetime.now().date() + timedelta(days=30)
            qs = qs.filter(date__gte=start_date, date__lte=end_date)
        return qs


class AvailabilityInline(admin.TabularInline):
    """
    Inline admin for employee availability preferences
    """
    model = EmployeeAvailability
    extra = 0
    fields = ('weekday', 'availability_type', 'start_time', 'end_time', 'notes', 'is_active')
    
    def get_queryset(self, request):
        """Order by weekday"""
        return super().get_queryset(request).order_by('weekday')


@admin.register(EmployeeAvailability)
class EmployeeAvailabilityAdmin(admin.ModelAdmin):
    """
    Admin interface for employee availability tracking
    """
    list_display = (
        'employee_name',
        'weekday_display',
        'availability_type',
        'time_range_display',
        'is_active'
    )
    
    list_filter = (
        'weekday',
        'availability_type',
        'is_active',
        'employee__role'
    )
    
    search_fields = (
        'employee__user__first_name',
        'employee__user__last_name',
        'notes'
    )
    
    fieldsets = (
        ('Employee & Day', {
            'fields': ('employee', 'weekday', 'is_active')
        }),
        ('Availability Details', {
            'fields': ('availability_type', 'start_time', 'end_time')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        """Display employee name with link"""
        name = obj.employee.user.get_full_name() or obj.employee.user.username
        emp_url = reverse('admin:staff_employee_change', args=[obj.employee.pk])
        return format_html('<a href="{}">{}</a>', emp_url, name)
    employee_name.short_description = 'Employee'
    employee_name.admin_order_field = 'employee__user__last_name'
    
    def weekday_display(self, obj):
        """Display weekday with color coding"""
        day_name = obj.get_weekday_display()
        colors = {
            'Saturday': '#ff6b6b',  # Red for weekend
            'Sunday': '#ff6b6b',    # Red for weekend
        }
        color = colors.get(day_name, '#4ecdc4')  # Default teal
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, day_name
        )
    weekday_display.short_description = 'Day'
    
    def time_range_display(self, obj):
        """Display time range with availability type"""
        if obj.availability_type == 'unavailable':
            return format_html('<span style="color: #dc3545;">Unavailable</span>')
        elif obj.start_time and obj.end_time:
            color = '#28a745' if obj.availability_type == 'preferred' else '#17a2b8'
            return format_html(
                '<span style="color: {};">{} - {}</span>',
                color, obj.start_time.strftime('%H:%M'), obj.end_time.strftime('%H:%M')
            )
        return '-'
    time_range_display.short_description = 'Available Times'


@admin.register(ShiftSwapRequest)
class ShiftSwapRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for shift swap requests
    """
    list_display = (
        'swap_summary',
        'shift_date',
        'status_display',
        'created_at',
        'action_buttons'
    )
    
    list_filter = (
        'status',
        'created_at',
        'original_shift__date',
        'requester__role'
    )
    
    search_fields = (
        'requester__user__first_name',
        'requester__user__last_name',
        'receiver__user__first_name',
        'receiver__user__last_name',
        'reason'
    )
    
    fieldsets = (
        ('Swap Details', {
            'fields': ('requester', 'receiver', 'original_shift', 'return_shift')
        }),
        ('Request Information', {
            'fields': ('reason', 'status')
        }),
        ('Manager Approval', {
            'fields': ('manager_notes', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('approved_at', 'created_at', 'updated_at')
    
    actions = ['approve_swaps', 'deny_swaps']
    
    def swap_summary(self, obj):
        """Display swap summary"""
        requester = obj.requester.user.get_full_name() or obj.requester.user.username
        receiver = obj.receiver.user.get_full_name() or obj.receiver.user.username
        return f"{requester} → {receiver}"
    swap_summary.short_description = 'Swap Request'
    
    def shift_date(self, obj):
        """Display shift date and time"""
        shift = obj.original_shift
        return f"{shift.date} ({shift.start_time}-{shift.end_time})"
    shift_date.short_description = 'Shift'
    shift_date.admin_order_field = 'original_shift__date'
    
    def status_display(self, obj):
        """Display status with color coding"""
        status_colors = {
            'pending': '#ffc107',
            'approved_by_receiver': '#17a2b8',
            'approved_by_manager': '#28a745',
            'completed': '#6c757d',
            'denied': '#dc3545',
            'cancelled': '#6c757d'
        }
        color = status_colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def action_buttons(self, obj):
        """Display action buttons for pending requests"""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="?action=approve&id={}">Approve</a> '
                '<a class="button" href="?action=deny&id={}">Deny</a>',
                obj.pk, obj.pk
            )
        return '-'
    action_buttons.short_description = 'Actions'
    
    def approve_swaps(self, request, queryset):
        """Bulk action to approve swap requests"""
        updated = 0
        for swap in queryset.filter(status='pending'):
            swap.status = 'approved_by_manager'
            swap.approved_by = request.user
            swap.approved_at = timezone.now()
            swap.save()
            updated += 1
        
        self.message_user(request, f'{updated} swap requests approved.')
    approve_swaps.short_description = "Approve selected swap requests"
    
    def deny_swaps(self, request, queryset):
        """Bulk action to deny swap requests"""
        updated = queryset.filter(status='pending').update(status='denied')
        self.message_user(request, f'{updated} swap requests denied.')
    deny_swaps.short_description = "Deny selected swap requests"


class ScheduleTemplateItemInline(admin.TabularInline):
    """
    Inline admin for schedule template items
    """
    model = ScheduleTemplateItem
    extra = 0
    fields = ('weekday', 'role', 'shift_type', 'start_time', 'end_time', 'break_duration', 'notes')
    ordering = ('weekday', 'start_time')


@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for schedule templates
    """
    list_display = (
        'name',
        'template_type',
        'shift_count',
        'is_active',
        'created_by',
        'created_at'
    )
    
    list_filter = (
        'template_type',
        'is_active',
        'created_at'
    )
    
    search_fields = (
        'name',
        'description'
    )
    
    fieldsets = (
        ('Template Details', {
            'fields': ('name', 'template_type', 'description', 'is_active')
        }),
        ('Administration', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    
    inlines = [ScheduleTemplateItemInline]
    
    actions = ['duplicate_template', 'apply_template_to_week']
    
    def shift_count(self, obj):
        """Display number of shifts in template"""
        count = obj.template_items.count()
        return f"{count} shifts"
    shift_count.short_description = 'Shifts'
    
    def duplicate_template(self, request, queryset):
        """Duplicate selected templates"""
        for template in queryset:
            # Create copy
            new_template = ScheduleTemplate.objects.create(
                name=f"{template.name} (Copy)",
                template_type=template.template_type,
                description=template.description,
                created_by=request.user
            )
            
            # Copy all template items
            for item in template.template_items.all():
                ScheduleTemplateItem.objects.create(
                    template=new_template,
                    weekday=item.weekday,
                    role=item.role,
                    shift_type=item.shift_type,
                    start_time=item.start_time,
                    end_time=item.end_time,
                    break_duration=item.break_duration,
                    notes=item.notes
                )
        
        self.message_user(request, f'{queryset.count()} templates duplicated.')
    duplicate_template.short_description = "Duplicate selected templates"
    
    def save_model(self, request, obj, form, change):
        """Auto-set created_by field"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Update Employee admin to include availability inline
EmployeeAdmin.inlines = [ScheduleInline, AvailabilityInline]


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Custom admin site configuration for better organization
class StaffAdminSite(admin.AdminSite):
    """Custom admin site for staff-specific administration"""
    site_header = "White Raven Staff Administration"
    site_title = "Staff Admin"
    index_title = "Staff Management"

# Create staff-specific admin site instance (optional)
staff_admin_site = StaffAdminSite(name='staff_admin')
