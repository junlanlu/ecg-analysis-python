def validate_post_input(expected_keys, expected_types, data):
    """Checks an input data dictionary for correct keys/datatypes

    Accepts a dictionary containing POST request data, along with
    expected keys and types. Returns error message if input data
    does not pass validation, or `True` if successful.

    :param expected_keys: list of valid key names
    :param expected_types: list of expected data types
    :param data: dictionary of POST data to check

    :returns: True if successful or string with error message,
              status code
    """
    for k, t in zip(expected_keys, expected_types):
        if k not in data.keys():
            return f"{k} not found in input"
        if type(t) is list:
            if type(data[k]) not in t:
                return f"{k} not a valid type, expected one of {t}"
        elif type(data[k]) is not t:
            return f"{k} not a valid type, expected {t}"
    return True


def validate_mrn(mrn):
    """Validates if mrn meets formatting requirements

    Function checks the supplied Medical Record Number to determine
    if it matches required formatting requirements. If it is a string,
    attempts to convert to int, returns int otherwise. Returns
    False if the mrn is invalid.

    :param mrn: the medical record number

    :returns: mrn converted to int if valid, False otherwise
    """
    expected_types = [str, int]
    if type(mrn) in expected_types:
        try:
            mrn = int(mrn)
        except ValueError:
            return False
    else:
        return False
    return mrn


def get_last_hr(patient_record):
    """Get last heart rate for the provided record.

    Accesses the last heart rate uploaded for the patient,
    returns this. Returns None if there are none found.

    :param patient_record: Patient object (MongoDB entry)
    :returns: last heart rate uploaded, None if not found.
    """
    if len(patient_record.heart_rate) > 0:
        return patient_record.heart_rate[-1]
    else:
        return None


def get_last_ecg(patient_record):
    """Get last ECG image for the provided record.

    Accesses the last ECG image uploaded for the patient,
    returns this. Returns None if there are no ECG images.

    :param patient_record: Patient object (MongoDB entry)
    :return: last ECG image uploaded, None if not found.
    """
    if len(patient_record.ecg_image) > 0:
        return patient_record.ecg_image[-1]
    else:
        return None


def get_patient_name(patient_record):
    """Get patient name for the provided record.

    Accesses the patient name for the provided record,
    returns this. Returns None if no name entered.

    :param patient_record: Patient object (MongoDB entry)
    :return: patient name, None if not found.
    """
    if patient_record.patient_name is None:
        return None
    else:
        return patient_record.patient_name


def get_patient_timestamp(patient_record):
    """Get last ECG entry timestamp for the provided record.

    Accesses the last ECG timestamp uploaded for the patient,
    returns this. Returns None if there are no uploads found.

    :param patient_record: Patient object (MongoDB entry)
    :returns: str, ECG data upload timestamp
    """
    if len(patient_record.entry_time) > 0:
        return patient_record.entry_time[-1]
    else:
        return None


def get_ecg_by_timestamp(patient_record, timestamp):
    """Return ECG image for patient by provided timestamp.

    Accesses the timestamp for the patient record. If the timestamp
    exists in the record, returns the corresponding ECG image.
    Otherwise, returns None.

    :param patient_record: Patient object (MongoDB entry)
    :param timestamp: str representation of a valid timestamp
    :returns: ECG image corresponding to timestamp, None if not found
    """
    if timestamp in patient_record.entry_time:
        ts_index = patient_record.entry_time.index(timestamp)
    else:
        return None
    return patient_record.ecg_image[ts_index]


def get_ecg_timestamps(patient_record):
    """Return list of all ECG image timestamps.

    Accepts a Patient object, and returns the list of
    all uploaded ECG image timestamps. Returns empty list if
    none found.

    :param patient_record: Patient object (MongoDB entry)
    :returns: list of ECG timestamps
    """
    if len(patient_record.entry_time) > 0:
        return patient_record.entry_time
    else:
        return []


def get_medical_image_by_index(patient_record, index):
    """Retrieve medical image by index from patient record

    Retrieves a medical image by index from the provided
    patient record. Returns raw image data, or None if not
    found

    :param patient_record: Patient object (MongoDB entry)
    :param index: int, index of medical record
    :returns: Medical image data, None if not found
    """
    if len(patient_record.medical_image) >= index:
        return patient_record.medical_image[index]
    else:
        return None
