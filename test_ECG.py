from ECG import ECG
import numpy as np
from testfixtures import LogCapture
import pytest
import matplotlib.pyplot as plt


def test_read_csv():
    filename = 'ecg_data/test_data1.csv'
    ECGobject = ECG(filename)
    time, voltage = ECGobject.read_csv()
    assert time is not None
    assert voltage is not None
    assert len(voltage) == len(time)


def test_parse_string_return():
    filename = ''
    ECG_object = ECG(filename)
    ECG_object.voltage = ['1', '', '1', '1', '1']
    ECG_object.time = ['0', '0', 'bad data', '1', 'NaN']
    time, voltage = ECG_object.parse_string()
    assert not np.isnan(time).any()
    assert not np.isnan(voltage).any()


def test_parse_string_log():
    filename = ''
    ECG_object = ECG(filename)
    with LogCapture() as log_c:
        ECG_object.voltage = ['1', '', '1', '1', '1']
        ECG_object.time = ['1,' '0', 'bad data', '1', 'NaN']
        ECG_object.parse_string()
    log_msg = "Bad or empty entry"
    log_c.check(("root", "ERROR", log_msg),
                ("root", "ERROR", log_msg),
                ("root", "ERROR", log_msg))


def test_log_if_abnormal_range():
    filename = ''
    log = filename.split('.')[0]+'.log'
    ECG_object = ECG(filename)
    with LogCapture() as log_c:
        ECG_object.voltage = ['350', '40']
        ECG_object.time = ['0', '1']
        ECG_object.parse_string()
        ECG_object.log_if_abnormal_range()
    log_msg = filename + ": Voltage exceeds normal range"
    log_c.check(("root", "WARNING", log_msg))
    with LogCapture() as log_c:
        ECG_object.voltage = ['299', '40']
        ECG_object.time = ['0', '1']
        ECG_object.parse_string()
        ECG_object.log_if_abnormal_range()
    log_c.check()


def test_calculate_sampling_rate():
    filename = ''
    ECG_object = ECG(filename)
    ECG_object.time = np.linspace(0, 20, 1200)
    assert ECG_object.calculate_sampling_rate() == 60


def test_bandpass_filter():
    filename = ''
    ECG_object = ECG(filename)
    f1, f2 = 3, 7
    f = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    expected_f = np.asarray([0, 0, 0, 3, 4, 5, 6, 7, 0, 0, 0])
    assert (ECG_object.bandpass_filter(f, f1, f2) == expected_f).all()


def test_filter():
    def f(x):
        return np.sin(x)+np.sin(5*x)+np.sin(10*x)
    filename = ''
    ECG_object = ECG(filename)
    ECG_object.time = np.linspace(0, 20, 1200)
    ECG_object.voltage = f(ECG_object.time)
    voltage_filter = ECG_object.filter(f1=5, f2=20)
    voltage_filter_fft = np.fft.fftshift(np.fft.fft(voltage_filter))
    voltage_fft = np.fft.fftshift(np.fft.fft(ECG_object.voltage))
    assert abs(voltage_filter_fft[632]) < abs(voltage_fft[632])
    assert abs(voltage_filter_fft[603]) < abs(voltage_fft[603])


def test_calculate_voltage_extremes():
    ECG_object = ECG('')
    ECG_object.voltage_filter = np.linspace(0, 20, 1200)
    voltage_extremes = ECG_object.calculate_voltage_extremes()
    assert voltage_extremes == (0, 20)


def test_calculate_duration():
    ECG_object = ECG('')
    ECG_object.time = np.linspace(0, 20, 1200)
    duration = ECG_object.calculate_duration()
    assert duration == 20


def test_find_peaks():
    voltage_filter = np.zeros((10000,))
    voltage_filter[1000] = 1
    voltage_filter[6000] = 1
    ECG_object = ECG('')
    ECG_object.voltage_filter = voltage_filter
    ECG_object.sampling_rate = 60
    peaks = ECG_object.find_peaks()
    assert (peaks == [1000, 6000]).all()


def test_calculate_num_beats():
    voltage_filter = np.zeros((10000,))
    voltage_filter[1000] = 1
    voltage_filter[6000] = 1
    ECG_object = ECG('')
    ECG_object.voltage_filter = voltage_filter
    ECG_object.sampling_rate = 60
    ECG_object.find_peaks()
    num_beats = ECG_object.calculate_num_beats()
    assert num_beats == 2


def test_calculate_beats():
    time = np.linspace(0, 10, 10000)
    voltage_filter = np.zeros((10000,))
    voltage_filter[1000] = 1
    voltage_filter[6000] = 1
    ECG_object = ECG('')
    ECG_object.voltage_filter = voltage_filter
    ECG_object.time = time
    ECG_object.sampling_rate = 60
    ECG_object.find_peaks()
    beats = ECG_object.calculate_beats()
    expected_beats = [time[1000], time[6000]]
    assert (beats == expected_beats).all()


def test_calculate_mean_hr_bpm():
    time = np.linspace(0, 10, 10000)
    voltage_filter = np.zeros((10000,))
    voltage_filter[1000] = 1
    voltage_filter[6000] = 1
    ECG_object = ECG('')
    ECG_object.voltage_filter = voltage_filter
    ECG_object.time = time
    ECG_object.sampling_rate = 60
    ECG_object.find_peaks()
    ECG_object.calculate_beats()
    bpm = ECG_object.calculate_mean_hr_bpm()
    expected_bpm = 12
    assert bpm == expected_bpm
