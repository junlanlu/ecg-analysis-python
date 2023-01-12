from pymodm import connect, MongoModel, fields
from pymongo import MongoClient
import requests
from PIL import Image, ImageTk
import numpy as np
import base64

server_address = 'http://127.0.0.1:5000'


def test_convert_ndarray_to_b64_string():
    from patient_client import convert_ndarray_to_b64_string
    test_img = Image.open('images/test_image.jpg')
    test_img_ndarray = np.array(test_img)
    b64str = convert_ndarray_to_b64_string(test_img_ndarray)
    assert b64str[0:20] == "iVBORw0KGgoAAAANSUhE"


def test_convert_b64_string_to_ndarray():
    from monitor_client import convert_b64_string_to_ndarray
    from patient_client import convert_ndarray_to_b64_string
    test_img = Image.open('images/test_image.jpg')
    test_img_ndarray = np.array(test_img)
    b64str = convert_ndarray_to_b64_string(test_img_ndarray)
    result = convert_b64_string_to_ndarray(b64str)
    assert (result == test_img_ndarray).all


def test_download_image_from_server():
    from monitor_client import download_image_from_server
    from patient_client import convert_ndarray_to_b64_string
    import filecmp
    import os
    test_img = Image.open("images/test_image.jpg")
    with open("images/test_image.jpg", 'rb') as test_img:
        test_img_b64 = base64.b64encode(test_img.read())
    download_image_from_server(test_img_b64, "images/test_image2.jpg")
    result = filecmp.cmp("images/test_image.jpg",
                         "images/test_image2.jpg")
    os.remove("images/test_image2.jpg")
    assert result is True
