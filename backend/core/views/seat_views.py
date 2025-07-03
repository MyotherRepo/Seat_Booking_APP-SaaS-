from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Seat
from core.serializers import SeatSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seats_by_floorplan(request):
    floor_id = request.query_params.get('floor_id')
    if not floor_id:
        return Response({'error':'floor_id is required'},status=400)

    seats = Seat.objects.filter(floor_plan_id=floor_id, is_active = True)
    serializer = SeatSerializer(seats,many = True)
    return Response(serializer.data)


