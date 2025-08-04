# White Raven Pourhouse - Admin User Guide

This guide helps Rose Woolf and authorized staff manage the White Raven Pourhouse website through the Django admin interface.

## Getting Started

### Admin Access
- **URL**: `https://yoursite.com/admin/`
- **Rose's Login**: `rose_owner` / `rose123!`
- **General Admin**: `admin` / `admin123!`

### First Login
1. Go to the admin URL in your web browser
2. Enter your username and password
3. Click "Log in"
4. You'll see the White Raven admin dashboard

## Managing Business Information

### Updating Business Details
1. Click **Business Information** on the admin home page
2. Click the business info entry (there should only be one)
3. Update any of the following:
   - **Name**: Business name (usually "White Raven Pourhouse")
   - **Tagline**: Your slogan ("The Best Little Pour House in Felton")
   - **Address**: Full street address
   - **Phone**: Contact phone number
   - **Email**: Business email address
   - **Instagram Handle**: Just the username (without @)
   - **Description**: Homepage description text

### Managing Business Hours
The hours are stored in a special format. Here's how to update them:

**Regular Hours Format:**
```
{
  "monday": {"open": "07:00", "close": "19:00", "closed": false},
  "tuesday": {"open": "07:00", "close": "19:00", "closed": false},
  "wednesday": {"open": "07:00", "close": "19:00", "closed": false},
  "thursday": {"open": "07:00", "close": "19:00", "closed": false},
  "friday": {"open": "07:00", "close": "20:00", "closed": false},
  "saturday": {"open": "08:00", "close": "20:00", "closed": false},
  "sunday": {"open": "08:00", "close": "18:00", "closed": false}
}
```

**Special Hours Format (holidays, etc.):**
```
{
  "2024-12-25": {"closed": true, "note": "Christmas Day - Closed"},
  "2024-12-31": {"open": "08:00", "close": "16:00", "note": "New Year's Eve - Limited Hours"}
}
```

## Managing the Menu

### Menu Categories
1. Go to **Menu** → **Categories**
2. **To add a new category:**
   - Click "Add category"
   - Enter name (e.g., "Seasonal Drinks")
   - Add description
   - Set order number (lower numbers appear first)
   - Check "Active" to make it visible
   - Click "Save"

3. **To edit a category:**
   - Click on the category name
   - Make changes and click "Save"

### Menu Items
1. Go to **Menu** → **Menu items**
2. **To add a new menu item:**
   - Click "Add menu item"
   - Fill in the required fields:
     - **Name**: Item name (e.g., "Vanilla Latte")
     - **Description**: Detailed description for customers
     - **Price**: In dollars (e.g., 5.25)
     - **Category**: Select from dropdown
     - **Available**: Check to show on public menu
     - **Featured**: Check to highlight on homepage
     - **Image**: Upload a photo (optional)
     - **Temperature**: Hot, Cold, Both, or Room temperature
     - **Size**: Small, Medium, Large, etc.
     - **Contains caffeine**: Check if applicable
     - **Dietary notes**: Vegan, gluten-free, etc.
     - **Preparation time**: Minutes needed to make
   - Click "Save"

3. **To edit a menu item:**
   - Click on the item name
   - Make changes and click "Save"

4. **To remove an item temporarily:**
   - Edit the item and uncheck "Available"
   - This hides it from customers but keeps it in your system

### Menu Item Images
- **Recommended size**: At least 400×300 pixels
- **File formats**: JPEG, PNG, WebP
- **File size**: Under 5MB
- **Tips**: Use well-lit, appetizing photos that show the item clearly

### Recipes (Staff Instructions)
1. Go to **Menu** → **Recipes**
2. **To add preparation instructions:**
   - Click "Add recipe"
   - Select the menu item
   - List ingredients (one per line)
   - Write step-by-step instructions
   - Set preparation time and difficulty
   - Add equipment needed and notes
   - Click "Save"

## Managing Staff

### Employee Records
1. Go to **Staff** → **Employees**
2. **To add a new employee:**
   - First create their user account in **Authentication** → **Users**
   - Then go back to **Staff** → **Employees** and click "Add employee"
   - Link to their user account
   - Fill in phone, emergency contact, role, wages, etc.
   - Set permissions (can open, close, handle cash)
   - Click "Save"

### Work Schedules
1. Go to **Staff** → **Schedules**
2. **To create a schedule:**
   - Click "Add schedule"
   - Select employee and date
   - Set start and end times
   - Choose shift type (opening, mid, closing)
   - Set break duration
   - Add any notes
   - Click "Save"

## Managing Customer Messages

### Contact Form Submissions
1. Go to **Core** → **Contact submissions**
2. **To view messages:**
   - Click on any submission to read the full message
   - Check "Responded" when you've replied to the customer
   - Add response notes for your records

2. **To reply to customers:**
   - Note their email address
   - Send your reply through your regular email
   - Mark the submission as "Responded" in the admin

## User Management

### Creating New Admin Users
1. Go to **Authentication** → **Users**
2. Click "Add user"
3. Enter username and password
4. Click "Save and continue editing"
5. Fill in first name, last name, email
6. For admin access, check:
   - **Staff status**: Can access admin
   - **Superuser status**: Full admin privileges (use carefully)
7. Click "Save"

### Password Changes
1. Go to **Authentication** → **Users**
2. Click on the user
3. Click "Change password" link
4. Enter new password twice
5. Click "Change password"

## Quick Reference

### Daily Tasks
- [ ] Check contact form submissions
- [ ] Review any new orders or inquiries
- [ ] Update menu item availability if needed

### Weekly Tasks
- [ ] Review staff schedules
- [ ] Check for any needed menu updates
- [ ] Review business hours for upcoming holidays

### Monthly Tasks
- [ ] Update seasonal menu items
- [ ] Review staff information and wages
- [ ] Check business information accuracy

## Common Tasks

### Making a Menu Item "Sold Out"
1. Go to **Menu** → **Menu items**
2. Find the item and click on it
3. Uncheck "Available"
4. Click "Save"
(Customers won't see it, but you can make it available again anytime)

### Adding Holiday Hours
1. Go to **Business Information**
2. Click on your business info
3. In the "Special hours" field, add:
```
{
  "2024-12-25": {"closed": true, "note": "Christmas Day - Closed"}
}
```
4. Click "Save"

### Featuring an Item on the Homepage
1. Go to **Menu** → **Menu items**
2. Find the item and click on it
3. Check "Featured"
4. Click "Save"
(The item will appear in the featured section on your homepage)

## Getting Help

### If Something Goes Wrong
1. Don't panic - you can always undo changes
2. Check the error message for clues
3. Try logging out and back in
4. Contact your technical support

### Backup Reminder
The system automatically backs up your data, but it's good practice to:
- Save important changes immediately
- Test major changes on a quiet day first
- Keep a record of your admin passwords in a safe place

## Tips for Success

1. **Update regularly**: Keep your menu and hours current
2. **Use good photos**: High-quality images increase sales
3. **Write clear descriptions**: Help customers understand what they're ordering
4. **Monitor contact forms**: Respond to customer inquiries promptly
5. **Train your staff**: Make sure employees who need admin access are properly trained

---

*This admin system helps you run White Raven Pourhouse efficiently. Take your time learning it, and don't hesitate to ask for help when needed!*