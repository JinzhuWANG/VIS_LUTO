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
#               Total Comodity proeuction                    #
##############################################################

Quantity_df = files.query('catetory == "quantity" and base_name == "quantity_comparison" and year_types == "single_year"').reset_index(drop=True)
quantity_df = get_quantity_df(Quantity_df)

# White space and title
st.write('#')
st.write('#')
st.markdown('## Total Comodity Production')

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

# Get the types for revenue
if select_type == 'Revenue':

    revenue_df = get_rev_cost_df(files, 'revenue')
    
    
    # white space and title
    st.write('#')
    st.write('#')
    st.markdown('## Total Revenue')

    # Plot the total revenue
    st.markdown('#### Total Revenue by Commodity')
    st.altair_chart(plot_rev_source(revenue_df, env='st'), use_container_width=True)
    # download the data
    st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='Revenue_by_commodity.csv',mime='text/csv')


    # Plot the total revenue by crop and livestock
    st.markdown('#### Total Revenue by Crop and Livestock')
    st.altair_chart(plot_rev_crop_lvstk(revenue_df, env='st'), use_container_width=True)
    # download the data
    st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='revenue_by_crop_lvstk.csv',mime='text/csv')

    # Plot the total revenue by irrigation
    st.markdown('#### Total Revenue by dryland and irrigated')
    st.altair_chart(plot_rev_irrigation(revenue_df, env='st'), use_container_width=True)
    # download the data
    st.download_button(label='Download data',data=revenue_df.to_csv(index=False),file_name='revenue_by_irrigation.csv',mime='text/csv')




##############################################################
#                      Total Cost                            #
##############################################################

cost_df = get_rev_cost_df(files, 'cost')

# white space and title
st.write('#')
st.write('#')

# Plot the total cost
st.markdown('# Total Cost')


# Plot the total cost by commodity
st.markdown('#### Total Cost by Commodity')
st.altair_chart(plot_cost_source(cost_df, env='st'), use_container_width=True)
# download the data
st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='cost_by_commodity.csv',mime='text/csv')

# Plot the total cost by type
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
st.markdown('# Total Profit')
st.altair_chart(get_profit_plot(revenue_df, cost_df, env='st'), use_container_width=True)
# download the data
st.download_button(label='Download data',data=cost_df.to_csv(index=False),file_name='profit.csv',mime='text/csv')


