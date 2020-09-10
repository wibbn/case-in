from flask_restx import Resource, Namespace, reqparse, fields, abort
from flask_restx._http import HTTPStatus
from flask_restx.inputs import email
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from application import app, jwt, redis
from application.models import User

# Namespace

auth_ns = Namespace("Authentication", path="/token",
                    description="Authentication with JWT tokens")

# Parsers

auth_parser = reqparse.RequestParser()
auth_parser.add_argument("email", type=email(), required=True, location="json",
                         help="Email cannot be empty.")
auth_parser.add_argument("password", type=str, required=True, location="json",
                         help="Password cannot be empty.")

# Models

token_model = auth_ns.model("Tokens", {
    "access_token": fields.String,
    "refresh_token": fields.String,
})

access_token_model = auth_ns.model("AccessToken", {
    "access_token": fields.String,
})

refresh_token_model = auth_ns.model("RefreshToken", {
    "refresh_token": fields.String,
})


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.objects.get(id=identity)


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token["jti"]
    entry = redis.get(jti)
    if entry is None:
        return False
    else:
        return entry == "true"

# Resources


@auth_ns.route("")
class Token(Resource):
    @auth_ns.expect(auth_parser)
    @auth_ns.marshal_with(token_model)
    def post(self):
        args = auth_parser.parse_args()
        user = User.objects.get_or_404(email=args["email"])
        if not user.verify_password(args["password"]):
            abort(HTTPStatus.UNAUTHORIZED)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, HTTPStatus.CREATED


@auth_ns.route("/refresh")
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    @auth_ns.marshal_with(access_token_model)
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {
            "access_token": access_token
        }, 200


@auth_ns.route("/revoke_access")
class TokenRevokeAccess(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()["jti"]
        redis.set(jti, "true", app.config["JWT_ACCESS_TOKEN_EXPIRES"] * 1.2)
        return {"message": "Access token revoked successfully"}


@auth_ns.route("/revoke_refresh")
class TokenRevokeRefresh(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()["jti"]
        redis.set(jti, "true", app.config["JWT_REFRESH_TOKEN_EXPIRES"] * 1.2)
        return {"message": "Refresh token revoked successfully"}
