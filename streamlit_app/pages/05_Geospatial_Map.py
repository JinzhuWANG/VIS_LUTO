import streamlit as st
from folium import Map, TileLayer
import leafmap.foliumap as leafmap
import pandas as pd


import warnings
warnings.filterwarnings('ignore')

# Set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
    
# import custom modules
from tools import get_all_files
from PARAMETERS import BASE2NAME, CAT2NAME, DATA_ROOT
from tools import get_range_tif_request

# Set page configuration
st.set_page_config(
    page_title="Map of LUTO simulation",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Write page title
st.write('#')
st.title('Geospatial Map')
st.write('#')


#####################################################
#                     Get map url                   #
#####################################################

# Set the endpoint for the TiTiler server
titiler_endpoint = "http://170.64.253.130:8000"

# Get all output files
files = get_all_files(DATA_ROOT)
maps = files.query('catetory.str.contains("map") and base_ext == ".tiff" and base_name.str.contains("color") and year_types == "single_year"').reset_index(drop=True)

# rename the columns to sensible names
maps['catetory'] = maps['catetory'].apply(lambda x: CAT2NAME[x])
maps['base_name'] = maps['base_name'].apply(lambda x: BASE2NAME[x])

# two columns for map selection
col1,col2 = st.columns(2)

########################### Select map for the left panel #############################
with col1:
    # Set up sidebar and filter the maps
    select_year = st.select_slider("Select Year", sorted(maps['year'].unique()))
    maps_year = maps.query('year == @select_year').reset_index(drop=True)

    selcect_cat = st.selectbox("Select Category", sorted(maps_year['catetory'].unique()))
    maps_cat = maps_year.query('catetory == @selcect_cat').reset_index(drop=True)


    # Only when the number of base_name is greater than 1, then we need to add a selectbox
    if len(maps_cat['base_name'].unique()) > 1:
        select_base = st.selectbox("Select Base", sorted(maps_cat['base_name'].unique()))
        maps_base = maps_cat.query('base_name == @select_base').reset_index(drop=True)
    else:
        maps_base = maps_cat.reset_index(drop=True)
        

    # get the path to the tif file
    tif_path = maps_base['path'][0].split('LUTO_DATA/')[1]
    tif_url = f'http://170.64.253.130:8080/LUTO_DATA/{tif_path}'



    # Get tileset from map_path_url
    tile_json_analytic = get_range_tif_request(titiler_endpoint, "cog/tilejson.json", tif_url)
    tileset = tile_json_analytic["tiles"][0]


#####################################################
#          Overlay tif_url to a map                 #
#####################################################

# get the metadata from the legend of land use classes
color_csvs = pd.read_csv('tools/color_map.csv')
legend_dict = dict(color_csvs[['lu_desc','color_HEX']].values)


#################### Leafmap  #######################
map = leafmap.Map(center=(-27, 134),
                  zoom=4,
                  draw_control=False,
                  measure_control=False,
                #   fullscreen_control=False,
                  attribution_control=True)

map.add_tile_layer(
    url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    name="ESRI Satellite",
    attribution="ESRI",
)

map.add_tile_layer(
    tileset,
    layers="LUTO",
    name="LUTO",
    format="image/png",
    transparent=True,
    attribution='LUTO'
)

map.add_legend(title="LUTO Classification", legend_dict=legend_dict)

map.to_streamlit(height=700)















 
