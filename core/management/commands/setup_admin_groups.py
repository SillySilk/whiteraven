from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import BusinessInfo, ContactSubmission
from menu.models import MenuItem, Category, Recipe
from staff.models import Employee, Schedule


class Command(BaseCommand):
    help = 'Set up admin user groups and permissions for White Raven Pourhouse'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up admin groups and permissions...'))

        # Create groups
        owner_group, created = Group.objects.get_or_create(name='Owner')
        manager_group, created = Group.objects.get_or_create(name='Manager')
        shift_lead_group, created = Group.objects.get_or_create(name='Shift Lead')
        staff_group, created = Group.objects.get_or_create(name='Staff')

        # Get content types
        business_ct = ContentType.objects.get_for_model(BusinessInfo)
        contact_ct = ContentType.objects.get_for_model(ContactSubmission)
        menuitem_ct = ContentType.objects.get_for_model(MenuItem)
        category_ct = ContentType.objects.get_for_model(Category)
        recipe_ct = ContentType.objects.get_for_model(Recipe)
        employee_ct = ContentType.objects.get_for_model(Employee)
        schedule_ct = ContentType.objects.get_for_model(Schedule)

        # Owner permissions (full access)
        owner_permissions = [
            # Business Info
            Permission.objects.get(content_type=business_ct, codename='view_businessinfo'),
            Permission.objects.get(content_type=business_ct, codename='change_businessinfo'),
            
            # Contact Submissions
            Permission.objects.get(content_type=contact_ct, codename='view_contactsubmission'),
            Permission.objects.get(content_type=contact_ct, codename='change_contactsubmission'),
            Permission.objects.get(content_type=contact_ct, codename='delete_contactsubmission'),
            
            # Menu Management
            Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='add_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='change_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='delete_menuitem'),
            
            Permission.objects.get(content_type=category_ct, codename='view_category'),
            Permission.objects.get(content_type=category_ct, codename='add_category'),
            Permission.objects.get(content_type=category_ct, codename='change_category'),
            Permission.objects.get(content_type=category_ct, codename='delete_category'),
            
            Permission.objects.get(content_type=recipe_ct, codename='view_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='add_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='change_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='delete_recipe'),
            
            # Staff Management
            Permission.objects.get(content_type=employee_ct, codename='view_employee'),
            Permission.objects.get(content_type=employee_ct, codename='add_employee'),
            Permission.objects.get(content_type=employee_ct, codename='change_employee'),
            Permission.objects.get(content_type=employee_ct, codename='delete_employee'),
            
            Permission.objects.get(content_type=schedule_ct, codename='view_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='add_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='change_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='delete_schedule'),
        ]

        # Manager permissions (most access except business info and employee deletion)
        manager_permissions = [
            # Contact Submissions
            Permission.objects.get(content_type=contact_ct, codename='view_contactsubmission'),
            Permission.objects.get(content_type=contact_ct, codename='change_contactsubmission'),
            
            # Menu Management
            Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='add_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='change_menuitem'),
            Permission.objects.get(content_type=menuitem_ct, codename='delete_menuitem'),
            
            Permission.objects.get(content_type=category_ct, codename='view_category'),
            Permission.objects.get(content_type=category_ct, codename='add_category'),
            Permission.objects.get(content_type=category_ct, codename='change_category'),
            
            Permission.objects.get(content_type=recipe_ct, codename='view_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='add_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='change_recipe'),
            Permission.objects.get(content_type=recipe_ct, codename='delete_recipe'),
            
            # Staff Management (limited)
            Permission.objects.get(content_type=employee_ct, codename='view_employee'),
            Permission.objects.get(content_type=employee_ct, codename='change_employee'),
            
            Permission.objects.get(content_type=schedule_ct, codename='view_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='add_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='change_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='delete_schedule'),
        ]

        # Shift Lead permissions (schedule management and menu viewing)
        shift_lead_permissions = [
            # Menu viewing only
            Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
            Permission.objects.get(content_type=category_ct, codename='view_category'),
            Permission.objects.get(content_type=recipe_ct, codename='view_recipe'),
            
            # Staff viewing and limited schedule management
            Permission.objects.get(content_type=employee_ct, codename='view_employee'),
            
            Permission.objects.get(content_type=schedule_ct, codename='view_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='add_schedule'),
            Permission.objects.get(content_type=schedule_ct, codename='change_schedule'),
        ]

        # Staff permissions (very limited, mainly viewing)
        staff_permissions = [
            # Menu viewing only
            Permission.objects.get(content_type=menuitem_ct, codename='view_menuitem'),
            Permission.objects.get(content_type=recipe_ct, codename='view_recipe'),
            
            # Own schedule viewing only
            Permission.objects.get(content_type=schedule_ct, codename='view_schedule'),
        ]

        # Assign permissions to groups
        owner_group.permissions.set(owner_permissions)
        manager_group.permissions.set(manager_permissions)
        shift_lead_group.permissions.set(shift_lead_permissions)
        staff_group.permissions.set(staff_permissions)

        self.stdout.write(
            self.style.SUCCESS('Successfully set up admin groups:')
        )
        self.stdout.write(f'  - Owner: {len(owner_permissions)} permissions')
        self.stdout.write(f'  - Manager: {len(manager_permissions)} permissions')
        self.stdout.write(f'  - Shift Lead: {len(shift_lead_permissions)} permissions')
        self.stdout.write(f'  - Staff: {len(staff_permissions)} permissions')

        self.stdout.write(
            self.style.WARNING(
                '\nNote: Assign users to appropriate groups in the Django admin interface.'
            )
        )