import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# set up working directory
import os
if __name__ == '__main__':
    os.chdir('/'.join(__file__.split('/')[:-1]))

# Set the page title and icon
st.set_page_config(page_title='Land Use Trade-Offs (LUTO) Model Insights', 
                   page_icon=':bar_chart:',
                   layout='wide')


# q: make the title close to the top of page
st.title(':bar_chart: Land Use Trade-Offs (LUTO) Model Insights')

with open('./LUTO_intro.md', 'r') as f: intro_str = f.readlines()
intro_str_1 = ('').join(intro_str[:16])
intro_str_2 = ('').join(intro_str[16:])

# two columns to show the LUTO introduction
col1, col2 = st.columns([3.7,5],gap = 'large')
with col1:
    st.markdown(intro_str_1)
with col2:
    st.markdown(intro_str_2)

st.markdown('<style>div.block-container{padding-top: 1rem;}</style>', 
            unsafe_allow_html=True)