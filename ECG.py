import json
import csv
import logging
import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt
import json
import matplotlib
matplotlib.use('Agg')


class ECG(object):
    def __init__(self, filename):
        print("***Processing filename.{}***".format(filename))
        self.duration = -1
        self.voltage_extremes = ()
        self.filename = filename
        self.time = []
        self.voltage = []
        self.voltage_filter = []
        self.num_beats = -1
        self.mean_hr_bpm = -1
        self.sampling_rate = -1
        self.beats = []
        self.peaks = []

        self.init_log()

    def preprocess(self):
        """Preprocess the CSV file

        Calls init_log(), read_csv(), parse_string(), log_if_abnormal_range()
        and filter() functions as a part of the preprocessing block

        :param self: self

        :returns: None
        """
        self.init_log()
        self.read_csv()
        self.parse_string()
        self.log_if_abnormal_range()
        self.filter()

    def init_log(self):
        """Initializes log file

        Initalizes a log file for each ECG strip being processed.
        Adds an INFO log indicating begin processing.

        :param self: self

        :returns: None
        """
        log = self.filename.split('.')[0]+'.log'
        logging.basicConfig(filename=log, filemode="w",
                            level=logging.INFO)
        logging.info("Begin processing of ECG {}".format(self.filename))

    def read_csv(self):
        """Reads in CSV file for time and voltage

        Given the file name for csv file return a list of strings
        (first column) and a list of voltages (second column)

        :param self: self

        :returns: list of string of time
        :returns: list of string of voltage
        """
        time = []
        voltage = []
        with open(self.filename, newline='') as csvfile:
            ecg_reader = csv.reader(csvfile, delimiter=',')
            for row in ecg_reader:
                time.append(row[0])
                voltage.append(row[1])
        self.time = time
        self.voltage = voltage
        return time, voltage

    def parse_string(self):
        """Converts list of strings to numerical arrays

        Converts list of strings from the .csv file to an array of
        numerical values. If an error occurs (ie bad data, missing
        data or NaN), an error will be logged.

        :param self: self

        :returns: array of float for time
        :returns: array of float for voltage
        """
        temp_time = []
        temp_voltage = []
        for i in range(len(self.time)):
            try:
                if not np.isnan([float(self.time[i]),
                                 float(self.voltage[i])]).any():
                    temp_time.append(float(self.time[i]))
                    temp_voltage.append(float(self.voltage[i]))
                else:
                    logging.error("Bad or empty entry")
            except ValueError:
                logging.error("Bad or empty entry")
        self.time = np.asarray(temp_time, dtype=np.float32)
        self.voltage = np.asarray(temp_voltage, dtype=np.float32)
        return temp_time, temp_voltage

    def log_if_abnormal_range(self):
        """Adds to log if maximum voltage exceeds 300mV

        Checks if the array of voltage values contains a value over 300mV
        If it does, log "Voltage exceeds normal range""

        :param self: self

        :returns: None
        """
        if (abs(self.voltage) > 300).any():
            log_msg = self.filename + ": Voltage exceeds normal range"
            logging.warning(log_msg)

    def calculate_sampling_rate(self):
        """Calculate the average sampling rate

        Calculate the average sampling rate of the ECG by dividing
        the total duration by the numbered of sampled points

        :param self: self

        :returns: Float of sampling rate
        """
        self.sampling_rate = len(self.time)/(np.max(self.time))
        return self.sampling_rate

    def bandpass_filter(self, f, f1, f2):
        """Apply a band pass filter to a list of frequencies

        Calculate the average sampling rate of the ECG by dividing
        the total duration by the numbered of sampled points

        :param self: self
        :param f1: minimum frequency of bandpass filter
        :param f2: maximum frequency of bandpas filter

        :returns: Array of float of frequencies
        """
        f[abs(f) < f1] = 0
        f[abs(f) > f2] = 0
        return f

    def filter(self, f1=3, f2=50):
        """Apply the bandpass filter to the signal

        Apply the bandpass filter to the voltage signal. This is done
        by calculating the fourier transform of the signal and then
        truncating the signal at the bands

        :param self: self
        :param f1: minimum frequency of bandpass filter
        :param f2: maximum frequency of bandpas filter

        :returns: array of the voltage filtered
        """
        sampling_rate = self.calculate_sampling_rate()
        signal_fft = np.fft.fftshift(np.fft.fft(self.voltage))
        f_max = 2*self.sampling_rate
        f = np.linspace(-f_max, f_max, len(self.time))
        f = self.bandpass_filter(f, f1, f2)
        signal_fft_filter = signal_fft * (f != 0).astype(float)
        signal_denoise = np.fft.ifft(signal_fft_filter)
        self.voltage_filter = abs(signal_denoise)
        return self.voltage_filter

    def calculate_metrics(self):
        """Calculate metrics

        Calculate the metrics of voltage extemes, duration,
        number of beats, beats, mean heart rate by calling the
        individual helper functions. Also logs for each metric
        calculated

        :param self: self

        :returns: None
        """
        logging.info("calculating voltage extremes")
        self.calculate_voltage_extremes()
        logging.info("calculating duration")
        self.calculate_duration()
        self.find_peaks()
        logging.info("calculating num_beats")
        self.calculate_num_beats()
        logging.info("calculating beats")
        self.calculate_beats()
        logging.info("calculating mean_hr_bpm")
        self.calculate_mean_hr_bpm()

    def calculate_voltage_extremes(self):
        """Calculate the voltage extremes

        Calculate the minimum and maximum of the filtered voltage
        signals. The extreme is stored in a tuple

        :param self: self

        :returns: Float of the extermes of the voltage
        """
        self.voltage_extremes = (min(self.voltage_filter),
                                 max(self.voltage_filter))
        return self.voltage_extremes

    def calculate_duration(self):
        """Calculate the duration

        Calculate the duration of the ECG signal by taking the
        maximum time point.

        :param self: self

        :returns: Float of the duration
        """
        self.duration = np.max(self.time)
        return self.duration

    def find_peaks(self):
        """Calculate the peaks of the ECG signal

        Defining each beat as the maximum of each ECG, the find_peaks
        function uses scipy.signals.find_peaks to find local peaks of the
        filtered voltage signal. The minimum height is the 80th percentile of
        the ECG signal while the minimum spacing is half the sampling rate

        :param self: self

        :returns: list of indices corresponding to detected peaks
        """
        voltage_filter = self.voltage_filter
        pks, p = signal.find_peaks(voltage_filter,
                                   height=np.percentile(voltage_filter, 80),
                                   distance=self.sampling_rate/2)
        self.peaks = pks
        return self.peaks

    def calculate_num_beats(self):
        """Calculate the number of beats of ECG strip

        Counts the length of the peaks variable to determine the number
        of beats. This implicitly defines each beat at the peak

        :param self: self

        :returns: integer of number of beats
        """
        self.num_beats = len(self.peaks)
        return self.num_beats

    def calculate_beats(self):
        """Calculate the time of each beat

        Calculates list of times that beats occur. This is done by using
        the self.peaks variable which has a list of indices that peaks occur.

        :param self: self

        :returns: list of floats of times that beats occur
        """
        self.beats = self.time[self.peaks]
        return self.beats

    def calculate_mean_hr_bpm(self):
        """Calculate the mean heart rate in bpm

        Calculates the heart rate by taking the average difference in time
        between beats.

        :param self: self

        :returns: integer of heart rate in bpm
        """
        dif_beats = np.diff(self.beats)
        self.mean_hr_bpm = np.round(60/np.mean(dif_beats))
        return self.mean_hr_bpm

    def exportJSON(self):
        """Export the metrics as a json file

        Exports the duration, voltage extreme, number of beats
        mean heart rate, and beat times into a json file of format
        filename.json

        :param self: self

        :returns: None
        """
        logging.info("exporting all metrics to json")
        metrics = {
            "duration": np.float64(self.duration),
            "voltage_extremes": self.voltage_extremes,
            "num_beats": self.num_beats,
            "mean_hr_bpm": self.mean_hr_bpm,
            "beats": self.beats.tolist(),
        }
        filename = self.filename.split('.')[0]+'.json'
        out_file = open(filename, 'w')
        json.dump(metrics, out_file)
        out_file.close()
        print("***Finished processing filename.{}***".format(self.filename))

    def make_plots(self):
        """Plot the voltages

        Plots the unfiltered ECG and filtered ECG signals with the
        detected peaks

        :param self: self

        :returns: None
        """

        plt.plot(self.time, self.voltage)
        plt.title('Original ECG')
        plt.axis('equal')
        plt.xlabel('time (s)')
        plt.ylabel('voltage (mV)')
        plt.savefig('images/ecg.jpg', dpi=200)
        plt.close()
