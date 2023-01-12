from flask import Flask, request, jsonify
import logging
from pymodm import connect, MongoModel, fields
import pymodm
from pymodm import errors as pymodm_errors
from Patient import Patient
from helpers import validate_post_input, validate_mrn
from helpers import get_last_ecg, get_last_hr, get_patient_name
from helpers import get_patient_timestamp
from helpers import get_ecg_timestamps, get_ecg_by_timestamp
from helpers import get_medical_image_by_index
import json
import requests
import base64
import io
import datetime
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from skimage.io import imsave
import pdb
import os

app = Flask(__name__)


def init_db():
    """Connect to the mongodb database

    Function connects to the MongoDB database called cloud_db

    :param: None

    :returns: None
    """
    logging.basicConfig(filename="cloudserver_db.log",
                        filemode="w", level=logging.DEBUG)
    print("Connecting to MongoDB")
    connect("mongodb+srv://junlanlu:Jl120998!@bme547.ocey0.mongodb.net/" +
            "cloud_db?retryWrites=true&w=majority")
    print("Connected")


@app.route("/new_patient_info", methods=["POST"])
def post_new_patient_info():
    """Server post request for adding new patient information to the patient
    patient databse

    Function gets the json file from the post request and processes
    the new patient information. Accept uploads from the patient-side client
    that will include, at a minimum, the medical record number. The upload may
    also include a name, medical image, and/or heart rate & ECG image.
    If the data passes the validation function, it is added to the patients_db
    database.

    :param: None

    :returns: message after posting new patient information, server status
    """
    in_data = request.get_json()
    answer, server_status = process_patient_info(in_data)
    return answer, server_status


def process_patient_info(in_data):
    """Processes patient data

    Processes the new patient in_data by first validating. If validation passes
    the patient is added to the mongodb database by calling
    add_patient_to_database. Adds logging if added succesfully

    :param in_data: dict of the input data from the post request
    /api/new_patient_info

    :returns: message after processing, server status
    """
    validate_input, server_status = validate_patient_info(in_data)
    if validate_input is not True:
        return validate_input, server_status
    patient = find_patient_in_db(int(in_data['mrn']))
    if patient is False:
        patient = add_new_patient_to_database(int(in_data['mrn']))
    patient = add_patient_info_to_database(patient, in_data)
    return "Patient information successfully added", 200


def validate_patient_info(in_data):
    """Validates the new patient information

    Function validates the json file to contain the correct keys
    and the correct types for "patient_name", "mrn", "medical_image",
    "ecg_image", "heart_rate"

    :param in_data: dict of the input data from the post request
    /api/new_patient_info

    :returns: message after validation , server status
    """
    expected_key = ["patient_name", "mrn",
                    "medical_image", "ecg_image", "heart_rate"]
    expected_types = [[str], [int, str], [str], [str], [int, str]]
    validate_input = validate_post_input(expected_key, expected_types, in_data)
    if validate_input is not True:
        return validate_input, 400
    for key in ["mrn", "heart_rate"]:
        if in_data[key] is not '':
            try:
                int(in_data[key])
            except ValueError:
                key_error = "{} has the wrong variable type".format(key)
                return key_error, 400
    if in_data['mrn'] is '':
        return "mrn is not valid", 400
    return True, 200


def find_patient_in_db(mrn):
    """Find the patient in the database or return False

    Finds the patient in the database by the mrn. If the patient
    does not exist, return False

    :param mrn: medical record number of the patient in integer format

    :returns: patient object
    """
    try:
        db_item = Patient.objects.raw({"_id": mrn}).first()
    except pymodm_errors.DoesNotExist:
        return False
    return db_item


def add_new_patient_to_database(mrn):
    """Adds the new patient to the database by primary key mrn

    Adds the new patient to the MongoDB database by primary key mrn

    :param mrn: patient medical record number

    :returns: Saved patient object
    """
    new_patient = Patient(mrn=mrn)
    saved_patient = new_patient.save()
    logging.info("Added patient {}".format(mrn))
    return saved_patient


