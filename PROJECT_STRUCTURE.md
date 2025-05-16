# Project Structure

This document explains the structure of the Canteen Automation System project to help you understand how the codebase is organized.

## Core Files

- `main.py`: Entry point for the application
- `app.py`: Flask application setup and configuration
- `models.py`: Core database models (User, MenuItem, OrderItem, Order)
- `models_extension.py`: Extended database models (Canteen, BankAccount, Payment, Notification, PasswordResetToken)

## Feature Modules

- `auth.py`: User authentication (login, registration, password reset)
- `menu.py`: Menu management and user dashboard
- `orders.py`: Order processing and status management
- `canteen.py`: Canteen registration and management
- `notifications.py`: Email and SMS notification system
- `payments.py`: Payment processing with Stripe

## Templates

- `templates/`
  - `base.html`: Base template with common layout
  - `login.html`: User login form
  - `register.html`: User registration form
  - `forgot_password.html`: Password reset request form
  - `reset_password.html`: New password form
  
  - `admin/`: Admin-specific templates
    - `dashboard.html`: Admin dashboard
    - `canteens.html`: Canteen management
    - `menu_management.html`: Menu management
    - `payment_history.html`: Payment tracking
  
  - `canteen/`: Canteen-specific templates
    - `register.html`: Canteen registration form
    - `bank_details.html`: Bank details form
    - `manage.html`: Canteen management interface
  
  - `user/`: User-specific templates
    - `dashboard.html`: User dashboard
    - `menu.html`: Menu browsing interface
    - `cart.html`: Shopping cart
    - `order_confirmation.html`: Order confirmation
    - `payment_history.html`: User payment history
    
  - `notifications/`: Notification templates
    - `list.html`: Notification list view

## Static Assets

- `static/`
  - `css/`: CSS stylesheets
    - `custom.css`: Custom styling
  - `js/`: JavaScript files
    - `main.js`: Main JavaScript functionality
    - `cart.js`: Shopping cart functionality

## Architecture Overview

The application follows a modular architecture with clear separation of concerns:

1. **Database Layer**: SQLAlchemy models in `models.py` and `models_extension.py`
2. **Business Logic Layer**: Python modules (`auth.py`, `menu.py`, etc.)
3. **Presentation Layer**: Jinja2 templates in the `templates/` directory
4. **Static Assets**: CSS and JavaScript in the `static/` directory

## Design Patterns

- **Blueprint Pattern**: Flask blueprints used for modular routing
- **MVC-like Structure**: 
  - Models: Database models in `models.py`
  - Views: Templates in `templates/`
  - Controllers: Route handlers in feature modules
- **Dependency Injection**: Flask extensions initialized in `app.py`
- **Repository Pattern**: Database access abstracted through SQLAlchemy models