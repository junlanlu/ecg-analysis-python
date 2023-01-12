from pymodm import connect, MongoModel, fields
from pymodm import errors as pymodm_errors


class Patient(MongoModel):
    patient_name = fields.CharField()
    mrn = fields.IntegerField(primary_key=True)
    medical_image = fields.ListField()
    ecg_image = fields.ListField()
    entry_time = fields.ListField()
    heart_rate = fields.ListField()
