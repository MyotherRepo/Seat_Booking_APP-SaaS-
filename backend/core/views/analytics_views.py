from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count , Q,F
from django.db.models.functions import TruncDate
from datetime import datetime,timedelta
from core.models import Booking,FloorPlan,Seat,User
from core.serializers import BookingSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_bookings(request):
    user = request.user
    if user.role != 'manager':
        return Response({'error' : 'Only managers can view all the bookings'},status = 403)
    
    org = user.organization
    bookings = Booking.objects.filter(seat__floor_plan_organization=org)

    username = request.query_params.get('user')
    date = request.query_params.get('date')
    floorplan_id = request.query_params.get('floorplan')
    
    if username:
        bookings = bookings.filter(user__username=username)
    
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            bookings = bookings.filter(date=parsed_date)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    if floorplan_id:
        bookings = bookings.filter(seat__floor_plan_id=floorplan_id)
    
    data = []
    for b in bookings.select_related('user','seat','seat__floor_plan'):
        data.append({
            'booking_id' : b.id,
            'username' : b.user.username,
            'email' : b.user.email,
            'seat_label' : b.seat.floor_plan.name,
            'date' : b.date,
            'created_at': b.created_at,
            'attended': b.marked_attendance,
            'booked_by_manager': b.booked_by_manager
        })

    return Response(data)
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_summary(request):
    user = request.user
    if user.role != 'manager':
        return Response({'error': 'Only managers can access analytics'}, status=403)

    org = user.organization

    today = datetime.today().date()
    last_30_days = today - timedelta(days=30)

    bookings = Booking.objects.filter(seat__floor_plan__organization=org)
    recent_bookings = bookings.filter(date__gte=last_30_days)

    total = recent_bookings.count()
    attended = recent_bookings.filter(marked_attendance=True).count()
    no_shows = recent_bookings.filter(marked_attendance=False).count()

    # Calculate last-minute bookings
    last_minute = 0
    for booking in recent_bookings:
        if booking.created_at == booking.date:
            last_minute += 1

    # Utilization per floor
    utilization = []
    floors = FloorPlan.objects.filter(organization=org)
    for floor in floors:
        total_seats = Seat.objects.filter(floor_plan=floor).count()
        bookings_on_floor = recent_bookings.filter(seat__floor_plan=floor).count()
        utilization.append({
            'floor': floor.name,
            'seats': total_seats,
            'bookings': bookings_on_floor,
            'utilization_percent': round((bookings_on_floor / (30 * total_seats)) * 100, 2) if total_seats else 0
        })

    return Response({
        'total_bookings': total,
        'attended': attended,
        'no_shows': no_shows,
        'attendance_rate': round((attended / total) * 100, 2) if total else 0,
        'last_minute_bookings': last_minute,
        'floor_utilization': utilization
    })