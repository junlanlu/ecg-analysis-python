import pytest
from pymodm import connect
from Patient import Patient


@pytest.fixture(scope="module")
def dummy_mongodb():
    from pymongo.errors import ConnectionFailure
    from pymongo.errors import ConfigurationError
    connected = True
    expected = True
    try:
        connect("mongodb+srv://junlanlu:Jl120998!@bme547.ocey0.mongodb.net/" +
                "cloud_db_dummy?retryWrites=true&w=majority")
    except ConnectionFailure:
        connected = False
    except ConfigurationError:
        connected = False
    dummy1 = Patient(
        mrn=100,
        patient_name="James",
        medical_image=["img1", "img2"],
        ecg_image=["ecg1", "ecg2"],
        entry_time=["ts1", "ts2"],
        heart_rate=[123, 60],
    )

    dummy2 = Patient(
        mrn=101,
    )

    dummy3 = Patient(
        mrn=102,
        patient_name="John",
        heart_rate=[123, 60],
    )

    dummy4 = Patient(
        mrn=103,
        ecg_image=["ecg1", "ecg2"],
        heart_rate=[123, 60],
    )

    dummy1.save()
    dummy2.save()
    dummy3.save()
    dummy4.save()
    yield
    for pt in Patient.objects.raw({}):
        pt.delete()
