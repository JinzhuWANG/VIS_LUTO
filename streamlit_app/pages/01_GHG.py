import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
from tools import get_all_files, get_GHG_file_df
from tools.Plot_GHG import get_GHG_plots,plot_GHG_total
from PARAMETERS import DATA_ROOT



 
################################################
#     Set up stremlit environment              #
################################################
st.set_page_config(
    page_title="GHG emissions",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.write('#')
st.title('GHG emissions')
st.write('#')

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


################################################
#                    Get files                 #
################################################
files = get_all_files(DATA_ROOT)


# Get the GHG files
GHG_files = get_GHG_file_df(files)
GHG_files = GHG_files.reset_index(drop=True).sort_values(['year','GHG_sum_t'])
GHG_files['GHG_sum_Mt'] = GHG_files['GHG_sum_t'] / 1e6


# Calculate the net emissions
Net_emission = GHG_files.groupby('year')['GHG_sum_Mt'].sum(numeric_only = True).reset_index()
Net_emission = Net_emission.rename(columns={'GHG_sum_Mt':'Net_emission'})
Net_emission['Net_emission_cum'] = Net_emission['Net_emission'].cumsum()


################################################
#       Get the selction for GHG types         #
################################################

# Show the total GHG emissions
st.sidebar.markdown('#### Check to show total GHG emissions')
Show_TOTAL_GHG = st.sidebar.checkbox('Total GHG emissions',value=True)


# Get the GHG types from one of 
#       ['Agricultural Landuse',
#        'Agricultural Management',
#        'Non-Agricultural Landuse', 
#        'Transition Penalty']
st.sidebar.header("#")
ghg_type = sorted(GHG_files['base_name'].unique()) 
ghg_type_selection = st.sidebar.radio('Which GHG category do you want to look into?',ghg_type)



################################################
#       Total GHG emissions across years       #
################################################
st.write('#')

if Show_TOTAL_GHG:

    # Get the cumulative plot and the individual plot
    cumsum_plot, individual_plot = plot_GHG_total(GHG_files, Net_emission)
    # Create two columns
    col1, col2 = st.columns(2)

    # Set plots into each column
    with col1:
        st.subheader('Total GHG emissions across years')
        st.altair_chart(individual_plot, use_container_width=True)
        # Download the data
        st.download_button(
            label="Download data",
            data=GHG_files[['year','base_name','GHG_sum_t']].to_csv(index=False).encode('utf-8'),
            file_name='GHG_emissions_sum.csv',
            mime='text/csv',
            help='Download the total GHG emissions across years'
        )
    
    with col2:
        st.subheader('Cumulative GHG emissions across years')
        st.altair_chart(cumsum_plot, use_container_width=True)
        
        # Download the data
        st.download_button(
            label="Download data",
            data=Net_emission.to_csv(index=False).encode('utf-8'),
            file_name='GHG_emissions_cumsum.csv',
            mime='text/csv',
            help='Download the cumulative GHG emissions across years'
        )
        
# white space lines
st.write('#')



################################################
#           Agricultural emissions             #
################################################

# Initialize the class
ag_lucc_GHG = get_GHG_plots(GHG_files,'Agricultural Landuse','GHG emissions (Mt CO2e)')


# get the df and plot
GHG_crop_lvstk_df,GHG_crop_lvstk_plot = ag_lucc_GHG.plot_GHG_crop_lvstk()
GHG_dry_irr_df,GHG_dry_irr_plot = ag_lucc_GHG.plot_GHG_dry_irr()
GHG_catetory_df,GHG_atetory_plot = ag_lucc_GHG.plot_GHG_category()
GHG_sources_df,GHG_sources_plot = ag_lucc_GHG.plot_GHG_sources()


# Link ghg type to the coresponding (plot,df)
Ag_GHG_types = {'Crop and Livestock':(GHG_crop_lvstk_plot,GHG_crop_lvstk_df),
                'Dry and Irrigation land':(GHG_dry_irr_plot,GHG_dry_irr_df),
                'GHG Category':(GHG_atetory_plot,GHG_catetory_df),
                'GHG Sources':(GHG_sources_plot,GHG_sources_df)}


if ghg_type_selection == 'Agricultural Landuse':
    st.sidebar.subheader('#')   
    GHG_type = st.sidebar.selectbox('Select GHG emissions from ...', Ag_GHG_types)
    
    st.header('#')
    st.markdown(f'### GHG emissions from Agricultural Landuse')
    st.altair_chart(Ag_GHG_types[GHG_type][0], use_container_width=True)
    
    # Download the data
    st.download_button(
        label="Download data",
        data=Ag_GHG_types[GHG_type][1].to_csv(index=False).encode('utf-8'),
        file_name='GHG_emissions_Ag_Landuse.csv',
        mime='text/csv',
        help='Download the GHG emissions from Agricultural Landuse'
    )
    
    
    
    # Get the landuse-irrigate-GHG plot
    st.sidebar.write('#')
    year = st.sidebar.select_slider('Select year to show detailed GHG emissions', GHG_files['year'].unique())
    GHG_lu_source_df,GHG_lu_source_plot = ag_lucc_GHG.plot_GHG_lu_source(year)


    st.write('#')
    st.write('#')
    
    st.write(f'### GHG emissions from Agricultural Landuse in {year}')
    st.altair_chart(GHG_lu_source_plot, use_container_width=True)
    # Download the data
    st.download_button(
        label="Download data",
        data=GHG_lu_source_df.to_csv(index=False).encode('utf-8'),
        file_name=f'GHG_emissions_Ag_Landuse_{year}.csv',
        mime='text/csv',
        help=f'Download the GHG emissions from Agricultural Landuse in {year}'
    )


    

################################################
#           Non-Agricultural emissions         #
################################################
non_ag_lucc_GHG = get_GHG_plots(GHG_files,'Non-Agricultural Landuse','GHG sequestration (Mt CO2e)')
GHG_non_ag_crop_lvstk_df,GHG_non_ag_crop_lvstk_plot = non_ag_lucc_GHG.plot_GHG_crop_lvstk()

Non_Ag_GHG_types = {'Environmental Plantings':(GHG_non_ag_crop_lvstk_plot,GHG_non_ag_crop_lvstk_df)}

if ghg_type_selection == 'Non-Agricultural Landuse':
    st.sidebar.subheader('#')   
    GHG_type = st.sidebar.selectbox('Select GHG emissions from ...', Non_Ag_GHG_types)
    
    st.header('#')
    st.markdown(f'### GHG emissions from Non-Agricultural Landuse')
    st.altair_chart(GHG_non_ag_crop_lvstk_plot, use_container_width=True)
    
    # Download the data
    st.download_button(
        label="Download data",
        data=GHG_non_ag_crop_lvstk_df.to_csv(index=False).encode('utf-8'),
        file_name='GHG_emissions_Non_Ag_Landuse.csv',
        mime='text/csv',
        help='Download the GHG emissions from Non-Agricultural Landuse'
    )





################################################
#     Agricultural management reductions       #
################################################

ag_man_GHG = get_GHG_plots(GHG_files,'Agricultural Management','GHG reductions (Mt CO2e)')

GHG_ag_man_GHG_crop_lvstk_df,GHG_ag_man_GHG_crop_lvstk_plot = ag_man_GHG.plot_GHG_crop_lvstk()
GHG_ag_man_dry_irr_df,GHG_ag_man_dry_irr_plot = ag_man_GHG.plot_GHG_dry_irr()
GHG_ag_man_df,GHG_ag_man_plot = ag_man_GHG.plot_GHG_category()

Ag_man_GHG_types = {'Crop and Livestock':(GHG_ag_man_GHG_crop_lvstk_plot,GHG_ag_man_GHG_crop_lvstk_df),
                    'Dry and Irrigation land':(GHG_ag_man_dry_irr_plot,GHG_ag_man_dry_irr_df),
                    'GHG Category':(GHG_ag_man_plot,GHG_ag_man_df)}

if ghg_type_selection == 'Agricultural Management':
    st.sidebar.subheader('#')   
    GHG_type = st.sidebar.selectbox('Select GHG reductions from ...', Ag_man_GHG_types)
    
    st.header('#')
    st.markdown(f'### GHG reductions from Agricultural Management')
    st.altair_chart(Ag_man_GHG_types[GHG_type][0], use_container_width=True)
    
    # Download the data
    st.download_button(
        label="Download data",
        data=Ag_man_GHG_types[GHG_type][1].to_csv(index=False).encode('utf-8'),
        file_name='GHG_redunctions_Ag_Management.csv',
        mime='text/csv',
        help='Download the GHG reductions from Agricultural Management'
    )
    
    
    
################################################
#           Transition Penalty                 #
################################################

if ghg_type_selection == 'Transition Penalty':
    st.header('#')
    st.markdown(f'### Transition Penalty is ALL ZERO in current scenario')














