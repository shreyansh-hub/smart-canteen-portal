# Canteen Automation System

A comprehensive web application for automating canteen operations in schools, colleges, and offices. The system allows users to browse menus, place orders, and make payments using various payment methods.

## Features

- **User Authentication**: Secure login and registration system with password reset functionality
- **Multiple User Roles**: Support for regular users, canteen owners, and admin roles
- **Menu Management**: Add, edit, and delete menu items with availability control
- **Order Processing**: Place orders, track status, and receive notifications
- **Payment Integration**: Secure payments using Stripe for UPI and card transactions
- **Canteen Registration**: Schools/colleges/offices can register their canteens
- **Real-time Notifications**: Email (SendGrid) and SMS (Twilio) notifications
- **Banking Integration**: Canteens can set up bank details to receive payments

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Payments**: Stripe API
- **Notifications**: SendGrid (Email), Twilio (SMS)
- **Frontend**: Bootstrap, JavaScript

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/canteen-automation-system.git
cd canteen-automation-system
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Set up environment variables:
```
export DATABASE_URL=your_database_url
export SENDGRID_API_KEY=your_sendgrid_api_key
export TWILIO_ACCOUNT_SID=your_twilio_account_sid
export TWILIO_AUTH_TOKEN=your_twilio_auth_token
export TWILIO_PHONE_NUMBER=your_twilio_phone_number
export STRIPE_SECRET_KEY=your_stripe_secret_key
```

4. Initialize the database:
```
flask db upgrade
```

5. Run the application:
```
flask run
```

## Usage

### Admin Dashboard
- Manage canteens, menu items, and user accounts
- View and process orders
- Access payment history

### Canteen Management
- Register new canteens
- Add bank details for payment processing
- Manage menu items

### User Interface
- Browse menu items
- Add items to cart
- Place orders
- Make payments
- View order history and status

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.