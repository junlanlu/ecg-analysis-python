from test_server_examples import validate_patient_info_examples
from test_server_examples import process_patient_info_examples
from test_server_examples import find_patient_in_db_examples
from test_server_examples import validate_get_patient_by_mrn_examples
import pytest
from Patient import Patient
from testfixtures import LogCapture
import datetime
from pymodm import connect, MongoModel, fields
from pymongo import MongoClient
import json
import requests
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from skimage.io import imsave


def test_init_db():
    from server import init_db
    from pymongo.errors import ConnectionFailure
    from pymongo.errors import ConfigurationError
    connected = True
    expected = True
    try:
        connect("mongodb+srv://junlanlu:Jl120998!@bme547.ocey0.mongodb.net/" +
                "cloud_db?retryWrites=true&w=majority")
    except ConnectionFailure:
        connected = False
    except ConfigurationError:
        connected = False
    assert connected == expected


@pytest.mark.parametrize("in_data, expected", process_patient_info_examples)
def test_process_patient_info(in_data, expected):
    from server import process_patient_info
    validate_input, server_status = process_patient_info(in_data)
    assert server_status == expected


def test_process_patient_info_mrnonly():
    from server import process_patient_info
    from server import find_patient_in_db
    in_data = {"patient_name": "",
               "mrn": "105",
               "ecg_image": "",
               "medical_image": "",
               "heart_rate": ""}
    validate_input, server_status = process_patient_info(in_data)
    expected = 200
    assert server_status == expected
    patient = find_patient_in_db(105)
    if patient is not False:
        patient.delete()


@pytest.mark.parametrize("in_data, expected", validate_patient_info_examples)
def test_validate_patient_info(in_data, expected):
    from server import validate_patient_info
    validate_input, server_status = validate_patient_info(in_data)
    assert server_status == expected


@pytest.mark.parametrize("mrn, expected", find_patient_in_db_examples)
def test_find_patient_in_db(mrn, expected):
    from server import find_patient_in_db
    db_item = find_patient_in_db(mrn)
    if db_item is not False:
        db_item = True
    assert db_item == expected


def test_add_new_patient_in_db():
    from server import add_new_patient_to_database
    from server import find_patient_in_db
    mrn = 103
    add_new_patient_to_database(mrn)
    assert find_patient_in_db(mrn) is not False


def test_add_patient_info_in_db():
    from server import add_patient_info_to_database
    from server import add_new_patient_to_database
    from server import find_patient_in_db
    new_patient = {"patient_name": "john", "mrn": 104,
                   "medical_image": 'cdf',
                   "ecg_image": 'abc',
                   "heart_rate": 70}
    add_new_patient_to_database(mrn=104)
    patient = find_patient_in_db(mrn=104)
    updated_patient = add_patient_info_to_database(patient, new_patient)
    assert find_patient_in_db(mrn=104) is not False
    assert new_patient['medical_image'] in updated_patient.medical_image
    assert new_patient['heart_rate'] in updated_patient.heart_rate
    assert new_patient['ecg_image'] in updated_patient.ecg_image


def test_get_available_mrns():
    from server import process_get_available_mrns
    from server import add_new_patient_to_database
    add_new_patient_to_database(mrn=999)
    add_new_patient_to_database(mrn=998)
    add_new_patient_to_database(mrn=997)
    mrns = process_get_available_mrns()
    assert 999 in mrns
    assert 998 in mrns
    assert 997 in mrns


@pytest.mark.parametrize("mrn, patient_info, expected",
                         validate_get_patient_by_mrn_examples)
def test_validate_get_patient_by_mrn(mrn, patient_info, expected):
    from server import validate_get_patient_by_mrn
    from server import add_patient_info_to_database
    from server import add_new_patient_to_database

    if type(expected) is not str:
        patient = add_new_patient_to_database(mrn=mrn)
        add_patient_info_to_database(patient, patient_info)
    found_result = validate_get_patient_by_mrn(mrn)
    assert found_result == expected


