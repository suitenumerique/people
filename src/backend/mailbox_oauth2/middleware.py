"""Middleware to allow a user to authenticate against "/o/authorize" only once."""

from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.sessions.exceptions import SuspiciousSession
from django.urls import reverse


def one_time_email_authenticated_session(get_response):
    """Middleware to allow a user to authenticate against "/o/authorize" only once."""

    def middleware(request):
        # Code executed for each request before the view (and later middleware) are called.
        if not request.user.is_authenticated:
            # If user is not authenticated, proceed:
            # this is not this middleware's concern
            return get_response(request)

        # Check if the auth backend is stored in session
        auth_backend = request.session.get(BACKEND_SESSION_KEY)

        if auth_backend != "mailbox_oauth2.backends.MailboxModelBackend":
            # If the backend is not MailboxModelBackend, proceed:
            # this is not this middleware's concern
            return get_response(request)

        # Allow access only to /o/authorize path
        if request.path != reverse("oauth2_provider:authorize"):
            # Kill the session immediately
            request.session.flush()
            raise SuspiciousSession(
                "Session was killed because user tried to access unauthorized path"
            )

        response = get_response(request)

        # Code executed for each request/response after the view is called.
        # When the response is a 200, the user might still be in the authentication flow
        # otherwise, we can kill the session as the current login process is done,
        # the user will be authenticated again when coming back from the OIDC federation.
        # We preserve the oidc_states for the case when the user wants to access people
        # in the first place (people -> keycloak -> people login -> keycloak -> people)
        if response.status_code != 200:
            state = request.session.get("oidc_states")
            request.session.flush()
            if state:
                request.session["oidc_states"] = state

        return response

    return middleware
