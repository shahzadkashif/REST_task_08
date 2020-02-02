from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
    flight = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='destination',
    )

    class Meta:
        model = Booking
        fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    flight = FlightSerializer()

    class Meta:
        model = Booking
        fields = ['total', 'flight', 'date',  'id', 'passengers']

    def get_total(self, obj):
        return obj.flight.price * obj.passengers


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        new_user = User(username=username,
                        first_name=first_name, last_name=last_name)
        new_user.set_password(password)
        new_user.save()
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    # bookings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', ]

    # def get_bookings(self, obj):
    #     bookings = obj.bookings.filter(date__lte=timezone.now())
    #     return BookingSerializer(bookings, many=True).data


class ProfileSerializer(serializers.ModelSerializer):
    past_bookings = serializers.SerializerMethodField()
    user = UserSerializer()
    tier = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'miles', 'past_bookings', 'tier', ]

    def get_tier(self, obj):
        if(0 <= obj.miles <= 9999):
            return("Blue")
        if(10000 <= obj.miles <= 59999):
            return("Silver")
        if(60000 <= obj.miles <= 99999):
            return("Gold")

        return("Platinum")

    def get_past_bookings(self, obj):
        bookings = obj.user.bookings.filter(date__lt=timezone.now())
        return BookingSerializer(bookings, many=True).data