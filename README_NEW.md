# Experienciaas - Event Platform

A modern, minimalist event discovery and booking platform built with Django. Find and register for events in your city with a beautiful, user-friendly interface.

## 🌟 Features

- **Modern UI**: Clean, minimalist design with responsive layout
- **Event Discovery**: Search and filter events by city, category, date, and more
- **User Registration**: Easy event registration and ticket management
- **Admin Panel**: Complete event management system
- **Multi-language Support**: Built with internationalization in mind
- **Mobile-First**: Responsive design that works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd experienciaas
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/local.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Populate with sample data**
   ```bash
   python manage.py populate_events
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to see the application!

## 🎨 Design Features

### Color Scheme
- Primary: `#3B82F6` (Blue)
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Error: `#EF4444` (Red)

### Typography
- Font Family: Inter (Google Fonts)
- Modern, clean typeface with excellent readability

### Components
- **Event Cards**: Clean cards with hover effects and image overlays
- **Filter Bar**: Easy-to-use filtering system
- **Navigation**: Sticky header with search integration
- **Responsive Grid**: Adaptive layout for all screen sizes

## 📱 Mobile Experience

The platform is built mobile-first with:
- Touch-friendly interface
- Optimized navigation
- Fast loading times
- Smooth animations

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Custom CSS with CSS Variables
- **Icons**: Font Awesome 6
- **Database**: PostgreSQL
- **Authentication**: Django Allauth

## 📦 Project Structure

```
experienciaas/
├── config/              # Django configuration
├── experienciaas/       # Main application
│   ├── events/         # Events app (main functionality)
│   ├── users/          # User management
│   ├── static/         # Static files (CSS, JS, images)
│   └── templates/      # HTML templates
├── requirements/       # Python dependencies
└── compose/           # Docker configuration
```

## 🎯 Key Models

### Event
- Title, description, images
- Date, time, location
- Pricing (free/paid)
- Capacity management
- Categories and cities

### City
- Name, country
- URL-friendly slugs

### Category
- Name, description
- Custom icons and colors

### Ticket
- User registration
- Payment tracking
- Status management

## 🔧 Customization

### Adding New Event Categories

1. Access Django Admin
2. Go to Events → Categories
3. Add new category with icon and color
4. Icon uses Font Awesome classes (e.g., `fas fa-music`)

### Styling Customization

Edit `experienciaas/static/css/project.css`:
- CSS Variables at the top for colors
- Component-specific styles
- Responsive breakpoints

### Adding New Cities

1. Django Admin → Events → Cities
2. Add city with country information
3. Slug is auto-generated for SEO-friendly URLs

## 🌐 Deployment

### Production Settings

1. Set environment variables:
   ```bash
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-secret-key
   DATABASE_URL=postgres://user:pass@localhost/db
   ```

2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

3. Use production server (Gunicorn + Nginx)

### Docker Deployment

```bash
docker-compose -f docker-compose.production.yml up -d
```

## 📊 Admin Panel

Access at `/admin/` with superuser credentials:

- **Event Management**: Create, edit, delete events
- **User Management**: Handle user accounts and permissions
- **Analytics**: View event statistics and user engagement
- **Content Management**: Manage cities and categories

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure authentication
- Rate limiting (production)

## 📈 Performance

- Optimized queries with select_related
- Image optimization
- CSS/JS compression
- Database indexing
- Lazy loading

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@experienciaas.com

## 🏗️ Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
black .
flake8 .
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

Built with ❤️ using Django and modern web technologies.
