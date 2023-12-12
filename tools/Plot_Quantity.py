import os
import altair as alt
import pandas as pd


# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import  LU_CROPS, LU_LVSTKS, PLOT_HEIGHT, PLOT_WIDTH


#####################################################################
#                      Quantity Plotting                            #
#####################################################################

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
                            scale=alt.Scale(scheme='tableau20'),
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


#####################################################################
#                      Ecomonic Value Plotting                      #
#####################################################################

def sum_lvstk(path:str):
    df = pd.read_csv(path,index_col=0,header=[0,1])
    # remove the last row and col
    df = df.iloc[:-1,:-1]
    # merge the rows with the name of ['Beef', 'Dairy', 'Sheep'] into one row, individually
    df_lvstk = df.loc[LU_LVSTKS]
    # splitting the index into two columns
    df_lvstk[['lu','land']] = df_lvstk.index.str.split('-').tolist()
    # sum the rows with the same land use
    df_lvstk = df_lvstk.groupby(['lu']).sum(numeric_only=True)
    # remove the rows with the name of ['Beef', 'Dairy', 'Sheep']
    df = df.drop(LU_LVSTKS,axis=0)
    # merge the df_lvstk into df
    df = pd.concat([df,df_lvstk]) 
    return df


def df_wide2long(df:pd.DataFrame):
    
    # remove the last row and col, sum the rows of ['Beef', 'Dairy', 'Sheep']
    df = sum_lvstk(df)
    # flatten the multi-index column
    df.columns = ['='.join(col) for col in df.columns.values]
    # melt the dataframe
    df = df.reset_index(names='Source').melt(id_vars=['Source'], value_vars=df.columns[1:])
    # # split the column into two, and remove the original column
    df[['Irrigation','Type']] = df['variable'].str.split('=',expand=True)
    # convert the value into billion
    df['value (billion)'] = df['value']/1e9   
    df = df.drop(['variable','value'],axis=1)

    return df


def get_rev_cost_df(files_df:pd.DataFrame,in_type:str):
    '''
    files_df: a dataframe with the following columns:
                - path: the path of the csv file
                - year: the year of the csv file
                - category: either 'revenue' or 'cost'
                - year_types: either 'single_year' or 'multi_year'
    in_type: either 'revenue' or 'cost'
    '''
    
    # in_type = 'Revenue' or 'Cost', otherwise raise error
    if in_type not in ['revenue','cost']:
        raise ValueError('in_type must be either "Revenue" or "Cost"')
    
    path_df = files_df.query('catetory == @in_type and year_types == "single_year"').reset_index(drop=True) 
        
    dfs =[]  
    for _,row in path_df.iterrows():
        df = df_wide2long(row['path'])
        # insert year as a column
        df.insert(0, 'year', row['year'])
        dfs.append(df)
    
    # concatenate all the dfs, remove rows with value of 0    
    out_df = pd.concat(dfs).reset_index(drop=True)
    out_df = out_df.query('`value (billion)` != 0')
    
    # sort the df by year, Source
    out_df = out_df.sort_values(['year','Source']).reset_index(drop=True)
    
    # merge the Source and Type columns
    out_df['Source_type'] = out_df.apply(lambda x: x['Source'] + ' ' + x['Type'], axis=1)
    
    # manually change the Source_type to remove "Revenue" from "Crop Revenue", and change "Dairy Milk" to "Dairy"
    out_df['Source_type'] = out_df['Source_type'].str.replace(' Revenue','')
    out_df['Source_type'] = out_df['Source_type'].str.replace('Dairy  Milk','Dairy')
    
    # add the column to show if this is a corp or livestock
    lvstk = [i.split(' - ')[0] for i in LU_LVSTKS]
    out_df['crop_lvstk'] = out_df['Source'].apply(lambda x: 'Crop' if any(x == s for s in LU_CROPS) else 'Livestock')

    return out_df




