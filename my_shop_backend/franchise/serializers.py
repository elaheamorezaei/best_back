import re
from rest_framework import serializers
from .models import FranchiseApplication


class FranchiseApplySerializer(serializers.Serializer):
    fullName = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False)
    city = serializers.CharField(max_length=100)
    province = serializers.CharField(max_length=100)
    franchiseType = serializers.ChoiceField(choices=FranchiseApplication.FRANCHISE_TYPE_CHOICES)
    investmentRange = serializers.ChoiceField(choices=FranchiseApplication.INVESTMENT_RANGE_CHOICES)
    hasSalesExperience = serializers.BooleanField()
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        if not re.match(r'^09\d{9}$', value.strip()):
            raise serializers.ValidationError("شماره تماس معتبر نیست")
        return value.strip()

    def validate_fullName(self, value):
        if not value.strip():
            raise serializers.ValidationError("نام و نام خانوادگی الزامی است")
        return value.strip()
