import json

from django.db.models import QuerySet
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from authentication.utils import hash_password, TokenManager, require_token
from users.models import User
from users.serializers import UserSerializer
from utils.exception import ValidationError


@require_http_methods(["POST"])
def login(request):
    # Read the username and password from the request
    data = json.loads(request.body.decode())
    if not data.get('username') or not data.get('password'):
        return HttpResponse(
            json.dumps({"message": "Username and password are required", "type": "login_fail"}),
            content_type='application/json',
            status=400
        )
    username = data.get('username')
    password_hash = hash_password(data.get('password'))
    # Check if the username and password are correct
    user: QuerySet[User] = User.objects.filter(username=username)
    if not user.exists():
        return HttpResponse(
            json.dumps({"message": f"User or password incorrect", "type": "login_fail"}),
            content_type='application/json',
            status=400
        )
    user: User = user.first()
    # Check the hash
    if user.password != password_hash:
        return HttpResponse(
            json.dumps({"message": f"User or password incorrect", "type": "login_fail"}),
            content_type='application/json',
            status=400
        )

    # Create JWT token
    try:
        access_token, refresh_token, access_expiration, refresh_expiration = TokenManager().create_token_pair(user.id)
        return HttpResponse(
            json.dumps({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_expiration": f"{access_expiration:%Y-%m-%d %H:%M:%S}",
                "refresh_expiration": f"{refresh_expiration:%Y-%m-%d %H:%M:%S}"
            }),
            content_type='application/json',
            status=200
        )
    except ValidationError as e:
        return e.as_http_response()


@require_http_methods(["POST"])
@require_token
def logout(request):
    # Read the token from the header
    bearer_token = request.headers.get('Authorization')
    token = bearer_token.split(" ")[1]
    # Revoke the token
    try:
        TokenManager().revoke_token(token)
    except ValidationError as e:
        return e.as_http_response()
    return HttpResponse(
        json.dumps({"message": "Logout successful"}),
        content_type='application/json',
        status=200
    )


@require_http_methods(["POST"])
def refresh(request):
    # Read the token from the header
    data = json.loads(request.body.decode())
    if not data.get('refresh_token'):
        return HttpResponse(
            json.dumps({"message": "Refresh token is required", "type": "refresh_fail"}),
            content_type='application/json',
            status=400
        )
    refresh_token = data.get('refresh_token')
    print(refresh_token)
    # Refresh the token
    try:
        access_token, refresh_token, access_expiration, refresh_expiration = TokenManager().refresh_token(refresh_token)
        return HttpResponse(
            json.dumps({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "access_expiration": f"{access_expiration:%Y-%m-%d %H:%M:%S}",
                "refresh_expiration": f"{refresh_expiration:%Y-%m-%d %H:%M:%S}"
            }),
            content_type='application/json',
            status=200
        )
    except ValidationError as e:
        return e.as_http_response()


@require_http_methods(["POST"])
def register(request):
    # Read the username and password from the request
    data = json.loads(request.body.decode())
    if not data.get('username') or not data.get('password') or not data.get('email'):
        return HttpResponse(
            json.dumps({"message": "Username and password and email are required", "type": "register_fail"}),
            content_type='application/json',
            status=400
        )
    username = data.get('username')
    email = data.get('email')
    # Check if the username already exists
    if User.objects.filter(username=username).exists():
        return HttpResponse(
            json.dumps({"message": "Username already exists", "type": "register_fail"}),
            content_type='application/json',
            status=400
        )
    # Create the user
    user = UserSerializer(data={
        "username": username,
        "email": email,
        "password": data.get('password')
    })
    try:
        user.save()
    except ValidationError as e:
        return e.as_http_response()
    return HttpResponse(
        json.dumps({"message": "User registered successfully"}),
        content_type='application/json',
        status=200
    )