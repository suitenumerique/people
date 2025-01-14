"""Views for handling OAuth2 authentication via API."""

import datetime

from django.contrib.auth import login

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from .serializers import LoginSerializer


class LoginView(APIView):
    """Login view to allow users to authenticate and create a session from the frontend."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticate user and create session.
        """
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # User is None if the credentials are invalid
        user = serializer.validated_data["user"]

        if user is not None:
            login(request, user)
            # In this context we need a session long enough to allow the user to
            # authenticate to make the OIDC loop. A minute should be enough.
            # Even if the session is longer, the one_time_email_authenticated_session
            # middleware will kill the session as soon as the user tries to access
            # paths outside the OIDC process or when the OIDC process is done here.
            request.session.set_expiry(datetime.timedelta(minutes=1))
            return Response({"message": "Successfully logged in"})

        return Response(
            {"error": "Invalid credentials"},
            status=HTTP_401_UNAUTHORIZED,
        )
