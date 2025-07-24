from django.test import TestCase, Client
from django.urls import reverse
from credit_system_app.models import Customer
from rest_framework.test import APITestCase
from rest_framework import status
from credit_system_app.models import Customer, Loan

class CustomerAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.eligibility_url = reverse('check-eligibility')
        self.test_customer_data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "phone_number": "1234567890",
            "monthly_salary": 50000
        }

    def test_register_customer_success(self):
        response = self.client.post(self.register_url, data=self.test_customer_data, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("customer_id", response.json())

    def test_check_eligibility_valid(self):
        # First register a customer
        register_res = self.client.post(self.register_url, data=self.test_customer_data, content_type="application/json")
        customer_id = register_res.json().get("customer_id")

        # Check eligibility
        eligibility_data = {
            "customer_id": customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(self.eligibility_url, data=eligibility_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.json())


class LoanFlowTests(APITestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id=999,
            first_name="Loan",
            last_name="Tester",
            age=30,
            phone_number="9876543210",
            monthly_salary=50000,
            approved_limit=1000000,
            current_debt=0
        )

    def test_create_loan(self):
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post("/create-loan", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("loan_id", response.data)
        self.assertEqual(response.data["message"], "Loan created successfully.")

    def test_make_payment(self):
        # First create a loan
        loan = Loan.objects.create(
            loan_id=12345,
            customer=self.customer,
            loan_amount=60000,
            interest_rate=10,
            tenure=12,
            monthly_installment=5275.60,
            emis_paid_on_time=10,
            start_date="2024-01-01",
            end_date="2025-01-01"
        )

        response = self.client.post("/make-payment", {
            "customer_id": self.customer.customer_id,
            "loan_id": loan.loan_id
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Payment successful")
        self.assertIn("remaining_tenure", response.data)