from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import FloorPlan,Seat
from core.serializers import FloorPlanSerializer

#get a list of floor plans
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_floorplans(request):
    org = request.user.organisation
    floorplans = FloorPlan.objects.filter(organisation=org)
    serializer = FloorPlanSerializer(floorplans,many=True)
    return Response(serializer.data)

#create floorplans
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_floorplan(request):
    if(request.user.role != 'manager'):
        return Response({'error' : 'Only managers can create floor plans'},status = 403)
    
    data = request.data.copy()
    data['organization'] = request.user.organization.id

    serializer = FloorPlanSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)

#bulk_create_seats
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_seats(request):
    user = request.user
    if user.role != 'manager':
        return Response({'error': 'Only managers can create seats'}, status=403)

    floorplan_id = request.data.get('floorplan_id')
    seats = request.data.get('seats', [])

    if not floorplan_id or not seats:
        return Response({'error': 'floorplan_id and seats are required'}, status=400)

    try:
        floorplan = FloorPlan.objects.get(id=floorplan_id, organization=user.organization)
    except FloorPlan.DoesNotExist:
        return Response({'error': 'Floorplan not found'}, status=404)

    created = []
    for seat_data in seats:
        seat = Seat.objects.create(
            floor_plan=floorplan,
            label=seat_data.get('label', ''),
            row=seat_data['row'],
            column=seat_data['column']
        )

        created.append({
            'id': seat.id,
            'label': seat.label,
            'row': seat.row,
            'column': seat.column
        })

    return Response({'message': 'Seats created successfully', 'seats': created}, status=201)
