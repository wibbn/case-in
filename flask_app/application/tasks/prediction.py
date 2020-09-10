from datetime import datetime
from application import celery
from ..models import Machine, MachineErrors, MachineMaintenance, MachineTelemetry

@celery.task
def predict_machine_failure():
    for machine in Machine.objects:
        request = dict()
        request["age"] = (datetime.utcnow() - machine.manufacture_date).days // 365
        request["delt_comp1"] = (datetime.utcnow() - MachineMaintenance
