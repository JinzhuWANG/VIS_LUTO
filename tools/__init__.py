import re
import os

import nbformat as nbf
from glob import glob

import pandas as pd

# set up working directory
if __name__ == '__main__':
    os.chdir('..')

from PARAMETERS import GHG_FNAME2TYPE, NOTEBOOK_META_DICT

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
    
    if not 'lucc_separate' in path:
        # Get the key if the file path contains the file pattern
        f_cat = [k for k,v in f_cat.items() if any(re.compile(fr'^{i}').search(os.path.basename(path)) for i in v)][0]
    else:
        luseperate_suffix = re.compile(r'lucc_separate/(.*)_\d').findall(path)[0]
        f_cat = f'lumap_separate_{luseperate_suffix}'
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

    file_paths['year'] = file_paths['year'].astype(int)

    return file_paths


def get_GHG_file_df(all_files_df):
    # Get only GHG_seperate files
    GHG_files = all_files_df.query('catetory == "GHG" and base_name != "GHG_emissions" ').reset_index(drop=True)
    GHG_files['GHG_sum_t'] = GHG_files['path'].apply(lambda x: pd.read_csv(x,index_col=0).loc['SUM','SUM'])
    GHG_files = GHG_files.replace({'base_name': GHG_FNAME2TYPE})

    return GHG_files


def add_meta_to_nb(ipath):

    # Search through each notebook and look for the text, add a tag if necessary
    ntbk = nbf.read(ipath, nbf.NO_CONVERT)

    for cell in ntbk.cells:
        cell_tags = cell.get('metadata', {}).get('tags', [])
        for key, val in NOTEBOOK_META_DICT.items():
            if key in cell['source']:
                if val not in cell_tags:
                    cell_tags.append(val)
        if len(cell_tags) > 0:
            cell['metadata']['tags'] = cell_tags

    nbf.write(ntbk, ipath)