"""Views for handling OAuth2 authentication via API."""

from django.contrib.auth import authenticate, login

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView


class LoginView(APIView):
    """Login view to allow users to authenticate and create a session from the frontend."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and create session.
        """
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Please provide both email and password"},
                status=HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "Successfully logged in"})

        return Response(
            {"error": "Invalid credentials"},
            status=HTTP_401_UNAUTHORIZED,
        )
