from tools import add_meta_to_nb
from glob import glob

# get the notebook paths
nb_paths = glob('*.ipynb')

# add the meta data to the notebooks
for nb_path in nb_paths:
    add_meta_to_nb(nb_path)