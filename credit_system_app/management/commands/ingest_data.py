import pandas as pd
from django.core.management.base import BaseCommand
from credit_system_app.models import Customer, Loan
from datetime import datetime

class Command(BaseCommand):
    help = "Ingest initial customer and loan data from Excel"

    def handle(self, *args, **kwargs):
        customer_df = pd.read_excel('data/customer_data.xlsx')
        loan_df = pd.read_excel('data/loan_data.xlsx')

        # Clean column names
        customer_df.columns = customer_df.columns.str.strip().str.lower().str.replace(" ", "_")
        loan_df.columns = loan_df.columns.str.strip().str.lower().str.replace(" ", "_")

        # ✅ Sample customer columns: ['customer_id', 'first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit']

        for _, row in customer_df.iterrows():
            Customer.objects.update_or_create(
                phone_number=str(row['phone_number']),  # ✅ Use unique field instead of customer_id
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'monthly_salary': row['monthly_salary'],
                    'approved_limit': row['approved_limit'],
                    'current_debt': 0.0,
                    'age': row['age']
            }
        )



        # ✅ Sample loan columns: ['customer_id', 'loan_id', 'loan_amount', 'tenure', 'interest_rate', 'monthly_payment', 'emis_paid_on_time', 'date_of_approval', 'end_date']

        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row['customer_id'])
            except Customer.DoesNotExist:
                continue  # Skip if customer doesn't exist

            Loan.objects.update_or_create(
                loan_id=row['loan_id'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['loan_amount'],
                    'tenure': row['tenure'],
                    'interest_rate': row['interest_rate'],
                    'monthly_installment': row['monthly_payment'],
                    'emis_paid_on_time': row['emis_paid_on_time'],
                    'start_date': pd.to_datetime(row['date_of_approval']).date(),
                    'end_date': pd.to_datetime(row['end_date']).date()
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Data ingestion complete."))
