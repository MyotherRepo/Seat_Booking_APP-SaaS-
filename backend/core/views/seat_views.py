from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Seat,Booking
from core.serializers import SeatSerializer
from datetime import datetime,date

# vanilla get seat function
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seats_by_floorplan(request):
    floor_id = request.query_params.get('floor_id')
    if not floor_id:
        return Response({'error':'floor_id is required'},status=400)

    seats = Seat.objects.filter(floor_plan_id=floor_id, is_active = True)
    serializer = SeatSerializer(seats,many = True)
    return Response(serializer.data)

# Seat grid API along with booking status
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def seat_grid_status(request):
    floor_id = request.query_params.get('floor_id')
    booking_date = request.query_params.get('date',date.today())

    if not floor_id:
        return Response({'error' : 'floor_id id required'} , status = 400)
    
    seats = Seat.objects.filter(floor_plan_id = floor_id , is_active = True)
    bookings = Booking.objects.filter(seat__floor_plan_id = floor_id, date = booking_date)
    booking_map = {b.seat_id : b.user_id for b in bookings}

    response_data = []
    for seat in seats:
        booking_user_id = booking_map.get(seat.id) 

        if not booking_user_id:
            status = 'available'
        elif booking_user_id == request.user.id:
            status = 'My Seat'
        else:
            status = 'already booked'

        response_data.append({
            'seat_id' : seat.id,
            'label' : seat.label,
            'row':seat.row,
            'column' : seat.column,
            'status' : status
        })

    return Response(response_data)