@pytest.mark.parametrize("mrn, expected", [
    (1001, "Patient not found"),
    (10000, "Patient not found"),
])
def test_validate_get_patient_by_mrn_not_in_db(mrn, expected, dummy_mongodb):
    from server import validate_get_patient_by_mrn
    from server import find_patient_in_db

    while find_patient_in_db(mrn):
        mrn = mrn+1
    found_result = validate_get_patient_by_mrn(mrn)
    assert found_result == expected


dummy_pt_1 = Patient(
    mrn=150,
    patient_name="James",
    medical_image=["img1", "img2"],
    ecg_image=["ecg1", "ecg2"],
    entry_time=["ts1", "ts2"],
    heart_rate=[123, 60],
)

dummy_pt_2 = Patient(
    mrn=152,
)

dummy_pt_3 = Patient(
    mrn=152,
    patient_name="John",
    heart_rate=[123, 60],
)

dummy_pt_4 = Patient(
    mrn=152,
    ecg_image=["ecg1", "ecg2"],
    heart_rate=[123, 60],
)


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, {
        "name": "James",
        "latest_hr": 60,
        "latest_ecg": "ecg2",
        "entry_time": "ts2",
    }),
    (dummy_pt_2, {
        "name": None,
        "latest_hr": None,
        "latest_ecg": None,
        "entry_time": None,
    }),
    (dummy_pt_3, {
        "name": "John",
        "latest_hr": 60,
        "latest_ecg": None,
        "entry_time": None,
    }),
    (dummy_pt_4, {
        "name": None,
        "latest_hr": 60,
        "latest_ecg": "ecg2",
        "entry_time": None,
    }),
])
def test_extract_latest_from_pt(patient, expected):
    from server import extract_latest_from_pt
    result = extract_latest_from_pt(patient)
    assert result == expected


@pytest.mark.parametrize("mrn, expected, code", [
    (100, {
        "name": "James",
        "latest_hr": 60,
        "latest_ecg": "ecg2",
        "entry_time": "ts2",
    }, 200),
    (101, {
        "name": None,
        "latest_hr": None,
        "latest_ecg": None,
        "entry_time": None,
    }, 200),
    ("102", {
        "name": "John",
        "latest_hr": 60,
        "latest_ecg": None,
        "entry_time": None,
    }, 200),
    (103, {
        "name": None,
        "latest_hr": 60,
        "latest_ecg": "ecg2",
        "entry_time": None,
    }, 200),
    ("onehundred", "Invalid MRN format", 400),
    ([120], "Invalid MRN format", 400),
    (900, "Patient not found", 400),
])
def test_get_name_and_latest_for_pt(mrn, expected, code, dummy_mongodb):
    from server import get_name_and_latest_for_pt
    result, status_code = get_name_and_latest_for_pt(mrn)
    assert result == expected
    assert status_code == code


@pytest.mark.parametrize("patient, timestamp, expected", [
    (dummy_pt_1, "ts1", "ecg1"),
    (dummy_pt_2, "ts2", "Error finding ECG"),
    (dummy_pt_1, "ts2", "ecg2"),
    (dummy_pt_1, "ts3", "Error finding ECG"),
])
def test_process_get_ecg_by_timestamp(patient, timestamp, expected):
    from server import process_get_ecg_by_timestamp
    result, status_code = process_get_ecg_by_timestamp(patient, timestamp)
    assert result == expected


@pytest.mark.parametrize("patient, img_id, expected", [
    (dummy_pt_1, 0, "img1"),
    (dummy_pt_1, 1, "img2"),
    (dummy_pt_2, 1, "Error finding Medical Image"),
])
def test_process_get_image_by_id(patient, img_id, expected):
    from server import process_get_image_by_id
    result, status_code = process_get_image_by_id(patient, img_id)
    assert result == expected


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, [0, 1]),
    (dummy_pt_2, []),
])
def test_process_get_all_medical_img(patient, expected):
    from server import process_get_all_medical_img
    result = process_get_all_medical_img(patient)
    assert result == expected
