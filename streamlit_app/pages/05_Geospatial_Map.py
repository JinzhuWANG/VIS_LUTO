import streamlit as st
import folium
from folium import Map, TileLayer
import leafmap
import pandas as pd


import warnings
warnings.filterwarnings('ignore')

# Set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
    
# import custom modules
from tools import get_all_files
from PARAMETERS import DATA_ROOT
from tools import get_range_tif_request

# Set page configuration
st.set_page_config(
    page_title="Geospatial Map",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Write page title
st.title('Geospatial Map')


#####################################################
#            Tile Server Configuration              #
#####################################################

# Set the endpoint for the TiTiler server
titiler_endpoint = "http://170.64.253.130:8000" 
