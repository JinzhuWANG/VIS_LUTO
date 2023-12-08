import os
import altair as alt
import pandas as pd


# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import  PLOT_HEIGHT, PLOT_WIDTH


# function to concatenate all the quantity dfs and return it for plotting
def get_quantity_df(in_dfs):
    all_dfs = []
    for idx,row in in_dfs.iterrows():

        # read the df
        df = pd.read_csv(row['path'])

        # get the df for the year of the loop
        df_this_yr = df[['Commodity','Prod_targ_year (tonnes, KL)']].copy()             ## TODO: change the columns name to actual year
        df_this_yr['year'] = row['year']

        # check if this is the first row, then get the df for base year
        if idx == 0:
            df_base_yr = df[['Commodity','Prod_base_year (tonnes, KL)']].copy()         ## TODO: change the columns name to actual year 
                                                                                        #        f'Prod_{base_year} (tonnes, KL)' at the next LUTO update
            # add the year to the df
            df_base_yr['year'] = row['year']

        # append df
        all_dfs.append(df_this_yr)


    # concatenate all the dfs, and made a column with the unit of Million tonnes
    all_df = pd.concat(all_dfs).reset_index(drop=True)
    all_df['Prod_targ_year (tonnes, ML)'] = all_df['Prod_targ_year (tonnes, KL)']/1000

    # rename the commodity column so that the first letter is capitalised
    all_df['Commodity'] = all_df['Commodity'].str.capitalize()
    
    return all_df


# function to plot the quantity change over time using column chart
def plot_quantity(df):
    plot =  alt.Chart(df).mark_bar().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('Prod_targ_year (tonnes, ML):Q', title='Production (tonnes, ML)'),
            color=alt.Color('Commodity:N', title='Commodity',
                            legend=alt.Legend(title="Commodity",
                                              orient='none',
                                              legendX=PLOT_WIDTH+20, legendY=+80,
                                              direction='vertical',
                                              titleAnchor='start')),
            tooltip=[alt.Tooltip('Commodity:N',title='Commodity'),
                     alt.Tooltip('Prod_targ_year (tonnes, ML):Q',title='Quantity (tonnes, ML)', format='.2f')],
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT)
    
    return plot

