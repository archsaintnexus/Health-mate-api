import os
import logging

logger = logging.getLogger(__name__)


def _init_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:
        candidate_paths = [
            os.getenv("FIREBASE_CREDENTIALS_PATH", ""),
            "./firebase-credentials.json",
            "./firebase-key.json",
        ]
        for cred_path in candidate_paths:
            print(f"TRYING PATH: {cred_path} | EXISTS: {os.path.exists(cred_path) if cred_path else False}")
            logger.debug(f"Trying Firebase credentials path: {cred_path}")

            if cred_path and os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    print(f"FIREBASE INITIALIZED WITH: {cred_path}")
                    logger.info(f"Firebase initialized with: {cred_path}")
                    return
                except Exception as e:
                    print(f"FAILED TO INIT WITH {cred_path}: {str(e)}")
                    logger.error(f"Failed to init Firebase with {cred_path}: {str(e)}")

        raise RuntimeError(
            "Firebase credentials not found. "
            "Set FIREBASE_CREDENTIALS_PATH to a valid JSON key file path."
        )
    else:
        print("FIREBASE ALREADY INITIALIZED")


def verify_id_token(token: str) -> dict:
    """Return decoded claims for a Firebase ID token.

    The Firebase SDK expects a *string* token.  During normal operation
    we receive this value from the client, but there have been intermittent
    production crashes where the value coming out of the REST framework
    serializer was not a string at all (e.g. a ``slice`` object).  When the
    underlying ``firebase_admin`` library receives anything other than a
    string it ends up attempting to use the value as a dictionary key which
    raises ``TypeError: unhashable type: 'slice'``.  That error bubbled up to
    our logs and resulted in a confusing ``400`` response.

    To avoid the problem we validate the argument type early and log
greater detail so developers can diagnose client errors.
    """

    # make sure the value is something sane before passing it to the
    # third‑party SDK; the earlier we catch bad input the easier it is to
    # trace back to the caller.
    if not isinstance(token, str):
        logger.error(
            "Expected Firebase token to be a string, got %r (type %s)",
            token,
            type(token).__name__,
        )
        raise ValueError("Firebase token must be a string.")

    try:
        from firebase_admin import auth as firebase_auth

        _init_firebase()

        # show a short preview of the token so we can correlate logs without
        # dumping the entire JWT (it can be quite long).
        logger.debug("Verifying Firebase ID token: %.30s", token)

        decoded = firebase_auth.verify_id_token(token)

        logger.info("Firebase token verified for: %s", decoded.get("email"))
        return decoded

    except Exception as err:
        # we still log the raw exception so it appears in container logs,
        # but surface a generic error to callers to avoid leaking internal
        # details.
        logger.error("Firebase token verification failed: %s", err)
        raise ValueError(f"Invalid Firebase token: {err}")
    


def update_user_password(uid: str, new_password: str) -> None:
    """
    Update a Firebase user's password.
    
    Args:
        uid: Firebase user UID
        new_password: New password to set
        
    Raises:
        ValueError: If update fails
    """
    try:
        from firebase_admin import auth as firebase_auth

        _init_firebase()

        firebase_auth.update_user(uid, password=new_password)
        print(f"PASSWORD UPDATED FOR UID: {uid}")
        logger.info(f"Firebase password updated for uid: {uid}")

    except Exception as err:
        print(f"FIREBASE PASSWORD UPDATE ERROR: {str(err)}")
        logger.error(f"Firebase password update failed for uid {uid}: {str(err)}")
        raise ValueError(f"Unable to update Firebase password: {str(err)}")


def delete_firebase_user(uid: str) -> None:
    """
    Delete a Firebase user account.
    
    Args:
        uid: Firebase user UID
        
    Raises:
        ValueError: If deletion fails
    """
    try:
        from firebase_admin import auth as firebase_auth

        _init_firebase()

        firebase_auth.delete_user(uid)
        print(f"FIREBASE USER DELETED: {uid}")
        logger.info(f"Firebase user deleted: {uid}")

    except Exception as err:
        print(f"FIREBASE DELETE ERROR: {str(err)}")
        logger.error(f"Firebase user deletion failed for uid {uid}: {str(err)}")
        raise ValueError(f"Unable to delete Firebase user: {str(err)}")


def get_firebase_user(uid: str) -> dict:
    """
    Get Firebase user record by UID.
    
    Args:
        uid: Firebase user UID
        
    Returns:
        Firebase user record
        
    Raises:
        ValueError: If user not found
    """
    try:
        from firebase_admin import auth as firebase_auth

        _init_firebase()

        user = firebase_auth.get_user(uid)
        return user

    except Exception as err:
        logger.error(f"Failed to get Firebase user {uid}: {str(err)}")
        raise ValueError(f"Unable to get Firebase user: {str(err)}")
    