from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Booking,Seat,Waitlist
from core.serializers import BookingSerializer
from django.db import IntegrityError
from datetime import date,datetime
from django.utils import timezone

# create a booking
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    user = request.user
    seat_id = request.data.get('seat')
    booking_date = request.data.get('date')

    # if seat_id or booking_date is none or missing
    if not seat_id or not booking_date:
        return Response({'error':'seat and date are required'},status = 400)
    
    try:
        booking = Booking.objects.create(
            user=user,
            seat_id=seat_id,
            date=booking_date
        )
        serializer=BookingSerializer(booking)
        return Response(serializer.data,status=201)
    except IntegrityError:
        return Response({'error':'Seat already booked for that day'},status = 409)

# mark attendance is booking for today is present  
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    user = request.user
    today = date.today()

    try:
        booking = Booking.objects.get(user=user,date=today)
        booking.marked_attendance = True
        booking.save()
        return Response({'success' : 'Attendance marked'})
    except Booking.DoesNotExist:
        return Response({'error':'No Booking found for today'},status = 404)
    
# cancel booking
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_booking(request,booking_id):
    user = request.user
    try:
        booking = Booking.objects.get(id=booking_id,user=request.user)
    except Booking.DoesNotExist:
        return Response({'error' : 'Booking not found'},status=404)

    #only allow if it's the user's booking or ther're a manager
    if booking.user != user and user.role != 'manager':
        return Response({'error' : 'Unauthorized'},status=403)
    
    # Save seat/date before deleting
    seat = booking.seat
    date = booking.date
    booking.delete()

    # Check waitlist and promote next user
    next_in_line = Waitlist.objects.filter(seat=seat,date=date).order_by('joined_at').first()

    if next_in_line:
        #create a booking for the guy
        Booking.objects.create(
            user = next_in_line.user,
            seat = seat,
            date = date,
        )

        #Remove the guy from the waitlist
        next_in_line.delete()

        # Send a notification
        return Response({
            'message' : 'Booking has been cancelled. Waitlisted user promoted.'
        })

    return Response({'message','Booking cancelled. No waitlisted user found.'})