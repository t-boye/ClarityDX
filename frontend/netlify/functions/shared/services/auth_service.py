from firebase_admin import verify_token

def authenticate_user(id_token):
    return verify_token(id_token)