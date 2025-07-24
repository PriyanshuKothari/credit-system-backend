from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import CustomerRegisterSerializer

@method_decorator(csrf_exempt, name='dispatch')
class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoanEligibilitySerializer
from .models import Customer
import math

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = LoanEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Get customer info
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

        # EMI Calculation
        P = loan_amount
        R = interest_rate / (12 * 100)
        N = tenure

        try:
            emi = P * R * (1 + R) ** N / ((1 + R) ** N - 1)
        except ZeroDivisionError:
            return Response({"detail": "Invalid interest rate or tenure"}, status=400)

        # Eligibility Conditions
        if loan_amount > customer.approved_limit:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "reason": "Loan amount exceeds approved limit."
            }, status=status.HTTP_200_OK)

        if emi > 0.5 * customer.monthly_salary:
            return Response({
                "customer_id": customer_id,
                "approval": False,
                "reason": "EMI exceeds 50% of monthly salary."
            }, status=status.HTTP_200_OK)

        # Eligible
        return Response({
            "customer_id": customer_id,
            "approval": True,
            "interest_rate": interest_rate,
            "corrected_tenure": tenure,
            "monthly_installment": round(emi, 2)
        }, status=status.HTTP_200_OK)

from .models import Customer, Loan
from .serializers import LoanCreateSerializer
from django.db import transaction
import math
import pandas as pd
from datetime import datetime

class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                customer = Customer.objects.get(customer_id=data['customer_id'])
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)

            # Calculate EMI
            P = data['loan_amount']
            R = data['interest_rate'] / (12 * 100)
            N = data['tenure']
            emi = (P * R * ((1 + R)**N)) / (((1 + R)**N) - 1)

            # Eligibility check
            if emi > 0.5 * customer.monthly_salary or data['loan_amount'] > customer.approved_limit:
                return Response({"error": "Customer not eligible for loan"}, status=400)

            # Create loan
            with transaction.atomic():
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=data['loan_amount'],
                    tenure=N,
                    interest_rate=data['interest_rate'],
                    monthly_installment=round(emi, 2),
                    emis_paid_on_time=0,
                    start_date=datetime.now().date(),
                    end_date=datetime.now().date() + pd.DateOffset(months=N)
                )

            return Response({"loan_id": loan.loan_id, "message": "Loan created successfully."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)



class ViewLoanView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            customer = loan.customer

            return Response({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "tenure": loan.tenure,
                "start_date": loan.start_date,
                "end_date": loan.end_date,
                "emis_paid_on_time": loan.emis_paid_on_time,
                "customer": {
                    "customer_id": customer.customer_id,
                    "name": f"{customer.first_name} {customer.last_name}",
                    "age": customer.age,
                    "phone_number": customer.phone_number,
                    "monthly_income": customer.monthly_salary,
                    "approved_limit": customer.approved_limit,
                    "current_debt": customer.current_debt
                }
            })
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer=customer)

            loans_data = []
            for loan in loans:
                loans_data.append({
                    "loan_id": loan.loan_id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "monthly_installment": loan.monthly_installment,
                    "tenure": loan.tenure,
                    "start_date": loan.start_date,
                    "end_date": loan.end_date,
                    "emis_paid_on_time": loan.emis_paid_on_time
                })

            return Response({
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "loans": loans_data
            })
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

class MakePaymentView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_id = request.data.get('loan_id')

        try:
            loan = Loan.objects.get(loan_id=loan_id, customer__customer_id=customer_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found for this customer."}, status=404)

        if loan.tenure <= 0:
            return Response({"error": "Loan already paid off."}, status=400)

        # Update loan details
        loan.tenure -= 1
        loan.emis_paid_on_time += 1
        loan.save()

        # Update customer debt
        customer = loan.customer
        customer.current_debt -= loan.monthly_installment
        if customer.current_debt < 0:
            customer.current_debt = 0
        customer.save()

        return Response({
            "message": "Payment successful",
            "remaining_tenure": loan.tenure
        })

class CustomerStatementView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        loans = Loan.objects.filter(customer=customer)

        loan_data = []
        for loan in loans:
            loan_data.append({
                "loan_id": loan.loan_id,
                "loan_amount": loan.loan_amount,
                "tenure": loan.tenure,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "emis_paid_on_time": loan.emis_paid_on_time,
                "start_date": loan.start_date,
                "end_date": loan.end_date
            })

        return Response({
            "customer_id": customer.customer_id,
            "name": f"{customer.first_name} {customer.last_name}",
            "phone_number": customer.phone_number,
            "approved_limit": customer.approved_limit,
            "current_debt": customer.current_debt,
            "loans": loan_data
        })
