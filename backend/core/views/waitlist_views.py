from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Waitlist,Booking,Seat
from core.serializers import WaitlistSerializer
from datetime import date
from django.db import IntegrityError

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_waitlist(request):
    user = request.user
    seat_id = request.data.get('seat')
    booking_date = request.data.get('date')

    if not seat_id or not booking_date:
        return Response({'error' : 'seat and date are required'},status=400)
    
    try:
        wait = Waitlist.objects.create(
            user = user,
            seat_id=seat_id,
            date=booking_date
        )
        return Response({'message' : 'Added to waitlist'},status = 201)
    # based on unique constraint
    except IntegrityError:
        return Response({'error' : 'Already on Waitlist'},status = 409)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_waitlist(request):
    waits = Waitlist.objects.filter(user = request.user)
    serializer = WaitlistSerializer(waits,many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def leave_waitlist(request,waitlist_id):
    try:
        entry = Waitlist.objects.get(id = waitlist_id,user = request.user)
        entry.delete()
        return Response({'message' : 'Removed from Waitlist'})
    except Waitlist.DoesNotExist:
        return Response({'error' : 'Not found'},status=404)

