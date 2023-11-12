import re
import os

import pandas as pd

def extract_dtype_from_path(path):
    # Define the output categories and its corresponding file patterns
    f_cat = {'dvar':['ag','non_ag'],
            'ammap':['ammap'],
            'GHG':['GHG'],
            'lumap':['lumap'],
            'lmmap':['lmmap'],
            'water':['water'],
            'lumap_separate':[r'(Non-)?Agriculture Landuse_\d{2}'],
            'cross_table':['crosstab','switches'],
            'quantity':['quantity'],
            }
    # Get the key if the file path contains the file pattern
    f_cat = [k for k,v in f_cat.items() if any(re.compile(fr'^{i}').search(os.path.basename(path)) for i in v)][0]

    return f_cat


def get_all_files(data_root):

    file_paths = []

    # Walk through the folder and its subfolders
    for foldername, subfolders, filenames in os.walk(data_root):
        for filename in filenames:
            # Create the full path to the file by joining the foldername and filename
            file_path = os.path.join(foldername, filename)
            # Append the file path to the list
            file_paths.append(file_path)

    # remove log files and sort the files
    file_paths = sorted([i for i in file_paths if 'out_' in i])

    # Get the year and the run number from the file name
    file_paths = pd.DataFrame({'path':file_paths})
    file_paths.insert(0, 'year', [re.compile(r'out_(\d{4})').findall(i)[0] for i in file_paths['path']])
    file_paths.insert(1, 'catetory', file_paths['path'].apply(extract_dtype_from_path))
    file_paths[['base_name','base_ext']] = [os.path.splitext(os.path.basename(i)) for i in file_paths['path']]
    file_paths = file_paths.reindex(columns=['year','catetory','base_name','base_ext','path'])

    return file_paths