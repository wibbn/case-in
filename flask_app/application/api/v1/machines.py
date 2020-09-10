from flask_restx import Resource, Namespace, reqparse, fields, abort
# noinspection PyProtectedMember
from flask_restx._http import HTTPStatus
from flask_restx.inputs import datetime_from_iso8601
from flask_jwt_extended import jwt_required, current_user
from application.models import Machine as MachineModel, MachineErrors as MachineErrorsModel, \
    MachineMaintenance as MachineMaintenanceModel, MachineModel as MachineModelModel, \
    MachinePart as MachinePartModel, MachineTelemetry as MachineTelemetryModel
from .api_models import pagination_model
from .parsers import paging_parser

# Namespace

machine_ns = Namespace("Machine", description="Machine endpoint", path="/machines",
                     decorators=[jwt_required])

# Parsers

machine_parser = reqparse.RequestParser()
machine_parser.add_argument("name", type=str, location="json",
                            store_missing=False, help="Machine name")
machine_parser.add_argument("manufacture_date", type=datetime_from_iso8601, location="json",
                            store_missing=False, help="Machine manufacture date")

post_machine_parser = machine_parser.copy()
post_machine_parser.replace_argument("name", type=str, location="json",
                                     required=True, help="Machine name")
post_machine_parser.replace_argument("manufacture_date", type=datetime_from_iso8601, location="json",
                                     required=True, help="Machine manufacture date")

machine_telemetry_parser = reqparse.RequestParser()
machine_telemetry_parser.add_argument("voltage", type=float, location="json",
                                      store_missing=False, help="machine voltage")
machine_telemetry_parser.add_argument("vibration", type=float, location="json",
                                      store_missing=False, help="machine vibration")
machine_telemetry_parser.add_argument("pressure", type=float, location="json",
                                      store_missing=False, help="machine pressure")
machine_telemetry_parser.add_argument("rotation", type=float, location="json",
                                      store_missing=False, help="machine rotation")

# Models

def get_telemetry(instance):
    db_telemetry = MachineTelemetryModel.objects(machine=instance).order_by("+date").limit(64)
    telemetry = {
        "voltage": [],
        "vibration": [],
        "pressure": [],
        "rotation": [],
    }
    for t in db_telemetry:
        telemetry["voltage"].append(t.voltage)
        telemetry["vibration"].append(t.vibration)
        telemetry["pressure"].append(t.pressure)
        telemetry["rotation"].append(t.rotation)
    return telemetry

machine_telemetry_model = machine_ns.model("MachineTelemetry", {
    "voltage": fields.List(fields.Float),
    "vibration": fields.List(fields.Float),
    "pressure": fields.List(fields.Float),
    "rotation": fields.List(fields.Float),
})

machine_model_model = machine_ns.model("MachineModel", {
    "name": fields.String,
    "manufaturer": fields.String,
})

machine_part_model = machine_ns.model("MachinePart", {
    "name": fields.String,
    "quantity": fields.Integer
})

machine_errors_model = machine_ns.model("MachineErrors", {
    "error_type": fields.String,
    "date": fields.DateTime
})

machine_maintenance_model = machine_ns.model("MachineMaintenance", {
    "date": fields.DateTime,
    "part": fields.Nested(machine_part_model)
})

machine_model = machine_ns.model("Machine", {
    "name": fields.String,
    "manufature_date": fields.DateTime,
    "model": fields.Nested(machine_model_model),
    "telemetry": fields.List(fields.Nested(machine_telemetry_model, attribute=get_telemetry)),
    "errors": fields.List(fields.Nested(machine_errors_model,
        attribute=lambda x: MachineErrorsModel.objects(machine=x).order_by("+date").limit(64))),
    "maintenance": fields.List(fields.Nested(machine_maintenance_model))
})

machines_model = machine_ns.inherit("Machines", pagination_model, {
    "machines": fields.List(fields.Nested(machine_model), attribute="items")
})

# Resources

@machine_ns.route("/")
class Machines(Resource):
    @machine_ns.marshal_with(machines_model)
    def get(self):
        args = paging_parser.parse_args()
        return MachineModel.objects.paginate(page=args["page"],
                                             per_page=args["per_page"])

    @machine_ns.marshal_with(machine_model)
    @machine_ns.expect(post_machine_parser)
    def post(self):
        args = post_machine_parser.parse_args()
        machine = MachineModel(**args)
        return machine.save()

# noinspection PyUnresolvedReferences
@machine_ns.route("/<machine_id>")
class Machine(Resource):
    @machine_ns.marshal_with(machine_model)
    @machine_ns.response(HTTPStatus.NOT_FOUND,
                         HTTPStatus.NOT_FOUND.phrase)
    def get(self, machine_id):
        return MachineModel.objects.get_or_404(id=machine_id)

    @machine_ns.marshal_with(machine_model)
    @machine_ns.expect(machine_parser)
    @machine_ns.response(HTTPStatus.NOT_FOUND,
                         HTTPStatus.NOT_FOUND.phrase)
    def patch(self, machine_id):
        args = machine_parser.parse_args()
        machine = MachineModel.objects.get_or_404(id=machine_id)
        machine.update(**args)
        machine.reload()
        return machine

    @machine_ns.response(HTTPStatus.NOT_FOUND,
                         HTTPStatus.NOT_FOUND.phrase)
    def delete(self, machine_id):
        machine = MachineModel.objects.get_or_404(id=machine_id)
        machine.delete()
        return {
            "message": "Machine was successfully deleted."
        }

@machine_ns.route("/<machine_id>/telemetry")
class MachineTelemetry(Resource):
    @machine_ns.expect(machine_telemetry_parser)
    @machine_ns.response(HTTPStatus.NOT_FOUND,
                         HTTPStatus.NOT_FOUND.phrase)
    def post(self):
        args = machine_telemetry_parser.parse_args()
        machine = MachineModel.objects.get_or_404(id=machine_id)
        telemetry = MachineTelemetryModel(machine=machine, **args)
        telemetry.save()
        return {
            "message": "Telemetry was saved successfully"
        }
