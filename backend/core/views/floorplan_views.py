from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import FloorPlan
from core.serializers import FloorPlanSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_floorplans(request):
    org = request.user.organisation
    floorplans = FloorPlan.objects.filter(organisation=org)
    serializer = FloorPlanSerializer(floorplans,many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_floorplan(request):
    if(request.user.role != 'manager'):
        return Response({'error' : 'Only managers can create floor plans'},status = 403)
    
    data = request.data.copy()
    data['organization'] = request.user.organisation.id

    serializer = FloorPlanSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.errors,status=400)