import pytest
from Patient import Patient


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
    mrn=153,
    medical_image=["img1", "img2"],
    ecg_image=["ecg1", "ecg2"],
    entry_time=["ts1"],
    heart_rate=[123, 60],
)


@pytest.mark.parametrize("expected_keys, expected_types, data, expected", [
    (["attending_username", "attending_email", "attending_phone"],
     [str, str, str],
     {"attending_username": "Smith.J",
      "attending_phone": "123-456-7890",
      "attending_email": "test@example.com"
      }, True),
    (["key_1", "key_2", "key_3"],
     [str, int, list],
     {"key_1": "Smith.J",
      "key_2": 5,
      "key_3": [1, 2, 3]
      }, True),
    (["key_1", "key_2", "key_3"],
     [str, int, list],
     {"key_1": "Smith.J",
      "key_2": 5,
      }, "key_3 not found in input"),
    (["key_1", "key_2", "key_3"],
     [str, int, list],
     {"key_1": "Smith.J",
      "key_2": "5",
      "key_3": [1, 3, 3]
      }, "key_2 not a valid type, expected {}".format(int)),
    (["key_1", "key_2", "key_3"],
     [str, int, [int, str]],
     {"key_1": "Smith.J",
      "key_2": 5,
      "key_3": 3
      }, True),
    (["key_1", "key_2", "key_3"],
     [str, int, [int, str]],
     {"key_1": "Smith.J",
      "key_2": 5,
      "key_3": "3"
      }, True),
    (["key_1", "key_2", "key_3"],
     [str, int, [int, str]],
     {"key_1": "Smith.J",
      "key_2": 5,
      "key_3": 2.35
      }, "key_3 not a valid type, expected one of {}".format([int, str])),
])
def test_validate_post_input(expected_keys, expected_types, data, expected):
    from helpers import validate_post_input
    result = validate_post_input(expected_keys, expected_types, data)
    assert result == expected


@pytest.mark.parametrize("mrn, expected", [
    (1, 1),
    (10235, 10235),
    ("1", 1),
    ("21353", 21353),
    ("3as", False),
    ([2134], False),
    ("one", False),
])
def test_validate_patient_id(mrn, expected):
    from helpers import validate_mrn
    validated = validate_mrn(mrn)
    assert validated == expected


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, "James"),
    (dummy_pt_2, None),
])
def test_get_patient_name(patient, expected):
    from helpers import get_patient_name
    pt_name = get_patient_name(patient)
    assert pt_name == expected


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, "ecg2"),
    (dummy_pt_2, None),
])
def test_get_last_ecg(patient, expected):
    from helpers import get_last_ecg
    pt_ecg = get_last_ecg(patient)
    assert pt_ecg == expected


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, 60),
    (dummy_pt_2, None),
])
def test_get_last_hr(patient, expected):
    from helpers import get_last_hr
    pt_hr = get_last_hr(patient)
    assert pt_hr == expected


@pytest.mark.parametrize("patient, timestamp, expected", [
    (dummy_pt_1, "ts2", "ecg2"),
    (dummy_pt_1, "ts1", "ecg1"),
    (dummy_pt_2, "ts1", None),
])
def test_get_ecg_by_timestamp(patient, timestamp, expected):
    from helpers import get_ecg_by_timestamp

    pt_ecg = get_ecg_by_timestamp(patient, timestamp)
    assert pt_ecg == expected


@pytest.mark.parametrize("patient, expected", [
    (dummy_pt_1, ["ts1", "ts2"]),
    (dummy_pt_2, []),
    (dummy_pt_3, ["ts1"]),
])
def test_get_ecg_timestamps(patient, expected):
    from helpers import get_ecg_timestamps
    pt_timestamps = get_ecg_timestamps(patient)
    assert pt_timestamps == expected


@pytest.mark.parametrize("patient, index, expected", [
    (dummy_pt_1, 0, "img1"),
    (dummy_pt_1, 1, "img2"),
    (dummy_pt_2, 1, None),
])
def test_get_medical_image_by_index(patient, index, expected):
    from helpers import get_medical_image_by_index
    result = get_medical_image_by_index(patient, index)
    assert result == expected
