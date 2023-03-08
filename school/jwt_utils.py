from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


def retrieve_id(token):

    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user_id = validated_token['user_id']
    except:
        raise AuthenticationFailed('Invalid or expired token')

    return user_id
