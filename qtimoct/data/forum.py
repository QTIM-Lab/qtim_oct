from glob import glob
from os.path import join
from collections import defaultdict
import pydicom
import subprocess as sp
import tempfile
import nibabel as nib
import numpy as np
import pandas as pd


def load_forum_data(xml_dir, dcm_dir, out_dir):

    defult_tmp_dir = tempfile._get_default_tempdir()
    xml_paths = sorted(glob(join(xml_dir, '*.xml')))
    dcm_paths = sorted(glob(join(dcm_dir, '*.dcm')))

    data = []

    for xml, dcm in zip(xml_paths, dcm_paths):

        xml_file = None
        dcm_file = pydicom.dcmread(dcm)

        series_entries = dcm_file.dir('series')
        if 'SeriesDescription' not in series_entries:
            continue

        # Patient and series description
        pname = dcm_file.PatientName
        desc = dcm_file.SeriesDescription

        if 'PixelData' in dcm_file.dir('pixel'):

            # Decompressing DICOM
            tmp_file = join(defult_tmp_dir, next(tempfile._get_candidate_names()))
            convert_dcm(dcm, tmp_file)

            # Converting to NIFTI
            raw_data = pydicom.dcmread(tmp_file).pixel_array
            if len(raw_data.shape) < 3 or 'Cube' not in desc:  continue
            x, y, z = raw_data.shape

            # Get metadata and create file name
            lat = dcm_file.Laterality
            img_date = dcm_file.StudyDate
            fname = f'{pname}_{desc}_{img_date}_{lat}.nii.gz'.replace(' ', '')
            print(fname, raw_data.shape, f'{raw_data.min()} - {raw_data.max()}')

            row_dict = dict(patient_name=pname, laterality=lat, filename=fname, date=img_date, x=x, y=y, z=z)
            data.append(row_dict)

            # Save nifti file
            nii_obj = nib.Nifti1Image(raw_data, np.eye(4))
            save_path = join(out_dir, fname)
            nib.save(nii_obj, save_path)

    df = pd.DataFrame(data=data)
    df['date'] = pd.to_datetime(df['date'])
    return df


def convert_dcm(input_dcm, output_dcm):

    cmd = ['gdcmconv', '--raw', input_dcm, output_dcm]
    return sp.check_output(cmd)
