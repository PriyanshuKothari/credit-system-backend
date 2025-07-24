from django.urls import path
from .views import RegisterCustomerView,CheckEligibilityView,CreateLoanView, ViewLoanView, ViewCustomerLoansView, MakePaymentView, CustomerStatementView

urlpatterns = [
    path('register', RegisterCustomerView.as_view(), name='register'),
    path('check-eligibility', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>', ViewLoanView.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>', ViewCustomerLoansView.as_view(), name='view-customer-loans'),
    path('make-payment', MakePaymentView.as_view(), name='make-payment'),
    path('get-statement/<int:customer_id>', CustomerStatementView.as_view(), name='get-statement'),



]
