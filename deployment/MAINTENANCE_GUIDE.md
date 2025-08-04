# White Raven Pourhouse - Maintenance Guide

Quick reference for maintaining your PythonAnywhere deployment.

## Daily Operations

### Admin Tasks
- **Admin URL**: `https://yourusername.pythonanywhere.com/admin/`
- **Update Menu**: Core > Menu items > Add/Edit items
- **Check Messages**: Core > Contact submissions
- **Update Hours**: Core > Business infos > Edit hours

### Content Management
1. **Adding Menu Items**:
   - Go to Menu > Menu items > Add menu item
   - Upload high-quality images (will be automatically resized)
   - Set appropriate category and pricing
   - Check "Available" to display on website

2. **Managing Categories**:
   - Menu > Categories > Add/Edit categories
   - Use "Order" field to control display sequence

3. **Business Information**:
   - Core > Business infos > Edit main business info
   - Update hours, contact information, tagline

## Weekly Maintenance

### 1. Check Error Logs
```bash
# PythonAnywhere Bash Console
cd ~/white-raven-pourhouse
tail -f logs/white_raven.log
```

### 2. Review Contact Form Submissions
- Admin > Core > Contact submissions
- Respond to customer inquiries
- Archive old submissions

### 3. Backup Database
```bash
# PythonAnywhere Bash Console
mysqldump -u yourusername -p yourusername$whiteravenpourhouse > ~/backups/db_$(date +%Y%m%d).sql
```

## Monthly Maintenance

### 1. Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update specific packages (be cautious)
pip install --upgrade django
```

### 2. Security Checks
```bash
# Run security audit
python manage.py security_check

# Check for Django security updates
pip install --upgrade django
```

### 3. Clean Up Media Files
- Review uploaded images in Media > Menu
- Delete unused images to save space
- Optimize large images if needed

## Updates and Deployments

### Deploying Code Changes
```bash
# PythonAnywhere Bash Console
cd ~/white-raven-pourhouse
git pull origin main
source ~/.virtualenvs/white-raven-env/bin/activate
pip install -r requirements-production.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**Don't forget**: Reload your web app in PythonAnywhere dashboard after updates!

### Database Migrations
```bash
# Create migration (after model changes)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## Troubleshooting Common Issues

### Site Not Loading
1. Check error log in PythonAnywhere Web tab
2. Verify environment variables are set
3. Check WSGI configuration file
4. Ensure virtual environment is activated

### Admin Not Accessible
1. Verify superuser account exists:
   ```bash
   python manage.py createsuperuser
   ```
2. Check URL: `/admin/` (not `/admin`)
3. Clear browser cache and cookies

### Email Not Working
1. Test email configuration:
   ```bash
   python manage.py test_email
   ```
2. Check Gmail app password is correct
3. Verify EMAIL_* environment variables

### Static Files Not Loading
1. Check static files mapping in Web tab
2. Run collectstatic:
   ```bash
   python manage.py collectstatic --noinput
   ```
3. Verify STATIC_ROOT path is correct

### Images Not Uploading
1. Check media files mapping in Web tab
2. Verify MEDIA_ROOT permissions:
   ```bash
   ls -la ~/media/
   chmod 755 ~/media/ ~/media/menu/ ~/media/uploads/
   ```

## Performance Monitoring

### Database Performance
```sql
-- Check database size
SELECT 
    table_schema AS "Database",
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS "Size (MB)"
FROM information_schema.tables 
WHERE table_schema = "yourusername$whiteravenpourhouse"
GROUP BY table_schema;
```

### Log Analysis
```bash
# Check for errors in the last 24 hours
grep -i error logs/white_raven.log | tail -20

# Monitor contact form submissions
grep "Contact form submitted" logs/white_raven.log | wc -l
```

## Security Best Practices

### Regular Security Tasks
1. **Update Passwords**: Change admin passwords every 90 days
2. **Review Users**: Remove inactive admin users
3. **Check Permissions**: Verify file permissions are secure
4. **Monitor Logs**: Watch for suspicious activity

### Security Commands
```bash
# Check for security issues
python manage.py security_check

# Test file upload security
python manage.py test_upload_security
```

## Backup Procedures

### Database Backup
```bash
# Create backup
mkdir -p ~/backups
mysqldump -u yourusername -p yourusername$whiteravenpourhouse > ~/backups/db_$(date +%Y%m%d_%H%M).sql

# Verify backup
head -20 ~/backups/db_$(date +%Y%m%d_%H%M).sql
```

### Media Files Backup
```bash
# Create media backup
tar -czf ~/backups/media_$(date +%Y%m%d).tar.gz ~/media/

# Verify backup
tar -tzf ~/backups/media_$(date +%Y%m%d).tar.gz | head -10
```

### Environment Variables Backup
- Export environment variables from PythonAnywhere Web tab
- Store securely (not in version control)
- Update backup when variables change

## Contact Information Management

### Processing Contact Forms
1. **Daily**: Check for new submissions in Admin
2. **Respond**: Reply to customer inquiries promptly  
3. **Archive**: Move old submissions to archive folder
4. **Analytics**: Track common inquiry types

### Email Management
- Monitor bounce rates
- Update email templates as needed
- Test auto-reply functionality monthly

## Seasonal Tasks

### Quarterly
- Review and update menu items and pricing
- Check for Django LTS updates
- Review business information accuracy
- Backup configuration files

### Annually
- Renew domain registration (if using custom domain)
- Review hosting plan and upgrade if needed
- Conduct full security audit
- Update copyright dates in templates

## Emergency Procedures

### Site Down
1. Check PythonAnywhere status page
2. Review error logs immediately
3. Check recent deployments
4. Rollback if necessary:
   ```bash
   git revert HEAD
   # Redeploy
   ```

### Database Issues
1. Check database connection
2. Review recent migrations
3. Restore from backup if necessary:
   ```bash
   mysql -u yourusername -p yourusername$whiteravenpourhouse < ~/backups/db_YYYYMMDD.sql
   ```

### Security Breach
1. Change all passwords immediately
2. Review access logs
3. Update secret key
4. Check for unauthorized changes
5. Contact PythonAnywhere support if needed

## Support Resources

- **PythonAnywhere Help**: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)
- **Emergency Contact**: Use PythonAnywhere support ticket system

Remember: Always test changes in development before applying to production!