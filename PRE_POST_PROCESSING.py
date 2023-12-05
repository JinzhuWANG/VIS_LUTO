from glob import glob

from tqdm.auto import tqdm
from tools import add_meta_to_nb, get_all_files
from tools.TIF2color import convert_1band_to_4band

from PARAMETERS import DATA_ROOT


##########################################################
#         Convert TIF to 4-bands-colored TIF             #
##########################################################

# get all the tif files
files = get_all_files(DATA_ROOT)
tif_files = files.query('base_ext.str.contains("tiff")')['path'].tolist()

# convert tif to 4-bands-colored tif
for tif_file in tqdm(tif_files):
    # skip existing colored tif
    if 'colored' in tif_file:
        continue
    # set binary_color to True if the tif is land use tif
    binary_color=True if 'lu' in tif_file else False
    # convert tif to 4-bands-colored tif
    convert_1band_to_4band(tif_file)


##########################################################
#             Add meta data to the notebooks             #
##########################################################

# get the notebook paths
nb_paths = glob('*.ipynb')

# add the meta data to the notebooks
for nb_path in nb_paths:
    add_meta_to_nb(nb_path)