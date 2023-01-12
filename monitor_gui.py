import tkinter as tk
from tkinter import N, E, S, W
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
from flask import request
import pdb
from PIL import Image, ImageTk
import base64
from ecg_analysis import analyze
import monitor_client as mc
import io
from skimage.io import imsave
from patient_client import convert_ndarray_to_b64_string

first_load = True


def main_window():
    """Create a window for the monitor GUI

    Creates a tkinter window for monitor GUI

    :param None:

    :returns: None
    """

    def refresh_data():
        """Refresh data on a loop

        Every 5 seconds, refresh all the loaded data and schedule
        another call to this method.

        :param None:

        :returns: None
        """
        if not first_load:
            get_latest_data()
        mrn_dropdown['values'] = mc.load_all_patients()
        root.after(5000, refresh_data)

    def get_latest_data():
        """Retrieve latest data for the selected patient

        Poll database for the most recent data for the selected patient.
        If no patient selected, do nothing.

        :param None:

        :returns: None
        """
        mrn = mrn_dropdown.get()
        if mrn == '':
            return
        mrn_value.set(mrn)
        pt_info = mc.load_patient_latest(mrn)
        ecg_images = mc.load_list_of_ecg_timestamps(mrn)
        ecg_dropdown['values'] = ecg_images
        pt_med_images = mc.load_list_of_medical_images(int(mrn))
        med_image_dropdown['values'] = pt_med_images
        if pt_med_images is []:
            med_img_load_btn.state(['disabled'])
        else:
            med_img_load_btn.state(['!disabled'])

        if ecg_images is []:
            ecg_compare_button.state(['disabled'])
        else:
            ecg_compare_button.state(['!disabled'])

        if pt_info['latest_hr'] is None:
            heart_rate_value.set("")
        else:
            heart_rate_value.set(pt_info['latest_hr'])
        if pt_info['entry_time'] is None:
            timestamp_value.set("")
        else:
            timestamp_value.set(pt_info['entry_time'])
        if pt_info['name'] is None:
            pt_name.set("")
        else:
            pt_name.set(pt_info['name'])

        if pt_info['latest_ecg'] is None:
            ecg_img_label.image = ''
        else:
            img_data = mc.convert_b64_string_to_ndarray(pt_info['latest_ecg'])
            ecg_img = load_img_data(img_data)
            ecg_img_label.image = ecg_img
            ecg_img_label.configure(image=ecg_img)
            save_ecg_btn.state(['!disabled'])

    def load_btn_cmd():
        """Load latest information for selected patient

        On click of Load button, clears the GUI, and
        refreshes with latest information for the selected patient.

        :param None:

        :returns: None
        """
        mrn = mrn_dropdown.get()
        if mrn != '':
            global first_load
            first_load = False
            heart_rate_value.set("")
            timestamp_value.set("")
            pt_name.set("")
            ecg_img_label.image = ''
            ecg_historical.image = ""
            med_img_label.image = ""
            ecg_dropdown.set("")
            med_image_dropdown.set("")
            save_ecg_btn.state(['disabled'])
            save_ecg_btn2.state(['disabled'])
            save_med_img_btn.state(['disabled'])

            get_latest_data()

    def load_img_data(ndarray_img):
        """Convert ndarray image data to TKinter object

        Accepts an ndarray with image data, and returns
        the TKinter object for the data.

        :param ndarray_img: ndarray with image data

        :returns: TKinter Image object
        """
        f = io.BytesIO()
        imsave(f, ndarray_img, plugin='pil')
        img = io.BytesIO()
        img.write(f.getvalue())
        img_obj = Image.open(img)
        pil_image_resize = img_obj.resize((300, 300))
        return ImageTk.PhotoImage(pil_image_resize)

    def save_image(image, template_name):
        """Save image to file

        Accepts a b64 image string as input, along with
        the template filename to use, and writes this image out
        to a file.

        :param template_name: str, image file name to save to
        :param image: base 64 image data

        :returns: None
        """
        file = filedialog.asksaveasfilename(
            initialfile=f"{template_name}",
            defaultextension=".jpg")
        if file == "":
            return
        mc.download_image_from_server(image, file)

    def save_cur_ecg():
        """Save current ECG image to file

        Download base64 image data from server for
        current ECG image, and saves to a .jpg file.

        :param None:

        :returns: None
        """
        mrn = mrn_value.get()
        patient_latest = mc.load_patient_latest(mrn)
        cur_ecg_img = patient_latest['latest_ecg']
        # print(cur_ecg_img)
        save_image(cur_ecg_img, f"Patient_{mrn}_current_ecg.jpg")

    def save_hist_ecg():
        """Save historical ECG image to file

        Download base64 image data from server, for
        selected historical ECG image, and saves
        to a .jpg file.

        :param None:

        :returns: None
        """
        timestamp = ecg_dropdown.get()
        mrn = mrn_value.get()
        old_ecg = mc.load_ecg_by_timestamp(mrn, timestamp)
        save_image(old_ecg,
                   f"Patient_{mrn}_ECG_{timestamp}.jpg".replace(
                       ":", "_"))

    def save_medical_img():
        """Save current medical image to file

        Download base64 image data from server for
        current medical image, and saves to a .jpg file.

        :param None:

        :returns: None
        """
        med_img_id = int(med_image_dropdown.get())
        mrn = mrn_value.get()
        med_img = mc.load_img_by_id(mrn, med_img_id)

        save_image(med_img, f"Patient_{mrn}_Medical_Image_{med_img_id}.jpg")

    def compare_ecg_cmd():
        """Load a historical ECG image side-by-side current

        Loads the selected historical ECG image (in the dropdown)
        alongside the existing, current ECG image, for user comparison.

        :param None:

        :returns: None
        """
        timestamp = ecg_dropdown.get()
        if timestamp != '':
            old_ecg = mc.load_ecg_by_timestamp(mrn_value.get(), timestamp)
            historical_data = mc.convert_b64_string_to_ndarray(old_ecg)
            historical_img = load_img_data(historical_data)
            ecg_historical.image = historical_img
            ecg_historical.configure(image=historical_img)
            save_ecg_btn2.state(['!disabled'])

    def load_medical_image():
        """Load the selected medical image

        Loads the selected medical image from the database, and
        displays it in the UI.

        :param None:

        :returns: None
        """
        med_img_id = med_image_dropdown.get()
        if med_img_id != '':
            med_img_id = int(med_img_id)
            med_img_enc = mc.load_img_by_id(int(mrn_value.get()), med_img_id)
            med_img_data = mc.convert_b64_string_to_ndarray(med_img_enc)
            med_img = load_img_data(med_img_data)
            med_img_label.image = med_img
            med_img_label.configure(image=med_img)
            save_med_img_btn.state(['!disabled'])

    root = tk.Tk()
    root.title('Monitor GUI client')
    root.geometry("1000x1000")

    mainframe = ttk.Frame(root, padding="3 3 12 12",
                          width=1000, height=1000)
    mainframe.grid(column=0, row=0)

    myfont = ("arial", 18)

    ttk.Label(mainframe,
              text="Available Medical Records",
              font=myfont).grid(column=0, row=0)
    mrn_dropdown = ttk.Combobox(mainframe,
                                state='readonly',
                                values=mc.load_all_patients())
    mrn_dropdown.grid(column=1, row=0)

    load_btn = ttk.Button(mainframe, text="Load Patient",
                          command=load_btn_cmd)
    load_btn.grid(column=2, row=0)

    mrn_value = tk.StringVar()
    mrn_value.set("")
    ttk.Label(mainframe, text="Medical Record Number: ",
              font=myfont).grid(column=0, row=2, sticky=tk.E)
    ttk.Label(mainframe, textvariable=mrn_value,
              font=myfont).grid(column=1, row=2, sticky=tk.W)

    pt_name = tk.StringVar()
    ttk.Label(mainframe, text="Patient Name: ",
              font=myfont).grid(column=0, row=3, sticky=tk.E)
    ttk.Label(mainframe, textvariable=pt_name,
              font=myfont).grid(column=1, row=3, sticky=tk.W)

    heart_rate_value = tk.StringVar()
    heart_rate_value.set("")
    ttk.Label(mainframe, text="Last Heart Rate: ",
              font=myfont).grid(column=0, row=4, sticky=tk.E)
    ttk.Label(mainframe, textvariable=heart_rate_value,
              font=myfont).grid(column=1, row=4, sticky=tk.W)

    timestamp_value = tk.StringVar()
    timestamp_value.set("")
    ttk.Label(mainframe, text="Entry Time: ",
              font=myfont).grid(column=0, row=5, sticky=tk.E)
    ttk.Label(mainframe, textvariable=timestamp_value,
              font=myfont).grid(column=1, row=5, sticky=tk.W)

    ecg_label = ttk.Label(mainframe, text="ECG image", font=myfont)
    ecg_label.grid(column=0, row=6)

    ttk.Label(mainframe,
              text="Select Historical Image: ",
              font=myfont).grid(column=2, row=4)

    ecg_dropdown = ttk.Combobox(mainframe, state='readonly')
    ecg_dropdown.grid(column=2, row=5)

    ecg_img_label = ttk.Label(mainframe, image=None)
    ecg_img_label.grid(column=1, row=6, sticky=tk.E)
    ecg_img_label.image = ''

    ecg_historical = ttk.Label(mainframe, image=None)
    ecg_historical.grid(column=2, row=6, sticky=tk.E)
    ecg_historical.image = ''

    ecg_compare_button = ttk.Button(mainframe, text="Compare ECGs",
                                    command=compare_ecg_cmd)
    ecg_compare_button.grid(column=3, row=5)

    ttk.Label(mainframe,
              text="Select Medical Image: ",
              font=myfont).grid(column=0, row=7)

    med_image_dropdown = ttk.Combobox(mainframe, state='readonly')
    med_image_dropdown.grid(column=1, row=7)

    med_img_label = ttk.Label(mainframe, image=None)
    med_img_label.grid(column=1, row=8, sticky=tk.E)
    med_img_label.image = ''

    med_img_load_btn = ttk.Button(mainframe, text="Load Medical Image",
                                  command=load_medical_image)
    med_img_load_btn.grid(column=2, row=7)

    save_ecg_btn = ttk.Button(mainframe, text="Save Current ECG",
                              command=save_cur_ecg)
    save_ecg_btn.grid(column=0, row=10)

    save_ecg_btn2 = ttk.Button(mainframe, text="Save Historical ECG",
                               command=save_hist_ecg)
    save_ecg_btn2.grid(column=0, row=11)

    save_med_img_btn = ttk.Button(mainframe, text="Save Medical Image",
                                  command=save_medical_img)
    save_med_img_btn.grid(column=0, row=12)

    save_ecg_btn.state(['disabled'])
    save_ecg_btn2.state(['disabled'])
    save_med_img_btn.state(['disabled'])
    med_img_load_btn.state(['disabled'])
    ecg_compare_button.state(['disabled'])

    root.after(5000, refresh_data)
    root.mainloop()
    return


if __name__ == '__main__':
    main_window()