def add_patient_info_to_database(patient, in_data):
    """Adds the new patient info to the database

    Adds the new patient information to the MongoDB database. If the entry
    is empty (GUI client did not provide any valid information), the
    information will not be added

    :param patient: From MongoDB patient class defined
    :param in_data: dict of the input data from the post request
    /api/new_patient_info

    :returns: Updated patient
    """
    timestamp = str(datetime.datetime.now()).split('.')[0]
    if in_data['patient_name'] is not '' and patient.patient_name is None:
        patient.patient_name = in_data['patient_name']
    if in_data['medical_image'] is not '':
        patient.medical_image.append(in_data['medical_image'])
    if in_data['ecg_image'] is not '':
        patient.ecg_image.append(in_data['ecg_image'])
        patient.entry_time.append(timestamp)
    if in_data['heart_rate'] is not '':
        patient.heart_rate.append(int(in_data['heart_rate']))
    updated_patient = patient.save()
    return updated_patient


@app.route("/mrn_list", methods=["GET"])
def get_available_mrns():
    """Route to get a list of all available MRNs in the DB

    Accepts no input. Connects to the database, returns a
    list of all valid Medical Record Numbers for all
    patients.

    :returns: jsonified list of valid MRNs contained in database
    """
    patients = process_get_available_mrns()
    # print(patients)
    return jsonify(data=patients, code=200)


def process_get_available_mrns():
    """Return list of all Medical Record Numbers

    Accepts no input. Connects to the database, returns a
    list of all valid Medical Record Numbers for all
    patients.

    :returns: list of valid MRNs contained in database
    """
    patients = []
    for patient in Patient.objects.raw({}):
        patients.append(patient.mrn)
    return patients


@app.route("/<mrn>/most_recent", methods=["GET"])
def get_name_and_latest_for_pt(mrn):
    """Route to fetch latest data for a given patient

    Accepts a patient MRN, and acquires the patient name, last
    reported heart rate, and last uploaded ECG image. This is
    expected to be called by the monitoring station client.

    :param mrn: int, str, valid medical record number for a patient
    :returns: JSON with entries:
            `name`: patient name
            `latest_hr`: last recorded patient heart rate
            `latest_ecg`: last uploaded ECG image
    """
    patient = validate_get_patient_by_mrn(mrn)
    if type(patient) is str:
        return patient, 400
    return_info = extract_latest_from_pt(patient)
    return return_info, 200


def extract_latest_from_pt(patient):
    """Accepts a patient object, returns most recent information

    Accepts a patient database entry, returns the last recorded
    heart rate, ECG image, and the patient's name, and entry timestamp.

    :param patient: Patient object (MongoDB entry)
    :returns: dict with entries:
            `name`: patient name
            `latest_hr`: last recorded patient heart rate
            `latest_ecg`: last uploaded ECG image
            `entry_time`: last entry timestamp
    """
    patient_hr = get_last_hr(patient)
    patient_ecg = get_last_ecg(patient)
    patient_name = get_patient_name(patient)
    patient_timestamp = get_patient_timestamp(patient)

    return_info = {
        "name": patient_name,
        "latest_hr": patient_hr,
        "latest_ecg": patient_ecg,
        "entry_time": patient_timestamp,
    }
    return return_info


def validate_get_patient_by_mrn(mrn):
    """Validate supplied mrn, retrieve patient if valid.

    Checks if the supplied medical record number is valid,
    attempts to retrieve this patient from the database if
    so. If mrn invalid, or not in database, returns an
    error message. Otherwise, returns the patient object.

    :param mrn: int, str medical record number
    :returns: str, error message or Patient object
    """
    mrn = validate_mrn(mrn)
    if mrn is False:
        return "Invalid MRN format"
    patient = find_patient_in_db(mrn)
    if patient is False:
        return "Patient not found"
    return patient


