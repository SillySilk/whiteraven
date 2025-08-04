# Static Images Directory

This directory contains static images for the White Raven Pourhouse website.

## Required Images

### Logo and Branding
- `favicon.ico` - Website favicon (16x16, 32x32, 48x48 pixels)
- `logo.png` - Main logo for use in various contexts
- `logo-white.png` - White version of logo for dark backgrounds

### Hero and Background Images
- `coffee-hero-bg.jpg` - Main hero background image for homepage
- `about-bg.jpg` - Background image for about section
- `contact-bg.jpg` - Background image for contact page

### Menu and Food Images
- `coffee-default.jpg` - Default placeholder for coffee items
- `food-default.jpg` - Default placeholder for food items
- `menu-category-coffee.jpg` - Category header for coffee
- `menu-category-food.jpg` - Category header for food
- `menu-category-pastries.jpg` - Category header for pastries

### Location and Atmosphere
- `storefront.jpg` - Photo of the coffee house exterior
- `interior-1.jpg` - Interior atmosphere photo
- `interior-2.jpg` - Interior seating area photo
- `barista-at-work.jpg` - Action shot of coffee preparation

### Placeholder Images
- `placeholder-menu-item.jpg` - Generic placeholder for menu items
- `placeholder-staff.jpg` - Generic placeholder for staff photos

## Image Guidelines

- **Format**: Use JPEG for photos, PNG for logos with transparency
- **Size**: Optimize for web (under 500KB for hero images, under 200KB for menu items)
- **Dimensions**: 
  - Hero images: 1920x1080 (16:9 ratio)
  - Menu items: 400x300 (4:3 ratio)
  - Staff photos: 300x300 (square)
- **Alt text**: Always provide descriptive alt text for accessibility
- **Responsive**: Ensure images work well on all screen sizes

## Adding New Images

1. Place the image file in this directory
2. Reference it in templates using: `{% static 'images/filename.jpg' %}`
3. Add appropriate alt text for accessibility
4. Consider adding lazy loading for performance: `loading="lazy"`

## Optimization

Consider using tools like:
- TinyPNG for compression
- WebP format for modern browsers
- Responsive images with `srcset` for different screen sizes