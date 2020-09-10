from flask_restx import Resource, Namespace, abort
# noinspection PyProtectedMember
from flask_restx._http import HTTPStatus
from application.models import User as UserModel
from .users import post_user_parser

# Namespace

register_ns = Namespace("Register", description="Register a new user", path="/register")

# Parsers

register_user_parser = post_user_parser.copy()
register_user_parser.remove_argument("is_active")

# Resources


@register_ns.route("")
class Register(Resource):
    @register_ns.expect(post_user_parser)
    @register_ns.response(HTTPStatus.CREATED,
                          HTTPStatus.CREATED.phrase)
    @register_ns.response(HTTPStatus.BAD_REQUEST,
                          HTTPStatus.BAD_REQUEST.phrase)
    def post(self):
        args = post_user_parser.parse_args()
        if UserModel.objects(email=args["email"]).count():
            abort(code=HTTPStatus.BAD_REQUEST, message="User with such email already exists")
        user = UserModel(**args)
        user.save()
        return {"message": "User was successfully created"}, HTTPStatus.CREATED
