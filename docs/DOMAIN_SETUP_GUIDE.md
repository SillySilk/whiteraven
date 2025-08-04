# White Raven Pourhouse - Custom Domain Setup Guide

This guide walks you through setting up a custom domain (like `whiteravenpourhouse.com`) for your PythonAnywhere-hosted website.

## Prerequisites

- Active PythonAnywhere account with your website deployed
- Custom domain name purchased from a domain registrar (GoDaddy, Namecheap, etc.)
- Access to your domain's DNS settings

## Step 1: Configure Domain on PythonAnywhere

### 1.1 Access Web App Settings
1. Log in to your PythonAnywhere dashboard
2. Go to the **Web** tab
3. Click on your web app (e.g., `yourusername.pythonanywhere.com`)

### 1.2 Add Custom Domain
1. Scroll down to the **Domain name** section
2. Click **Add a new domain**
3. Enter your domain name (e.g., `whiteravenpourhouse.com`)
4. Click **Add domain**

### 1.3 Configure WWW Subdomain (Optional)
1. Add another domain entry for `www.whiteravenpourhouse.com`
2. This allows both `whiteravenpourhouse.com` and `www.whiteravenpourhouse.com` to work

## Step 2: Configure DNS Settings

### 2.1 Access Your Domain Registrar
1. Log in to your domain registrar (GoDaddy, Namecheap, etc.)
2. Find DNS management or DNS settings
3. Look for options to add/edit DNS records

### 2.2 Add CNAME Record
1. **Type**: CNAME
2. **Name/Host**: `www` (for www.whiteravenpourhouse.com)
3. **Value/Points to**: `yourusername.pythonanywhere.com`
4. **TTL**: 3600 (or default)

### 2.3 Add A Records for Root Domain
Since most registrars don't allow CNAME for root domains, use A records:

1. **Type**: A
2. **Name/Host**: `@` or leave blank (for whiteravenpourhouse.com)
3. **Value**: One of PythonAnywhere's IP addresses:
   - `35.184.189.133`
   - `35.188.30.25` 
   - `35.202.7.188`
4. **TTL**: 3600

*Note: Check PythonAnywhere's current IP addresses in their help docs as these may change.*

## Step 3: SSL Certificate Setup

### 3.1 Enable HTTPS
1. In your PythonAnywhere web app settings
2. Scroll to **HTTPS certificate** section
3. Click **Enable HTTPS** for your custom domain
4. PythonAnywhere will automatically get a Let's Encrypt certificate

### 3.2 Force HTTPS (Recommended)
1. Check **Force HTTPS** to redirect all HTTP traffic to HTTPS
2. This improves security and SEO

## Step 4: Update Django Settings

### 4.1 Update ALLOWED_HOSTS
In your `settings.py` file, update:
```python
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'whiteravenpourhouse.com',
    'www.whiteravenpourhouse.com'
]
```

### 4.2 Set CSRF Settings
```python
CSRF_TRUSTED_ORIGINS = [
    'https://whiteravenpourhouse.com',
    'https://www.whiteravenpourhouse.com'
]
```

## Step 5: Testing

### 5.1 DNS Propagation
1. DNS changes can take 24-48 hours to fully propagate
2. Test with online tools like `whatsmydns.net`
3. Try accessing your site from different locations/networks

### 5.2 Website Functionality
Test these URLs:
- `http://whiteravenpourhouse.com` (should redirect to HTTPS)
- `https://whiteravenpourhouse.com` (should work)
- `https://www.whiteravenpourhouse.com` (should work)
- `https://whiteravenpourhouse.com/admin/` (admin should work)

## Common Domain Registrars

### GoDaddy
1. Go to DNS Management
2. Add records in the DNS Records section
3. Type: CNAME, Name: www, Value: yourusername.pythonanywhere.com

### Namecheap
1. Go to Domain List → Manage → Advanced DNS
2. Add new record: CNAME, Host: www, Value: yourusername.pythonanywhere.com

### Cloudflare (if using)
1. Go to DNS settings
2. Add CNAME: www → yourusername.pythonanywhere.com
3. Set Proxy status to "DNS only" initially

## Troubleshooting

### Domain Not Working
- **Check DNS propagation**: Use tools like `nslookup` or online checkers
- **Verify CNAME/A records**: Make sure they point to correct addresses
- **Wait for propagation**: Can take up to 48 hours

### SSL Certificate Issues
- **Let's Encrypt failed**: Try again after DNS is fully propagated
- **Mixed content warnings**: Update any hardcoded HTTP links to HTTPS
- **Certificate not updating**: Contact PythonAnywhere support

### Django Settings Issues
- **ALLOWED_HOSTS error**: Make sure domain is in ALLOWED_HOSTS list
- **CSRF errors**: Add domain to CSRF_TRUSTED_ORIGINS
- **Static files not loading**: Update STATIC_URL and MEDIA_URL if needed

## Email Configuration (Optional)

### Professional Email Setup
Consider setting up professional email like `rose@whiteravenpourhouse.com`:

1. **Google Workspace**: Professional email with Gmail interface
2. **Domain registrar email**: Many offer basic email hosting
3. **Separate email provider**: Like ProtonMail or Zoho

### Update Contact Forms
Update your Django settings to use the professional email:
```python
DEFAULT_FROM_EMAIL = 'noreply@whiteravenpourhouse.com'
SERVER_EMAIL = 'server@whiteravenpourhouse.com'
```

## SEO Considerations

### Google Search Console
1. Add both `whiteravenpourhouse.com` and `www.whiteravenpourhouse.com`
2. Submit your sitemap
3. Monitor for crawl errors

### Google My Business
Update your website URL in Google My Business listing

### Social Media
Update website links on:
- Instagram (@whiteravenpourhouse)
- Facebook
- DoorDash profile
- Any other business listings

## Maintenance

### Certificate Renewal
- Let's Encrypt certificates auto-renew
- Monitor expiration in PythonAnywhere dashboard
- Contact support if renewal fails

### DNS Monitoring
- Periodically check that DNS settings haven't changed
- Monitor domain expiration dates
- Keep registrar account information updated

---

**Need Help?**
- PythonAnywhere Help: `help.pythonanywhere.com`
- Domain registrar support
- Your web developer or IT support

*Having a custom domain makes your coffee shop look professional and helps with branding and SEO!*