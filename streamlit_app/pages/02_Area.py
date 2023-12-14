import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
    
    
# Set the page title and icon
st.set_page_config(page_title='Area change', 
                   page_icon=':bar_chart:',
                   layout='wide')

st.write('#')
st.title('Area change')
st.write('#')


# import custom functions
import re
from tools import get_all_files
from PARAMETERS import DATA_ROOT
from tools.Plot_AREA import get_AREA_lu, get_begin_end_df, plot_area_lu,\
                            get_AREA_lm, plot_area_lm,\
                            get_AREA_am, plot_area_am_total, plot_area_am_lu, plot_begin_end_area_change
                            
# Get all output files
files = get_all_files(DATA_ROOT)



#######################################################
#                Total use area change                #
#######################################################
Area_df = files.query('catetory == "cross_table" and year_types == "single_year"').reset_index(drop=True)
crosstab_lu = Area_df.query('base_name == "crosstab-lumap"').reset_index(drop=True)
lu_area = get_AREA_lu(crosstab_lu)

crosstab_lm = Area_df.query('base_name == "crosstab-lmmap"').reset_index(drop=True)
lm_area = get_AREA_lm(crosstab_lm)



# write subheader
st.markdown('## Area change for each Land Use type')
st.altair_chart(plot_area_lu(lu_area), use_container_width=True)

# download the data
st.download_button(
    label="Download data",
    data=lu_area.to_csv(index=False).encode('utf-8'),
    file_name='Landuse_area_change.csv',
    mime='text/csv',
    help='Download the Area Change for each landuse across years'
)

st.write('#')
    


# write subheader
st.markdown('## Area change for dry/irrigated land')
st.altair_chart(plot_area_lm(lm_area), use_container_width=True)

# download the data
st.download_button(
    label="Download data",
    data=Area_df.to_csv(index=False).encode('utf-8'),
    file_name='Land_management_area_change.csv',
    mime='text/csv',
    help='Download the Area Change for each land management across years'
)

st.write('#')


#######################################################
#         Agricultural management area change         #
#######################################################

st.markdown('## Area change for each Agricultural Management type')

# get the data
switches_am = Area_df.query('base_name.str.contains(r"switches.*amstat.*", regex=True)').reset_index(drop=True)
am_area_km2 = get_AREA_am(switches_am)
am_area_km2[['Land use','Agricultural management']] = am_area_km2['Land use']\
                                                     .apply(lambda x: re.findall(r'(.*) \((.*)\)',x)[0]).tolist()
am_area_km2_total = am_area_km2.groupby(['Year','Agricultural management']).sum(numeric_only=True).reset_index()


# plot the data
st.subheader('Total agricultural management area')
st.altair_chart(plot_area_am_total(am_area_km2_total), use_container_width=True)
st.download_button(
    label="Download data",
    data=am_area_km2_total.to_csv(index=False).encode('utf-8'),
    file_name='Total_agricultural_management_area_change.csv',
    mime='text/csv',
    help='Download the Area Change for each agricultural management across years'
)

st.subheader('Agricultural management area by land use')
st.altair_chart(plot_area_am_lu(am_area_km2), use_container_width=True)
st.download_button(
    label="Download data",
    data=am_area_km2.to_csv(index=False).encode('utf-8'),
    file_name='Agricultural_management_area_by_landuse.csv',
    mime='text/csv',
    help='Download the Area Change for each agricultural management across years'
)



#######################################################
#       Land use change between begin/end years       #
#######################################################

begin_end_df_area, begin_end_df_pct = get_begin_end_df(files)
begin_yr,end_yr = files['year'].min(), files['year'].max()

# write the area with background style
st.write('## Area change between {} and {}'.format(begin_yr, end_yr))
st.markdown('- The unit is in square kilometers (km2)\n - Each row shows the transition from the land use in {} to the land use in {}'.format(begin_yr, end_yr))
st.write(begin_end_df_area.style.background_gradient(cmap='Oranges', axis=1).format('{:,.0f}'))

# Plot the percentage change
st.markdown('### Percentage change between {} and {}'.format(begin_yr, end_yr))
st.altair_chart(plot_begin_end_area_change(begin_end_df_pct,'web'), use_container_width=True)


