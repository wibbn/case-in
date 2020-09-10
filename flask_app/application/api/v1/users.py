from flask_restx import Resource, Namespace, reqparse, fields, abort
# noinspection PyProtectedMember
from flask_restx._http import HTTPStatus
from flask_restx.inputs import email
from flask_jwt_extended import jwt_required, current_user
from application.models import User as UserModel
from .api_models import pagination_model
from .parsers import paging_parser

# Namespace

users_ns = Namespace("Users", description="Users endpoint", path="/users",
                     decorators=[jwt_required])

# Parsers

user_parser = reqparse.RequestParser()
user_parser.add_argument("email", type=email(), location="json",
                         store_missing=False, help="Email of a user")
user_parser.add_argument("password", type=str, location="json",
                         store_missing=False, help="Password of a user")
user_parser.add_argument("first_name", type=str, location="json",
                         store_missing=False,
                         help="First name of a user")
user_parser.add_argument("last_name", type=str, location="json",
                         store_missing=False,
                         help="Second name of a user")
user_parser.add_argument("is_active", type=bool, location="json", default=True,
                         store_missing=False, help="Active or disabled user")

post_user_parser = user_parser.copy()
post_user_parser.replace_argument("email", type=email(), location="json",
                                  required=True, help="Email of a user")
post_user_parser.replace_argument("first_name", type=str, location="json",
                                  required=True, help="First name of a user")
post_user_parser.replace_argument("password", type=str, location="json",
                                  required=True, help="Password of a user")

# Models

user_model = users_ns.model("User", {
    "id": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "is_active": fields.Boolean,
    "avatar": fields.String(attribute=lambda x: x.avatar.url),
})

users_model = users_ns.inherit("Users", pagination_model, {
    "users": fields.List(fields.Nested(user_model), attribute="items")
})

# Resources


@users_ns.route("/")
class Users(Resource):
    @users_ns.marshal_with(users_model)
    def get(self):
        args = paging_parser.parse_args()
        return UserModel.objects.paginate(page=args["page"],
                                          per_page=args["per_page"])

    @users_ns.marshal_with(user_model)
    @users_ns.expect(post_user_parser)
    def post(self):
        args = post_user_parser.parse_args()
        if UserModel.objects(email=args["email"]).count():
            abort(code=HTTPStatus.BAD_REQUEST, message="User with such email already exists")
        user = UserModel(**args)
        return user.save()


# noinspection PyUnresolvedReferences
@users_ns.route("/<user_id>")
class User(Resource):
    @users_ns.marshal_with(user_model)
    @users_ns.response(HTTPStatus.NOT_FOUND,
                       HTTPStatus.NOT_FOUND.phrase)
    def get(self, user_id):
        return UserModel.objects.get_or_404(id=user_id)

    @users_ns.marshal_with(user_model)
    @users_ns.expect(user_parser)
    @users_ns.response(HTTPStatus.NOT_FOUND,
                       HTTPStatus.NOT_FOUND.phrase)
    def patch(self, user_id):
        args = user_parser.parse_args()
        user = UserModel.objects.get_or_404(id=user_id)
        user.update(**args)
        user.reload()
        return user

    @users_ns.response(HTTPStatus.NOT_FOUND,
                       HTTPStatus.NOT_FOUND.phrase)
    def delete(self, user_id):
        user = UserModel.objects.get_or_404(id=user_id)
        user.delete()
        return {
            "message": "User was successfully deleted."
        }
