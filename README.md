# Smart Canteen Portal

A full-stack web app to manage canteen operations — built for schools, colleges, and offices. Users can browse the menu, place orders, and pay online. Admins and canteen owners get their own dashboards to manage everything on the backend.

---

## Why I built this

Canteen queues are slow and cash payments are a mess. This tries to fix that — orders go through the app, payments are handled online, and the kitchen knows exactly what's coming in.

---

## What's inside

**For users**
- Register, log in, browse the menu
- Add items to cart and place orders
- Pay via UPI or card (Razorpay)
- Track order status and view past orders

**For admins**
- Dashboard to manage orders and payments
- Add, edit, or remove menu items
- Handle custom requests from users

**For canteen owners**
- Register their canteen
- Control menu availability
- Add bank details to receive payments

---

## Tech used

- **Backend** — Python, Flask
- **Database** — SQLite with SQLAlchemy ORM
- **Frontend** — HTML, CSS, Bootstrap, JavaScript
- **Auth** — Flask-Login
- **Payments** — Razorpay
- **Email notifications** — SendGrid

---

## Running it locally

```bash
git clone https://github.com/shreyansh-hub/smart-canteen-portal.git
cd smart-canteen-portal
pip install -r requirements.txt
```

Create a `.env` file and fill in:

```env
DATABASE_URL=your_database_url
SENDGRID_API_KEY=your_sendgrid_api_key
RAZORPAY_KEY_ID=your_key
RAZORPAY_SECRET=your_secret
```

Then:

```bash
flask db upgrade
flask run
```

---

## What I'd add next

- Mobile app
- Analytics for canteen owners (peak hours, popular items, etc.)
- Menu recommendations based on order history
