# 🌸 Women SHG Management System

**An intelligent web-based platform that empowers Women Self-Help Groups (SHGs) by managing finances, users, and workflows with real-time tracking, automation, and multilingual support.**

---

## 1. Project Title & Tagline

A smart SHG management system that enables loan tracking, payment monitoring, meeting management, and user coordination in a centralized and scalable platform.

---

## 2. Problem Statement

Women Self-Help Groups often rely on manual record-keeping, which leads to errors, lack of transparency, and inefficient communication. Existing solutions are either too complex or not tailored for rural accessibility.

This project solves these issues by providing a **simple, centralized, and digital system** that allows SHGs to manage finances, meetings, and communication effectively while supporting local languages.

---

## 3. Features

| Feature                  | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| User Authentication     | Secure login with OTP email verification                                    |
| Loan Management         | Apply, approve, and track loans                                             |
| Payment Tracking        | Monitor repayments and financial records                                    |
| Meeting Management      | Schedule and manage group meetings                                          |
| Admin Dashboard         | Full control over users, loans, and activities                              |
| Notification System     | Automated reminders for payments and updates                                |
| Multilingual Support    | Supports English and Tamil                                                  |
| Chatbot Assistance      | Helps users navigate and interact with the system                           |
| Role-Based Access       | Separate access for Admins, Sub-admins, and Users                           |

---

## 4. Tech Stack

### Backend
- Python (Flask)

### Frontend
- HTML
- CSS
- Jinja Templates

### Database
- SQLite

### Integrations
- Flask-Mail (Email OTP & notifications)
- Custom Scheduler (Loan reminders)

---

## 5. Project Structure

```
Women-SHG-Project/
│
├── Hackathon/
│   ├── app.py                 # Main application
│   ├── models.py              # Database models
│   ├── auth.py                # Authentication logic
│   ├── admin.py               # Admin routes
│   ├── user.py                # User routes
│   ├── forms.py               # Form handling
│   ├── email_utils.py         # Email system
│   ├── loan_reminder_scheduler.py
│   ├── config.py              # Configuration
│   ├── requirements.txt
│   │
│   ├── templates/             # UI pages
│   ├── static/                # CSS, JS, images
│   │
│   └── instance/
│       └── database.db        # SQLite database
│
└── README.md

````

---

## 6. Installation & Setup

### Clone Repository

```bash
git clone https://github.com/yourusername/women-shg-management.git
cd women-shg-management/Hackathon
````

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Edit `config.py`:

```python
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "your-app-password"
SECRET_KEY = "your-secret-key"
```

---

### Run Application

```bash
python app.py
```

Open:

```
http://127.0.0.1:5000/
```

---

## 7. How It Works

### 1. User Flow

1. User registers using email
2. OTP verification is completed
3. User accesses dashboard
4. Performs actions (loan, payment, meetings)
5. System updates data in real-time

---

### 2. Loan System

1. User applies for loan
2. Admin reviews request
3. Loan is approved/rejected
4. Repayment tracking begins
5. Notifications are sent for due payments

---

### 3. Notification System

1. Scheduler checks due payments
2. Email reminders are triggered
3. Users receive alerts instantly

---

## 8. Scalability

* Can be upgraded from SQLite → MySQL/PostgreSQL
* Deployable on cloud platforms (AWS, Render, Railway)
* Modular structure supports future expansion
* Scheduler can be replaced with Celery/Redis

---

## 9. Feasibility

This project uses simple and widely adopted technologies, making it easy to implement and deploy. It is cost-effective and suitable for small to medium-scale SHGs.

---

## 10. Novelty

This system is designed as a **digital transformation tool for rural financial groups**.

Key uniqueness:

* Local language support (Tamil)
* SHG-focused financial workflow
* Automation via reminders
* Lightweight and easy to use

---

## 11. Feature Depth

* OTP-based secure authentication
* Real-time updates after every operation
* Persistent database storage
* Role-based system (Admin/User)
* Error handling for:

  * Invalid inputs
  * Failed transactions
  * Missing data

---

## 12. Ethical Use & Disclaimer

* User data is securely handled
* Email authentication requires user consent
* No personal data is shared with third parties
* Designed for ethical financial management use

---

## 13. License

This project is intended for educational and social impact purposes.

---

## 14. Author

**Sanjay**
📧 [your-email@sanjaypriyan0987@gmail.com]
🔗 [https://github.com/sanjay-ux391]
