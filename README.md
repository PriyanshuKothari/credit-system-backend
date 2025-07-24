# 💳 Credit System API (Django + DRF + Docker)

A simple credit system backend with customer registration, loan eligibility, loan management, and repayment features.

> ✅ Built with Django REST Framework  
> 🐳 Dockerized for production  
> 🚀 Deployed on Render  

---

## 🚀 Live Demo

- 🔗 API Base URL: [https://credit-system-9hj8.onrender.com](https://credit-system-9hj8.onrender.com)
- 📄 Swagger Docs: [https://credit-system-9hj8.onrender.com/swagger/](https://credit-system-9hj8.onrender.com/swagger/)
- 🟥 Redoc: [https://credit-system-9hj8.onrender.com/redoc/](https://credit-system-9hj8.onrender.com/redoc/)
---

## 📦 Features

- ✅ Customer Registration (`/register`)
- ✅ Loan Eligibility Check (`/check-eligibility`)
- ✅ Create Loan (`/create-loan`)
- ✅ View Loan by ID (`/view-loan/<loan_id>`)
- ✅ View All Loans by Customer (`/view-loans/<customer_id>`)
- ✅ Make EMI Payment (`/make-payment`)
- ✅ View Customer Details (`/view-customer/<customer_id>`)

---

## 🛠️ Setup Instructions (Local Development)

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/credit-system.git
   cd credit-system


2. **Create .env file**
``` 
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/credit_db
```


3. **Build & run with Docker**
```
docker-compose up --build
```

4. **Run Tests**
```
docker-compose exec web python manage.py test
```



## ⚙️ Technologies

- Python 3.10
- Django 5.x
- Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- Gunicorn (Production WSGI server)
- drf-yasg (Swagger/OpenAPI docs)


## 📂 Project Structure
```
credit_system/
├── credit_system_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```


## 🙏 Acknowledgements
Thanks to the assignment and reviewers for evaluating this project!

## 🔐 Disclaimer
Note: Secrets and environment variables are not included in this repo. Please create your own .env file as shown above.
