from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from core.models import User,Organization
from core.serializers import UserSerializer
from rest_framework.authtoken.models import Token

#create a new user account
@api_view(['POST'])
def register_user(request):
    data = request.data
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return Response({'error': f"'{field}' is required."}, status=400)

    #  username already exists
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already taken'}, status=400)

    # Extract domain from email and match to Organization , no need to send in the postman 
    try:
        domain = data['email'].split('@')[1]
        organization = Organization.objects.get(domain=domain)
    except (IndexError, Organization.DoesNotExist):
        return Response({'error': 'Invalid or unregistered organization domain'}, status=400)

    # Create user
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'employee'),
        organization=organization
    )

    serializer = UserSerializer(user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'user': serializer.data, 'token': token.key}, status=201)


@api_view(['POST'])
def login_user(request):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    if not user:
        return Response({'error': 'Invalid credentials'}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({
        'user': serializer.data,
        'token': token.key,
        'organization': user.organization.name if user.organization else None
    })
