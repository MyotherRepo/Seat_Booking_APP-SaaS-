from rest_framework import serializers
from .models import Organization,User,FloorPlan,Seat,Booking,Waitlist

#1. Organisation
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id','name','domain']

#2. User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','role','organization']
    
#3. FloorPlan
class FloorPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FloorPlan
        fields = ['id','organization','name','image','rows','columns']
        
#4. Seat
class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id','floor_plan','label','row','column','is_active']

#5. Booking
class BookingSerializer(serializers.ModelSerializer):
    seat_detail = SeatSerializer(source='seat',read_only=True)
    user_detail = UserSerializer(source='user',read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'seat','seat_detail',
            'user','user_detail',
            'date',
            'created_at',
            'marked_attendance',
            'booked_by_manager'
        ]

        read_only_fields = ['created_at']

#6. Waitlist
class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = '__all__'