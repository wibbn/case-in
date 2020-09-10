from flask import jsonify
from flask_restx import Resource
from flask_jwt_extended import jwt_required
from application import cache
from application.tasks.main import simple_task
from . import api


@api.route("/")
class Main(Resource):
    @jwt_required
    @cache.cached()
    def get(self):
        result = simple_task.delay()
        return jsonify({"message": result.get(timeout=1)})
