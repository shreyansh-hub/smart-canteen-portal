# Smart Canteen Portal
A full-stack web application designed to automate canteen operations for schools, colleges, and offices. It enables users to browse menus, place orders, and make secure online payments while providing powerful admin controls.
---
## Features
### User Features
- User registration & login (secure authentication)
- Browse menu items
- Add to cart & place orders
- Online payment (UPI / Card)
- Order history & status tracking
### Admin Features
- Admin dashboard
- Manage menu items (add / edit / delete)
- Order management system
- Payment tracking
- Handle custom requests
### Canteen Owner Features
- Register canteen
- Manage menu & availability
- Add bank details for payments
---
## Payment & Notifications
- Razorpay integration for secure payments
- Email notifications using SendGrid
---
## Tech Stack
| Layer     | Technology                       |
|-----------|----------------------------------|
| Backend   | Python (Flask)                   |
| Database  | SQLite (SQLAlchemy ORM)          |
| Frontend  | HTML, CSS, Bootstrap, JavaScript |
| Auth      | Flask-Login                      |
| Payments  | Razorpay                         |
| Messaging | SendGrid                         |
---
## Setup Instructions
### Clone the repository
```bash
git clone https://github.com/shreyansh-hub/smart-canteen-portal.git
cd smart-canteen-portal
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Configure environment variables
Create a `.env` file and add:
```env
DATABASE_URL=your_database_url
SENDGRID_API_KEY=your_sendgrid_api_key
RAZORPAY_KEY_ID=your_key
RAZORPAY_SECRET=your_secret
```
### Run database migrations
```bash
flask db upgrade
```
### Run the application
```bash
flask run
```
---
## Future Enhancements
- [ ] Mobile app integration
- [ ] AI-based menu recommendations
- [ ] Advanced analytics dashboard
---
## Author
**Shreyansh Mishra**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/shreyansh-mishra05/)
[![Email](https://img.shields.io/badge/Email-red?style=flat&logo=gmail)](mailto:shreyansh.mishra0009@gmail.com)