@app.route("/<mrn>/ecg/timestamps", methods=["GET"])
def get_patient_ecg_times(mrn):
    """Return list of all ECG timestamps for the provided patient

    Validates the patient MRN, returns an error code if not valid,
    or if not found. Otherwise, returns the list of ECG timestamps
    (returns empty JSONified list if nothing uploaded).

    :param mrn: int, str medical record number
    :returns: JSONified list of timestamps, server code
             OR returns error message and failure code
    """
    patient = validate_get_patient_by_mrn(mrn)
    if type(patient) is str:
        return patient, 400
    timestamps = get_ecg_timestamps(patient)
    return jsonify(timestamps), 200


def process_get_ecg_by_timestamp(patient, timestamp):
    """Return specific ECG image based on selected timestamp.

    Accepts validated patient object and a timestamp. Returns
    ECG image corresponding to the timestamp, or the appropriate
    error message.

    :param patient: Patient object (MongoDB entry)
    :param timestamp: str representation of a valid timestamp
    :returns: ECG image corresponding to timestamp, error message if not found
    """
    ecg = get_ecg_by_timestamp(patient, timestamp)
    if ecg is not None:
        return ecg, 200
    else:
        return "Error finding ECG", 400


@app.route("/<mrn>/ecg/<timestamp>", methods=["GET"])
def get_ecg_at_timestamp(mrn, timestamp):
    """Return specific ECG image based on selected timestamp.

    Validates the MRN and the timestamp, then returns the
    selected image data corresponding to that timestamp.

    :param mrn: int, str medical record number
    :param timestamp: str, timestamp
    :returns: None if no image found, appropriate error message if there
             are errors, or image data corresponding to input
    """
    patient = validate_get_patient_by_mrn(mrn)
    if type(patient) is str:
        return patient, 400
    result, status_code = process_get_ecg_by_timestamp(patient, timestamp)
    return jsonify(result=result, code=status_code)


def process_get_image_by_id(patient, img_id):
    """Process the validated patient object, return requested image.

    Returns a medical image from the patient record by id (index).
    Returns the appropriate error messages and codes if the image
    does not exist or is not found.

    :param patient: Patient object (MongoDB entry)
    :param img_id: int, index of medical image requested
    :returns: None if no image found, appropriate error message if there
             are errors, or image data corresponding to input
    """
    img = get_medical_image_by_index(patient, int(img_id))
    if img is not None:
        return img, 200
    else:
        return "Error finding Medical Image", 400


@app.route("/<mrn>/images/<img_id>", methods=["GET"])
def get_image_by_id(mrn, img_id):
    """Return medical image by ID (index in the record)

    Return the medical image for a given patient, by 'image id',
    or the index of the image in the patient record for medical images.

    :param mrn: int, str medical record number
    :param img_id: int, index of medical image requested
    :returns: None if no image found, appropriate error message if there
             are errors, or image data corresponding to input
    """
    patient = validate_get_patient_by_mrn(mrn)
    if type(patient) is str:
        return patient, 400
    result, status_code = process_get_image_by_id(patient, img_id)
    # print(result)
    return jsonify(result=result, code=status_code)


def process_get_all_medical_img(patient):
    """Process the validated patient object, return list of all images.

    Returns a list of medical images from the patient record.
    List is returned as a list of indices.

    :param patient: Patient object (MongoDB entry)
    :returns: Empty list if no images, or list of images (by index).
    """
    if len(patient.medical_image) > 0:
        result = [x for x in range(0, len(patient.medical_image))]
        # print(result)
        return result
    else:
        # print("Fail")
        return []


@app.route("/<mrn>/images", methods=["GET"])
def get_all_images(mrn):
    """Return all medical images for a patient

    Return all medical images for a given patient, or an empty list
    if none found.

    :param mrn: int, str medical record number
    :returns: Empty list if no images found, list of image files
             otherwise
    """
    patient = validate_get_patient_by_mrn(mrn)
    if type(patient) is str:
        return patient, 400
    result = process_get_all_medical_img(patient)
    return jsonify(result=result, code=200)


if __name__ == "__main__":
    init_db()
    app.run()
    get_available_mrns()
