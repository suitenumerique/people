"""Define here some fake responses from Matrix API, useful to mock responses in tests."""

from rest_framework import status


# SEARCH
def mock_search_empty():
    """Mock response when no Matrix user has been found through search."""
    return {
        "message": {"limited": "false", "results": []},
        "status_code": status.HTTP_200_OK,
    }


def mock_search_successful(user):
    """Mock response when exactly one user has been found through search."""
    return {
        "message": {
            "limited": "false",
            "results": [
                {
                    "user_id": f"@{user.email.replace('@', '-')}:user_server.com",
                    "display_name": f"@{user.name} [Fake]",
                    "avatar_url": "null",
                },
            ],
        },
        "status_code": status.HTTP_200_OK,
    }


def mock_search_successful_multiple(user):
    """Mock response when more than one user has been found through search."""
    return {
        "message": {
            "limited": "false",
            "results": [
                {
                    "user_id": f"@{user.email.replace('@', '-')}:user_server1.com",
                    "display_name": f"@{user.name} [Fake]",
                    "avatar_url": "null",
                },
                {
                    "user_id": f"@{user.email.replace('@', '-')}:user_server2.com",
                    "display_name": f"@{user.name} [Other Fake]",
                    "avatar_url": "null",
                },
            ],
        },
        "status_code": status.HTTP_200_OK,
    }


# JOIN ROOMS
def mock_join_room_successful(room_id):
    """Mock response when succesfully joining room. Same response if already in room."""
    return {"message": {"room_id": str(room_id)}, "status_code": status.HTTP_200_OK}


def mock_join_room_no_known_servers():
    """Mock response when room to join cannot be found."""
    return {
        "message": {"errcode": "M_UNKNOWN", "error": "No known servers"},
        "status_code": status.HTTP_404_NOT_FOUND,
    }


def mock_join_room_forbidden():
    """Mock response when room cannot be joined."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": "You do not belong to any of the required rooms/spaces to join this room.",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }


# INVITE USER
def mock_invite_successful():
    """Mock response when invite request was succesful. Does not check the user exists."""
    return {"message": {}, "status_code": status.HTTP_200_OK}


def mock_invite_user_already_in_room(user):
    """Mock response when invitation forbidden for People user."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": f"{user.email.replace('@', '-')}:home_server.fr is already in the room.",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }


# KICK USER
def mock_kick_successful():
    """Mock response when succesfully joining room."""
    return {"message": {}, "status_code": status.HTTP_200_OK}


def mock_kick_user_forbidden(user):
    """Mock response when kick request is forbidden (i.e. wrong permission or user is room admin."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": f"You cannot kick user @{user.email.replace('@', '-')}.",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }


def mock_kick_user_not_in_room():
    """
    Mock response when trying to kick a user who isn't in the room. Don't check the user exists.
    """
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": "The target user is not in the room",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }
