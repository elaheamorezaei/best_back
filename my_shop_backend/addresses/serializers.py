import re
from rest_framework import serializers
from core.utils import to_persian_date
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    fullAddress = serializers.CharField(source='full_address', read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'province', 'city', 'district', 'street', 'alley',
            'plaque', 'unit', 'postal_code', 'receiver_type',
            'receiver_name', 'phone_number', 'receiver_phone',
            'location_lat', 'location_lng', 'is_default', 'fullAddress',
        ]


class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['user', 'created_at']

    def validate_postal_code(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("کدپستی باید ۱۰ رقم باشد")
        return value


# ---------------------------------------------------------------------------
# Profile-specific serializers (camelCase, single `address` text field)
# ---------------------------------------------------------------------------

class ProfileAddressSerializer(serializers.ModelSerializer):
    address = serializers.CharField(source='street', read_only=True)
    postalCode = serializers.CharField(source='postal_code', read_only=True)
    phoneNumber = serializers.CharField(source='phone_number', read_only=True)
    receiverType = serializers.CharField(source='receiver_type', read_only=True)
    receiverName = serializers.SerializerMethodField()
    receiverPhone = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    mapAddress = serializers.CharField(source='map_address', read_only=True)
    isDefault = serializers.BooleanField(source='is_default', read_only=True)
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = [
            'id', 'province', 'city', 'address', 'plaque', 'unit',
            'postalCode', 'phoneNumber', 'receiverType', 'receiverName',
            'receiverPhone', 'location', 'mapAddress', 'isDefault', 'createdAt',
        ]

    def get_receiverName(self, obj):
        if obj.receiver_type == Address.RECEIVER_OTHER:
            return obj.receiver_name or None
        return None

    def get_receiverPhone(self, obj):
        if obj.receiver_type == Address.RECEIVER_OTHER:
            return obj.receiver_phone or None
        return None

    def get_location(self, obj):
        if obj.location_lat is not None and obj.location_lng is not None:
            return {'lat': obj.location_lat, 'lng': obj.location_lng}
        return None

    def get_createdAt(self, obj):
        return to_persian_date(obj.created_at)


class ProfileAddressWriteSerializer(serializers.Serializer):
    """Handles both POST (create) and PUT (partial update) for profile addresses.

    Context keys:
      - user: the authenticated user (required for create)
      - partial: bool — False for POST, True for PUT
    """
    province = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(max_length=500, required=False)
    plaque = serializers.CharField(max_length=20, required=False)
    unit = serializers.CharField(max_length=20, required=False, allow_blank=True)
    postalCode = serializers.CharField(max_length=10, required=False)
    phoneNumber = serializers.CharField(max_length=15, required=False)
    receiverType = serializers.ChoiceField(
        choices=[Address.RECEIVER_SELF, Address.RECEIVER_OTHER], required=False,
    )
    receiverName = serializers.CharField(max_length=200, required=False, allow_blank=True)
    receiverPhone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    location = serializers.DictField(required=False, allow_null=True)
    mapAddress = serializers.CharField(max_length=500, required=False, allow_blank=True)
    isDefault = serializers.BooleanField(required=False)

    def validate_postalCode(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("کدپستی باید ۱۰ رقم باشد")
        return value

    def validate_phoneNumber(self, value):
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود")
        return value

    def validate(self, data):
        if not self.context.get('partial', False):
            required = ['province', 'city', 'address', 'plaque', 'postalCode', 'phoneNumber']
            errors = {f: "این فیلد الزامی است" for f in required if not data.get(f)}
            if data.get('receiverType') == Address.RECEIVER_OTHER:
                if not data.get('receiverName'):
                    errors['receiverName'] = "نام تحویل‌گیرنده الزامی است"
                if not data.get('receiverPhone'):
                    errors['receiverPhone'] = "شماره تحویل‌گیرنده الزامی است"
            if errors:
                raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        user = self.context['user']
        loc = validated_data.get('location') or {}
        return Address.objects.create(
            user=user,
            province=validated_data['province'],
            city=validated_data['city'],
            street=validated_data['address'],
            plaque=validated_data['plaque'],
            unit=validated_data.get('unit', ''),
            postal_code=validated_data['postalCode'],
            phone_number=validated_data['phoneNumber'],
            receiver_type=validated_data.get('receiverType', Address.RECEIVER_SELF),
            receiver_name=validated_data.get('receiverName', ''),
            receiver_phone=validated_data.get('receiverPhone', ''),
            location_lat=loc.get('lat') if loc else None,
            location_lng=loc.get('lng') if loc else None,
            map_address=validated_data.get('mapAddress', ''),
            is_default=validated_data.get('isDefault', False),
        )

    def update(self, instance, validated_data):
        field_map = {
            'province': 'province', 'city': 'city', 'address': 'street',
            'plaque': 'plaque', 'unit': 'unit', 'postalCode': 'postal_code',
            'phoneNumber': 'phone_number', 'receiverType': 'receiver_type',
            'receiverName': 'receiver_name', 'receiverPhone': 'receiver_phone',
            'mapAddress': 'map_address', 'isDefault': 'is_default',
        }
        for src, dst in field_map.items():
            if src in validated_data:
                setattr(instance, dst, validated_data[src])
        if 'location' in validated_data:
            loc = validated_data['location'] or {}
            instance.location_lat = loc.get('lat') if loc else None
            instance.location_lng = loc.get('lng') if loc else None
        instance.save()
        return instance
