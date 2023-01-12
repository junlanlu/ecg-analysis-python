from ECG import ECG


def analyze(filename):
    """Main driver function

    Reads in CSV file, preprocess the CSV file, calculate
    the metrics, and exports the JSON file. Optional graphing
    allowed.

    :param: None

    :returns: None
    """
    ECGobject = ECG(filename)
    ECGobject.preprocess()
    ECGobject.calculate_metrics()
    # Uncomment the line below if you want to plot the ECG signal
    ECGobject.make_plots()
    # ECGobject.exportJSON()
    return int(ECGobject.mean_hr_bpm)
