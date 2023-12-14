import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-3]))
    

# Set the page title and icon
st.set_page_config(page_title='Commodity Production and Profit', 
                   page_icon=':bar_chart:',
                   layout='wide')

st.write('#')
st.title('Commodity Production and Profit')
st.write('#')


# Import the tools
from tools import get_all_files
from PARAMETERS import DATA_ROOT

from tools.Plot_Quantity import plot_quantity, get_quantity_df, get_rev_cost_df,\
                                plot_rev_source, plot_rev_crop_lvstk, plot_rev_irrigation,\
                                plot_cost_source, plot_cost_type, plot_cost_water,\
                                get_profit_plot


# Get all output files
files = get_all_files(DATA_ROOT)


##############################################################
#               Total Commodity proeuction                    #
##############################################################

st.sidebar.markdown('#### Click to show total commodity production')
show_quantity = st.sidebar.checkbox('Total commodity production', value=True)

if show_quantity:
    Quantity_df = files.query('catetory == "quantity" and base_name == "quantity_comparison" and year_types == "single_year"').reset_index(drop=True)
    quantity_df = get_quantity_df(Quantity_df)

    # White space and title
    st.write('#')
    st.write('#')
    st.markdown('## Total Commodity Production')

    # Plot the total production
    st.altair_chart(plot_quantity(quantity_df,'st'), use_container_width=True)

    # Download the data
    st.download_button(label='Download data',data=quantity_df.to_csv(index=False),file_name='quantity.csv',mime='text/csv')


# Get the Selection for Revenue, Cost, and Profit
st.sidebar.markdown('#### Which statistics to show?')
select_type = st.sidebar.selectbox('Select type', ['Revenue', 'Cost', 'Profit'])


##############################################################
#                      Total Revenue                         #
##############################################################

# Get the revenue data
revenue_df = get_rev_cost_df(files, 'revenue')

# Get the types for revenue
if select_type == 'Revenue':

    # Get the selection for segregation
    segregation_type = st.sidebar.selectbox('Select segregation type', ['Commodity', 'Crop and Livestock', 'Irrigation'])
    

    # Segregate the data by commodity
    if segregation_type == 'Commodity':
       
        st.write('#')
        st.write('#')
        st.markdown('## Total Revenue')

        # Plot the total revenue
        st.markdown('#### Total Revenue by Commodity')
        st.altair_chart(plot_rev_source(revenue_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='Revenue_by_commodity.csv',mime='text/csv')


    # Segregate the data by crop and livestock
    if segregation_type == 'Crop and Livestock':
        
        st.write('#')
        st.write('#')
        st.markdown('## Total Revenue')

        # Plot the total revenue
        st.markdown('#### Total Revenue by Crop and Livestock')
        st.altair_chart(plot_rev_crop_lvstk(revenue_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='Revenue_by_crop_lvstk.csv',mime='text/csv')
    
    # Segregate the data by irrigation
    if segregation_type == 'Irrigation':
        
        st.write('#')
        st.write('#')
        st.markdown('## Total Revenue')

        # Plot the total revenue
        st.markdown('#### Total Revenue by Irrigation')
        st.altair_chart(plot_rev_irrigation(revenue_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='Revenue_by_irrigation.csv',mime='text/csv')



##############################################################
#                      Total Cost                            #
##############################################################

# Get the cost data
cost_df = get_rev_cost_df(files, 'cost')

if select_type == 'Cost':
    
    cost_type = st.sidebar.selectbox('Select cost type', ['Commodity', 'Type', 'Water Source'])

    # white space and title
    st.write('#')
    st.write('#')
    st.markdown('# Total Cost')

    
    # Plot the total cost by commodity
    if cost_type == 'Commodity':
        st.markdown('#### Total Cost by Commodity')
        st.altair_chart(plot_cost_source(cost_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='cost_by_commodity.csv',mime='text/csv')

    # Plot the total cost by water source
    if cost_type == 'Water Source':
        st.markdown('#### Total Cost by Water Source')
        st.altair_chart(plot_cost_water(cost_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='cost_by_water.csv',mime='text/csv')
        
    # Plot the total cost by type
    if cost_type == 'Type':
        st.markdown('#### Total Cost by Type')
        st.altair_chart(plot_cost_type(cost_df, env='st'), use_container_width=True)
        # download the data
        st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='cost_by_type.csv',mime='text/csv')


##############################################################
#                      Total Profit                          #
##############################################################

# white space and title
st.write('#')
st.write('#')

# Plot the total profit
if select_type == 'Profit':
    
    st.markdown('# Total Profit')
    st.altair_chart(get_profit_plot(revenue_df, cost_df, env='st'), use_container_width=True)
    # download the data
    st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='profit.csv',mime='text/csv')


