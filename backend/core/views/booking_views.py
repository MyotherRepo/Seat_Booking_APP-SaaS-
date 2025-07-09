from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Booking,Seat,Waitlist
from core.serializers import BookingSerializer
from django.db import IntegrityError
from datetime import date,datetime
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from core.models import User, Seat, Booking , Waitlist


# create a booking by the manager
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking(request):
    user = request.user

    if user.role != 'manager':
        return Response({'error': 'Only managers can create bookings for others.'}, status=403)

    target_user_id = request.data.get('user_id')
    seat_id = request.data.get('seat_id')
    booking_date = request.data.get('date')

    if not target_user_id or not seat_id or not booking_date:
        return Response({'error': 'user_id, seat_id, and date are required'}, status=400)

    try:
        target_user = User.objects.get(id=target_user_id)
        seat = Seat.objects.get(id=seat_id)
        booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Seat.DoesNotExist:
        return Response({'error': 'Seat not found'}, status=404)
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    #  user already has a booking on that date
    if Booking.objects.filter(user=target_user, date=booking_date).exists():
        return Response({'error': 'This user already has a booking on this date'}, status=409)

    # Check if the seat is already booked on that date
    if Booking.objects.filter(seat=seat, date=booking_date).exists():
        return Response({'error': 'Seat already booked on this date'}, status=409)

    try:
        booking = Booking.objects.create(
            user=target_user,
            seat=seat,
            date=booking_date,
            booked_by_manager=True
        )
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=201)

    except IntegrityError:
        return Response({'error': 'Booking failed due to a constraint'}, status=500)
    
#view booking
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-date')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


# mark attendance if booking for today is present  
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

    return Response({'message': 'Booking cancelled. No waitlisted user found.'})

#Race Condition
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def book_seat(request):
    user = request.user
    seat_id = request.data.get("seat_id")
    booking_date = request.data.get("date")  # we get sends "YYYY-MM-DD"

    if not seat_id:
        return Response({'error': 'Seat ID is required'}, status=400)

    if not booking_date:
        booking_date = date.today()
    else:
        try:
            booking_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    try:
        seat = Seat.objects.select_for_update().get(id=seat_id)

        # Prevent duplicate bookings for the user on the same date
        if Booking.objects.filter(user=user, date=booking_date).exists():
            return Response({'error': 'You already have a booking on this date'}, status=400)

        # Check if seat is already booked
        if Booking.objects.filter(seat=seat, date=booking_date).exists():
            # If seat is booked, automatically add the user to the waitlist
            if not Waitlist.objects.filter(user=user, seat=seat, date=booking_date).exists():
                Waitlist.objects.create(user=user, seat=seat, date=booking_date)
                return Response({'message': 'Seat already booked. You have been added to the waitlist.'}, status=202)
            else:
                return Response({'message': 'You are already on the waitlist for this seat and date.'}, status=200)

        # If seat is not booked, we will create a booking
        Booking.objects.create(user=user, seat=seat, date=booking_date)
        return Response({'message': 'Seat booked successfully for today'}, status=201)

    except Seat.DoesNotExist:
        return Response({'error': 'Seat not found'}, status=404)