from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count , Q,F
from datetime import datetime,timedelta
from core.models import Booking,FloorPlan,Seat

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_summary(request):
    user = request.user
    if user.role != 'manager':
        return Response({'error' : 'Only managers can access analytics'}, status=403)
    
    org = user.organisation

    today = datetime.today().date()
    last_30_days = today-timedelta(days=30)

    bookings = Booking.objects.filter(seat__floor_plan__organisation=org)
    recent_bookings = bookings.filter(date__gte = last_30_days)

    total = recent_bookings.count() #total bookings in the last 30 days by a particular organisation
    attended = recent_bookings.filter(marked_attendance=True).count() #booking vs attendance  
    no_shows = recent_bookings.filter(marked_attendance=False).count() #no show rate
    last_minute = recent_bookings.filter(created_at__date=F('date')).count() # Last minute Bookings

    utilization = []
    floors = FloorPlan.objects.filter(organisation=org)
    for floor in floors:
        total_seats = Seat.objects.filter(floor_plan=floor).count()
        bookings_on_floor = recent_bookings.filter(seat__floor_plan=floor).count()
        utilization.append({
            'floor' : floor.name,
            'seats' : total_seats,
            'bookings' : bookings_on_floor,
            'utilization_percent' : round((bookings_on_floor/(30*total_seats)) * 100 , 2 ) if total_seats else 0
        })

    return Response({
        'total_bookings' : total,
        'attended' : attended,
        'no_shows' : no_shows,
        'attendace_rate' : round((attended/total) * 100 , 2) if total else 0,
        'last_minute_bookings' : last_minute,
        'floor_utilization' : 'utilization'
    })