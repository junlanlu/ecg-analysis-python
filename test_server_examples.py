from Patient import Patient

validate_patient_info_examples = [({"patient_name": 'bob',
                                    "mrn": "Smith.J",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"patient_nae": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"patient_name": 'bob',
                                    "mn": "101",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"patient_name": 'bob',
                                    "mrn": 101,
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 200),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 200),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "abc",
                                    "medical_image": "",
                                    "heart_rate": "61"}, 200),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "12",
                                    "medical_image": "",
                                    "heart_rate": 61}, 200),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "abc",
                                    "medical_image": "abc",
                                    "heart_rate": 61}, 200),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": "12",
                                    "medical_image": 12,
                                    "heart_rate": 61}, 400),
                                  ({"patient_name": 'bob',
                                    "mrn": "101",
                                    "ecg_image": 12,
                                    "medical_image": "",
                                    "heart_rate": 61}, 400),
                                  ({"patient_name": 101,
                                    "mrn": "101",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"mrn": 102,
                                    "patient_name": "",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 200),
                                  ({"mrn": 102,
                                    "patient_name": "",
                                    "eg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"mrn": 102,
                                    "patient_name": "",
                                    "ecg_image": "",
                                    "medial_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"mrn": "",
                                    "patient_name": "bob",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"mrn": "",
                                    "patient_name": "",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400),
                                  ({"patient_name": 101,
                                    "mrn": "",
                                    "ecg_image": "",
                                    "medical_image": "",
                                    "heart_rate": ""}, 400), ]

process_patient_info_examples = validate_patient_info_examples

find_patient_in_db_examples = [(101, True), (9999, False)]

validate_get_patient_by_mrn_examples = [
    (1000, {
        "patient_name": 'bob',
        "ecg_image": "",
        "medical_image": "",
        "heart_rate": ""
    }, Patient(mrn=1000,
               patient_name="bob")),
    ("1001", {
        "patient_name": 'Frank',
        "ecg_image": "",
        "medical_image": "",
        "heart_rate": ""
    }, Patient(mrn=1001,
               patient_name="Frank")),
    ("1002a", {}, "Invalid MRN format"),
    ([123], {}, "Invalid MRN format"),
]