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


def upload_patient_info(patient_name, mrn, heart_rate, med_img, ecg_img):
    """Post request to server to upload the patient information

    User selects image file from dialog box and the image is
    resized and displayed on the GUI.

    :param patient_name: patient name
    :param mrn: patient medical record number
    :param heart_rate: patient heart rate from ecg trace
    :param med_img: PIL image of medical image from the GUI
    :param ecg_img: PIL image of ecg image from the GUI

    :returns: server status code
    """
    if(med_img is not None):
        med_img_b64_string = convert_ndarray_to_b64_string(np.array(med_img))
    else:
        med_img_b64_string = ''
    if(ecg_img is not None):
        ecg_img_b64_string = convert_ndarray_to_b64_string(np.array(ecg_img))
    else:
        ecg_img_b64_string = ''
    new_patient_info = {"patient_name": patient_name, "mrn": mrn,
                        "medical_image": med_img_b64_string,
                        "ecg_image": ecg_img_b64_string,
                        "heart_rate": heart_rate, }

    r = requests.post(server_address+"/new_patient_info",
                      json=new_patient_info)
    return r.status_code


def convert_ndarray_to_b64_string(img_ndarray):
    """Convert ndarray to base64 string

    User selects image file from dialog box and the image is
    resized and displayed on the GUI.

    :param img_ndarray: an n-dimensional numpy array representing the image

    :returns: base64 string of the img_ndarray
    """
    f = io.BytesIO()
    imsave(f, img_ndarray, plugin='pil')
    y = base64.b64encode(f.getvalue())
    b64_string = str(y, encoding='utf-8')
    return b64_string


if __name__ == '__main__':
    new_patient = {"patient_name": "", "mrn": 2,
                   "medical_image": '',
                   "ecg_image": 'abc',
                   "heart_rate": '72.0', }

    r = requests.post(
        server_address+"/new_patient_info", json=new_patient)
    print(r.status_code)
    print(r.text)

    new_patient = {"patient_name": "amy", "mrn": 101,
                   "medical_image": '',
                   "ecg_image": 'abc',
                   "heart_rate": 70}

    r = requests.post(
        server_address+"/new_patient_info", json=new_patient)
    print(r.status_code)
    print(r.text)

    new_patient = {"patient_name": "bob", "mrn": 101,
                   "medical_image": '',
                   "ecg_image": 'abc',
                   "heart_rate": 70}

    r = requests.post(
        server_address+"/new_patient_info", json=new_patient)
    print(r.status_code)
    print(r.text)

    new_patient = {"mrn": 101,
                   "medical_image": 'a',
                   "ecg_image": '',
                   "heart_rate": ''}

    r = requests.post(
        server_address+"/new_patient_info", json=new_patient)
    print(r.status_code)
    print(r.text)

    med_img = Image.open('images/test_image.jpg')
    med_img_ndarray = np.array(med_img)
    print(convert_ndarray_to_b64_string(med_img_ndarray)[0:20])
