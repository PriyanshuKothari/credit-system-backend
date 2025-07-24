from rest_framework import serializers
from .models import Customer

class CustomerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id','first_name', 'last_name', 'age', 'monthly_salary', 'phone_number']

    def create(self, validated_data):
        # Calculate approved limit
        salary = validated_data['monthly_salary']
        approved_limit = round(36 * salary, -5)  # round to nearest lakh
        validated_data['approved_limit'] = approved_limit
        validated_data['current_debt'] = 0.0
        return Customer.objects.create(**validated_data)

from rest_framework import serializers

class LoanEligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class LoanCreateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()