def plot_rev_source(revenue_df):
    
    revenue_df_source = revenue_df.groupby(['year', 'Source_type']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(revenue_df_source).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Revenue (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Revenue (billion AU$)'), 
                'Source_type'],
        color= alt.Color('Source_type:N', 
                        scale=alt.Scale(scheme='tableau20')
                        ,legend=alt.Legend(title="Commodity",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=80,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )

    return plot


def plot_rev_crop_lvstk(revenue_df):
    revenue_df_crop_lvstk = revenue_df.groupby(['year', 'crop_lvstk']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(revenue_df_crop_lvstk).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Revenue (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Revenue (billion AU$)'), 
                alt.Tooltip('crop_lvstk:N', title='Type')],
        color= alt.Color('crop_lvstk:N', 
                        legend=alt.Legend(title="Type",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT/2,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )

    return plot


def plot_rev_irrigation(revenue_df):
    revenue_df_irrigation = revenue_df.groupby(['year', 'Irrigation']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(revenue_df_irrigation).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Revenue (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Revenue (billion AU$)'), 
                alt.Tooltip('Irrigation:N', title='Irrigation')],
        color= alt.Color('Irrigation:N', 
                        legend=alt.Legend(title="Irrigation",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT/2,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )

    return plot


def plot_cost_source(cost_df):
    cost_df_source = cost_df.groupby(['year', 'Source']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(cost_df_source).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Cost (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Cost (billion AU$)'), 
                'Source'],
        color= alt.Color('Source:N', 
                        scale=alt.Scale(scheme='tableau20')
                        ,legend=alt.Legend(title="Land Use",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=80,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )
    
    return plot


def plot_cost_type(cost_df):
    cost_df_type = cost_df.groupby(['year', 'Type']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(cost_df_type).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Cost (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Cost (billion AU$)'), 
                'Type'],
        color= alt.Color('Type:N', 
                        legend=alt.Legend(title="",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT/2,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )

    return plot


def plot_cost_water(cost_df):
    cost_df_water = cost_df.groupby(['year', 'Irrigation']).sum(numeric_only=True).reset_index()

    plot = alt.Chart(cost_df_water).mark_bar().encode(
        x='year:O',
        y=alt.Y('value (billion):Q',title='Cost (billion AU$)'),
        tooltip=[alt.Tooltip('value (billion):Q', format='.2f', title='Cost (billion AU$)'), 
                'Irrigation'],
        color= alt.Color('Irrigation:N', 
                        legend=alt.Legend(title="Commodity",
                                            orient='none',
                                            legendX=PLOT_WIDTH+10, legendY=80,
                                            direction='vertical',
                                            titleAnchor='start')),
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    )

    return plot



def get_profit_plot(revenue_df,cost_df):
    
    rev_source = revenue_df.groupby(['year', 'Source']).sum(numeric_only=True).reset_index()
    cost_source = cost_df.groupby(['year', 'Source']).sum(numeric_only=True).reset_index()

    rev_cost_source = rev_source.merge(cost_source, on=['year', 'Source'], suffixes=('_rev', '_cost'))

    # rename columns
    rev_cost_source = rev_cost_source.rename(columns={'value (billion)_rev': 'Revenue (billion)',
                                                    'value (billion)_cost': 'Cost (billion)'})
    # calculate profit
    rev_cost_source['Cost (billion)'] = -rev_cost_source['Cost (billion)']
    rev_cost_source['Profit (billion)'] = rev_cost_source['Revenue (billion)'] + rev_cost_source['Cost (billion)']

    rev_cost_all = rev_cost_source.groupby('year').sum(numeric_only=True).reset_index()

    # add two dummy columns for plotting the color of rev and cost
    rev_cost_all['rev_color'] = 'Revenue'
    rev_cost_all['cost_color'] = 'Cost'

    base = alt.Chart(rev_cost_all).encode(
        x=alt.X('year:O', title='Year'),
    )

    revenue_plot = base.mark_bar(size=6,xOffset=-3).encode(
        y=alt.Y('Revenue (billion):Q', title='Value (billion)'),
        color=alt.Color('rev_color:N',
                        scale=alt.Scale(range=['#1f77b4']),
                        legend=alt.Legend(
                                        title=None,
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.48,
                                        direction='vertical',
                                        titleAnchor='start')),
    ) 

    cost_plot = base.mark_bar(size=6,xOffset=3,color='#ff7f0e').encode(
        y=alt.Y('Revenue (billion):Q'),
        y2=alt.Y2('Profit (billion):Q'),
        color=alt.Color('cost_color:N',
                        scale=alt.Scale(range=['#ff7f0e']),
                        legend=alt.Legend(
                                        title=None,
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.45,
                                        direction='vertical',
                                        titleAnchor='start')),
    )

    plot = alt.layer(revenue_plot, cost_plot).properties(
                width=PLOT_WIDTH,
                height=PLOT_HEIGHT).resolve_scale(
        color='independent'
    )
    
    return plot