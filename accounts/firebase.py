import os
import logging
import base64
import json
import tempfile

logger = logging.getLogger(__name__)


def _init_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:

        # ✅ Production (Render) — read from base64 env var
        b64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")
        if b64:
            try:
                decoded = base64.b64decode(b64).decode("utf-8")
                json.loads(decoded)  # validate JSON
                tmp = tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=".json",
                    delete=False,
                    prefix="firebase_",
                )
                tmp.write(decoded)
                tmp.close()
                cred = credentials.Certificate(tmp.name)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized from FIREBASE_CREDENTIALS_BASE64")
                return
            except Exception as e:
                logger.error("Failed to init Firebase from base64: %s", e)
                raise RuntimeError(f"Firebase base64 init failed: {e}")

        # ✅ Local development — read from file path
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
            "Set FIREBASE_CREDENTIALS_BASE64 on Render or "
            "FIREBASE_CREDENTIALS_PATH locally."
        )
    else:
        print("FIREBASE ALREADY INITIALIZED")
        logger.debug("Firebase already initialized")


def verify_id_token(token: str) -> dict:
    """Return decoded claims for a Firebase ID token."""

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

        logger.debug("Verifying Firebase ID token: %.30s", token)

        decoded = firebase_auth.verify_id_token(token)

        logger.info("Firebase token verified for: %s", decoded.get("email"))
        return decoded

    except Exception as err:
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
    