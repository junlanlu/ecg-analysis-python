import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, simpledialog, messagebox
from flask import request
import pdb
from PIL import Image, ImageTk
import base64
from ecg_analysis import analyze
from patient_client import upload_patient_info

ecg_pil_image = None
med_pil_image = None


def design_window():
    """Create a window for the patient GUI

    Creates a tkinter window for patient GUI

    :param None:

    :returns: None
    """
    def cancel_btn_cmd():
        """Cancel button command to close window

        Cancel button command to close window

        :param None:

        :returns: None
        """
        root.destroy()

    def med_image_cmd():
        """Command to select medical image file and display on GUI

        User selects image file from dialog box and the image is
        resized and displayed on the GUI. File must be in .jpg format

        :param None:

        :returns: None
        """
        global med_pil_image
        newsize = (200, 200)
        med_img_filename = filedialog.askopenfilename(
            filetypes=[("jpeg files", "*.jpg")])
        if med_img_filename == "":
            return
        med_pil_image = Image.open(med_img_filename)
        pil_image_resize = med_pil_image.resize(newsize)
        tk_image = ImageTk.PhotoImage(pil_image_resize)
        med_img_label.image = tk_image
        med_img_label.configure(image=tk_image)

    def ecg_image_cmd():
        """Command to select ecg trace file and display on GUI

        User selects image file from dialog box and the image is
        resized and displayed on the GUI. The ecg trace file must
        be in .csv firmat

        :param None:

        :returns: None
        """
        global ecg_pil_image
        newsize = (300, 200)
        ecg_filename = filedialog.askopenfilename(
            filetypes=[("csv files", "*.csv")])
        if ecg_filename == "":
            return
        heart_rate.set(analyze(ecg_filename))
        ecg_pil_image = Image.open('images/ecg.jpg')
        pil_image_resize = ecg_pil_image.resize(newsize)
        tk_image = ImageTk.PhotoImage(pil_image_resize)
        ecg_img_label.image = tk_image
        ecg_img_label.configure(image=tk_image)

    def upload_btn_cmd():
        """Command to make a server request to post information in
        GUI

        Command to post all information in GUI to the database

        :param None:

        :returns: None
        """
        if mrn.get() == "":
            return
        # pdb.set_trace()
        upload_patient_info(patient_name.get(), mrn.get(),
                            heart_rate.get(), med_pil_image, ecg_pil_image)

    def clear_cmd():
        """Clears all entries in the GUI

        Clears all information including entries and images in the GUI

        :param None:

        :returns: None
        """
        global med_pil_image
        global ecg_pil_image

        med_pil_image = None
        ecg_pil_image = None
        patient_name.set("")
        mrn.set("")
        ecg_img_label.image = ''
        med_img_label.image = ''
        heart_rate.set('')

    root = tk.Tk()
    root.title('Patient-side GUI client')
    root.geometry("700x600")

    myfont = ("arial", 18)

    patient_name_label = ttk.Label(root, text="Patient Name", font=myfont)
    patient_name_label.grid(column=0, row=0)

    patient_name = tk.StringVar()
    patient_name.set("")
    name_entry = ttk.Entry(
        root, textvariable=patient_name, font=myfont, width=20)
    name_entry.grid(column=1, row=0)

    mrn_label = ttk.Label(root, text="Medical Record Number", font=myfont)
    mrn_label.grid(column=0, row=1)

    mrn = tk.StringVar()
    mrn_entry = ttk.Entry(root, textvariable=mrn, font=myfont, width=20)
    mrn_entry.grid(column=1, row=1)

    clear_btn = ttk.Button(root, text="Clear", command=clear_cmd)
    clear_btn.grid(column=2, row=5)

    heart_rate = tk.StringVar()
    heart_rate.set("")
    heart_rate_label = ttk.Label(
        root, text="Current heart rate (bpm)", font=myfont)
    heart_rate_label.grid(column=0, row=6)
    heart_rate_value_label = ttk.Label(
        root, textvariable=heart_rate, font=myfont)
    heart_rate_value_label.grid(column=1, row=6)

    ecg_label = ttk.Label(root, text="ECG image", font=myfont)
    ecg_label.grid(column=0, row=7)
    ecg_img_label = ttk.Label(root, image=None)
    ecg_img_label.grid(column=1, row=7)
    ecg_img_label.image = ''
    ecg_img_btn = ttk.Button(
        root, text="Display ecg trace", command=ecg_image_cmd)
    ecg_img_btn.grid(column=2, row=7)

    medical_img_label = ttk.Label(root, text="Medical image", font=myfont)
    medical_img_label.grid(column=0, row=8)
    med_img_label = ttk.Label(root, image=None)
    med_img_label.grid(column=1, row=8)
    med_img_label.image = ''
    medical_img_btn = ttk.Button(
        root, text="Display medical image", command=med_image_cmd)
    medical_img_btn.grid(column=2, row=8)

    upload_btn = ttk.Button(root, text="Upload", command=upload_btn_cmd)
    upload_btn.grid(column=2, row=9)

    cancel_btn = ttk.Button(root, text="Cancel", command=cancel_btn_cmd)
    cancel_btn.grid(column=2, row=10)

    root.mainloop()
    return


if __name__ == '__main__':
    design_window()
