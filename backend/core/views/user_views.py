from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from core.models import User
from core.serializers import UserSerializer
from rest_framework.authtoken.models import Token

#create a new user account
@api_view(['POST'])
def register_user(request):
    data = request.data
    if User.objects.filter(username=data['username']).exists():
        return Response({'error' : 'Username already taken'},status=400)
    
    user = User.objects.create_user(
        username = data['username'],
        email = data['email'],
        password = data['password'],
        role = data.get('role','employee'),
        organization_id = data['organization']
    )
    serializer = UserSerializer(user)
    token,_ = Token.objects.get_or_create(user=user)
    return Response({'user' : serializer.data,'token':token.key},status = 201)

@api_view(['POST'])
def login_user(request):
    user = authenticate(username=request.data['username'],password=request.data['password'])
    if not user:
        return Response({'error' : 'Invalid credentials'},status=401)
    
    token, _ = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'user':serializer.data,'token':token.key})

                           
                    