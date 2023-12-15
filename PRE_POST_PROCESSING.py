from glob import glob
import os
import pandas as pd

from tqdm.auto import tqdm
from tools import add_meta_to_nb, get_all_files
from tools.TIF2color import ParallelConvertDecorator, convert_1band_to_4band, create_qml_from_csv, hex_color_to_numeric

from PARAMETERS import DATA_ROOT


##########################################################
#         Convert TIF to 4-bands-colored TIF             #
##########################################################

# get all the tif files
files = get_all_files(DATA_ROOT)
tif_files = files.query('base_ext.str.contains("tiff")')['path'].tolist()

# remove previously converted tif files
for tif_file in tif_files:
    if 'color' in tif_file:
        os.remove(tif_file)
        tif_files.remove(tif_file)

# convert tif to 4-bands-colored tif
num_workers = min(8, files['year'].nunique())
parallel_decorator = ParallelConvertDecorator(max_workers=num_workers, input_files=tif_files)
convert_tif_to_4band_parallel = parallel_decorator(convert_1band_to_4band)
convert_tif_to_4band_parallel()

# strip white spaces for each tif file
tif_files = files.query('base_ext.str.contains("tiff")')['path'].tolist()
for tif_file in tif_files:
    os.rename(tif_file, tif_file.replace(' ',''))

# create color style files
color_csvs = pd.read_csv('tools/color_map.csv')
color_csvs['color_num'] = color_csvs['color_HEX'].apply(lambda x: hex_color_to_numeric(x))
create_qml_from_csv(color_csvs['lu_code'], 
                    color_csvs['color_num'],
                    color_csvs['lu_desc'])





##########################################################
#             Add meta data to the notebooks             #
##########################################################

# remove the notebooks in the ebook folder
ebook_paths = glob('ebook/*.ipynb')
for nb_path in ebook_paths:
    os.remove(nb_path)


# add the meta data to the notebooks
nb_paths = glob('*.ipynb')
for nb_path in nb_paths:
    add_meta_to_nb(nb_path)
    os.system(f'cp {nb_path} ebook/')