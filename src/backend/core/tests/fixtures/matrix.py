"""Define here some fake data from matrix, useful to mock response"""

from rest_framework import status


# JOIN ROOMS
def mock_ok_room_joined(room_id):
    """Mock Matrix response when succesfully joining room."""
    return {"message": {"room_id": str(room_id)}, "status_code": status.HTTP_200_OK}


# INVITE USER
def mock_invite_successful():
    """Mock Matrix response when invite request was succesful."""
    return {"message": {}, "status_code": status.HTTP_200_OK}


def mock_invite_user_to_room_already_in_room(user_id):
    """Mock Matrix response when invitation forbidden for People user."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": f"{user_id} is already in the room.",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }


# KICK USER
def mock_kick_successful():
    """Mock Matrix response when succesfully joining room."""
    return {"message": {}, "status_code": status.HTTP_200_OK}


def mock_kick_user_from_room_forbidden(user_id):
    """Mock Matrix response when kick request is forbidden (i.e. wrong permission or user is room admin."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": f"You cannot kick user @{user_id}.",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }


def mock_kick_user_not_in_room():
    """Mock Matrix when trying to kick a user who isn't in the room."""
    return {
        "message": {
            "errcode": "M_FORBIDDEN",
            "error": "The target user is not in the room",
        },
        "status_code": status.HTTP_403_FORBIDDEN,
    }
