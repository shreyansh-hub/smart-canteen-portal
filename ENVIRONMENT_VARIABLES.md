# Environment Variables

The Canteen Automation System requires several environment variables to be set for proper functioning. This document explains what each variable is used for and how to set them.

## Required Environment Variables

### Database Configuration
- `DATABASE_URL`: PostgreSQL connection URL in the format `postgresql://username:password@host:port/database_name`
- `PGHOST`: PostgreSQL host (used as a fallback)
- `PGPORT`: PostgreSQL port (used as a fallback)
- `PGUSER`: PostgreSQL user (used as a fallback)
- `PGPASSWORD`: PostgreSQL password (used as a fallback)
- `PGDATABASE`: PostgreSQL database name (used as a fallback)

### Email Notifications (SendGrid)
- `SENDGRID_API_KEY`: Your SendGrid API key for sending email notifications

### SMS Notifications (Twilio)
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number for sending SMS

### Payment Processing (Stripe)
- `STRIPE_SECRET_KEY`: Your Stripe secret key for processing payments

### Application Security
- `SESSION_SECRET`: A secret key for securing Flask sessions (should be a long, random string)

## Setting Environment Variables

### Development (Local)
Create a `.env` file in the project root directory with the following content:
```
DATABASE_URL=postgresql://username:password@host:port/database_name
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=canteen_automation
SENDGRID_API_KEY=your_sendgrid_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
STRIPE_SECRET_KEY=your_stripe_secret_key
SESSION_SECRET=your_session_secret
```

### Production Deployment
For production deployments, set these environment variables according to your hosting platform's documentation. This typically involves using a web interface or CLI commands specific to your hosting provider.

## Important Security Notes

- Never commit `.env` files or any files containing these values to your Git repository
- Regularly rotate your secret keys, especially for production environments
- Use strong, unique values for each environment variable
- Consider using a secrets management service for production environments