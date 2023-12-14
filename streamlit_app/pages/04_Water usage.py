import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
    
# Import custom functions
from tools import get_all_files
from PARAMETERS import DATA_ROOT

from tools.Plot_Water import plot_water_percent, get_water_df, plot_water_use_volum

# Get all output files
files = get_all_files(DATA_ROOT)

water_dfs = files.query('catetory == "water" and year_types == "single_year"').reset_index(drop=True)
water_df = get_water_df(water_dfs)


# Write page title
st.title('Water usage')
st.write('#')



###############################################
#           Total Water Usage                 #
###############################################

water_type = st.sidebar.selectbox('Select water type', ['Absolute volume (million T)','Percentage to limit  (%)'])

if water_type == 'Absolute volume (million T)':
    # plot the total water usage using line plot
    st.write('## Total water usage (million T)')
    st.altair_chart(plot_water_use_volum(water_df,'st'), use_container_width=True)
    # download data
    st.download_button(
        label="Download data (csv)",
        data=water_df.to_csv(index=False),
        file_name='water_usage_volume.csv',
        mime='text/csv',
        )
    
elif water_type == 'Percentage to limit  (%)':
    # plot the PROPORTION_% change overtime using line plot
    st.write('## Percentage to limit  (%)')
    st.altair_chart(plot_water_percent(water_df,'st'), use_container_width=True)
    # download data
    st.download_button(
        label="Download data (csv)",
        data=water_df.to_csv(index=False),
        file_name='water_usage_percent.csv',
        mime='text/csv',
        )









