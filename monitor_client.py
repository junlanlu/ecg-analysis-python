import requests
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from skimage.io import imsave
import pdb
from PIL import Image, ImageTk
import numpy as np

server_address = 'http://vcm-17598.vm.duke.edu:5000'


def load_all_patients():  # pragma: no cover
    """GET request to server to load all patient MRNs

    GET request to the server to get all the MRNs entered
    in the database.

    :param:

    :returns: list of patient MRNs
    """
    r = requests.get(server_address+"/mrn_list").json()
    return r['data']


def load_patient_latest(mrn):  # pragma: no cover
    """GET request to the server, retrieve latest patient data

    Sends a GET request to the server for a specific patient MRN.
    Expects a JSON string containing the patient name, last measured
    heart rate/ECG image, and the timestamp for this ECG.

    :param mrn: int, patient MRN
    :return: dict, latest patient data:
             `name`: patient name
             `latest_hr`: last recorded patient heart rate
             `latest_ecg`: last uploaded ECG image
    """
    r = requests.get(server_address+f"/{mrn}/most_recent").json()
    return r


def load_list_of_ecg_timestamps(mrn):  # pragma: no cover
    """GET request to the server, retrieve list of patient ECG timestamps

    Sends a GET request to the server for a specific patient MRN. Expects
    a JSONified list with timestamps for all recorded ECG uploads. The
    list will be empty if there are no entries.

    :param mrn: int, patient MRN
    :return: list of ECG entry timestamps
    """
    r = requests.get(server_address+f"/{mrn}/ecg/timestamps").json()
    return r


def load_list_of_medical_images(mrn):  # pragma: no cover
    """GET request to the server, retrieve list of patient medical images

    Sends a GET request to the server for a specific patient MRN. Expects
    a JSONified list with indices for all recorded medical image uploads. The
    list will be empty if there are no entries.

    :param mrn: int, patient MRN
    :return: list of medical image entry indices
    """
    r = requests.get(server_address + f"/{mrn}/images").json()
    return r['result']


def load_ecg_by_timestamp(mrn, timestamp):  # pragma: no cover
    """GET request to the server, retrieve ECG image by timestamp

    Sends a GET request to the server for a specific patient MRN.
    Expects a JSON string with the image data for the selected ECG
    image (by timestamp).

    :param mrn: int, patient MRN
    :param timestamp: string, ECG image timestamp
    :return: string, encoded image data
    """
    r = requests.get(server_address + f"/{mrn}/ecg/{timestamp}").json()
    return r['result']


def load_img_by_id(mrn, img_id):  # pragma: no cover
    """GET request to the server, retrieve medical image by ID

    Sends a GET request to the server for a specific patient MRN.
    Expects a JSON string with the image data for the selected
    medical image (by image id).

    :param mrn: int, patient MRN
    :param img_id: int, medical image id
    :return: string, encoded image data
    """
    r = requests.get(server_address + f"/{mrn}/images/{img_id}").json()
    return r['result']


def convert_b64_string_to_ndarray(b64_string):
    """Converts a b64 string to an image ndarray

    Accepts a b64 string, and returns an ndarray with
    the image data ready for display by the UI

    :param b64_string: string variable containing the image
           bytes encoded as a base64 string
    :return: variable containing an ndarray with image data
    """
    image_bytes = base64.b64decode(b64_string)
    image_buf = io.BytesIO(image_bytes)
    img_ndarray = mpimg.imread(image_buf, format='JPG')
    return img_ndarray


def download_image_from_server(b64_string, filename):
    """Saves base64 image data to file

    Saves the base64 image data to an image file, after
    decoding the data.

    :param b64_string: base64 image data
    :param filename: str, filename to save to
    :return:
    """
    image_bytes = base64.b64decode(b64_string)
    print(filename)
    with open(filename, "wb") as out_file:
        out_file.write(image_bytes)


if __name__ == '__main__':  # pragma: no cover
    pt_list = load_all_patients()
    print(pt_list)
    for pt in pt_list:
        load_patient_latest(pt)
        x = load_list_of_ecg_timestamps(pt)
