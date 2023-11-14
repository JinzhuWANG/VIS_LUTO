import os
import altair as alt
import pandas as pd
from tqdm.auto import tqdm

# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import LU_CROPS, LU_LVSTKS, NON_AG_LANDUSE




class get_GHG_plots():
    """
    A class for generating greenhouse gas (GHG) emission plots.

    Parameters:
    -----------
    GHG_files : pd.DataFrame
        A pandas DataFrame containing the GHG files to be plotted.
    GHG_type : str
        The type of GHG to be plotted. Can only be one of the following: 
        ['Agricultural Landuse','Agricultural Management', 'Non-Agricultural Landuse', 'Transition Penalty'].
    GHG_value_name : str, optional
        The name of the GHG value to be plotted. Default is 'GHG emissions (Mt CO2e)'.

    Methods:
    --------
    read_GHG_to_long()
        Reads the GHG files to long format.
    plot_GHG_crop_lvstk()
        Plots the GHG emissions for crops and livestock.
    plot_GHG_dry_irr()
        Plots the GHG emissions for dry and irrigated land.
    plot_GHG_lu_lm(year)
        Plots the GHG emissions for land use and land management for a given year.
    plot_GHG_lu_source(year)
        Plots the GHG emissions for land use and GHG source for a given year.
    """
class get_GHG_plots():

    def __init__(self, 
                 GHG_files:pd.DataFrame,
                 GHG_type:str,
                 GHG_value_name:str = 'GHG emissions (Mt CO2e)'):

        # Get GHG file paths under the given GHG type
        self.GHG_files = GHG_files.query(f'base_name == "{GHG_type}"').reset_index(drop=True)
        self.GHG_type = GHG_type
        self.GHG_value_name = GHG_value_name
        self.GHG_df_long = self.read_GHG_to_long()

        # Check if the total GHG is negative
        self.reverse_scale = True if self.GHG_df_long['Quantity (Mt CO2e)'].to_numpy(na_value=0).sum() < 0 else False
        

        # Check if the GHG type is valid
        if GHG_type not in ['Agricultural Landuse','Agricultural Management', 
                            'Non-Agricultural Landuse', 'Transition Penalty']:
            
            raise ValueError('GHG_type can only be one of the following: \
                             ["Agricultural Landuse","Agricultural Management", \
                             "Non-Agricultural Landuse", "Transition Penalty"].')

    
    def read_GHG_to_long(self):

        # Read GHG emissions of ag lucc
        CSVs = []
        for _,row in tqdm(self.GHG_files.iterrows(),total=self.GHG_files.shape[0]):
            csv = pd.read_csv(row['path'],index_col=0,header=[0,1,2]).drop('SUM',axis=1)

            # Get the land use and land use category
            if self.GHG_type != 'Non-Agricultural Landuse':
                csv_crop = csv[[True if i in LU_CROPS else False for i in  csv.index]]
                csv_crop.index = pd.MultiIndex.from_product(([row['year']], csv_crop.index, ['Crop']))

                csv_lvstk = csv[[True if i in LU_LVSTKS else False for i in  csv.index]]
                csv_lvstk.index = pd.MultiIndex.from_tuples(tuple(csv_lvstk.index.str.split(' - ')))
                csv_lvstk = csv_lvstk.groupby(level=0).sum(numeric_only=True)
                csv_lvstk.index = pd.MultiIndex.from_product(([row['year']], csv_lvstk.index, ['Livestock']))

                csv = pd.concat([csv_crop,csv_lvstk],axis=0)
            else:
                csv = csv[[True if i in NON_AG_LANDUSE else False for i in  csv.index]]
                csv.index = pd.MultiIndex.from_product(([row['year']], csv.index, ['Non-Agricultural Landuse']))

            CSVs.append(csv)

        # Convert the GHG to long format, so that each variable is in one column
        GHG_df = pd.concat(CSVs,axis=0)
        GHG_df = GHG_df.droplevel(0,axis=1)
        
        GHG_df_long = GHG_df.copy()
        GHG_df_long.columns = ["+".join(i) for i in GHG_df_long.columns.tolist()]
        GHG_df_long = GHG_df_long.reset_index()
        GHG_df_long.columns = ['Year','Land use','Land use category'] + GHG_df_long.columns.tolist()[3:]

        GHG_df_long = GHG_df_long.melt(id_vars=['Year','Land use','Land use category'],
                                            value_vars=GHG_df_long.columns.tolist()[3:],
                                            value_name='val_t')


        GHG_df_long['Quantity (Mt CO2e)'] = GHG_df_long['val_t'] / 1e6
        GHG_df_long[['Irrigation','Sources']] = GHG_df_long['variable'].str.split('+',expand=True)
        GHG_df_long.drop(['val_t','variable'],axis=1,inplace=True)
        GHG_df_long = GHG_df_long.reindex(columns=['Year','Land use category','Land use',
                                                        'Irrigation','Sources', 'Quantity (Mt CO2e)'])

        return GHG_df_long
    

    def plot_GHG_crop_lvstk(self):

        # get the df
        GHG_crop_lvstk_total = self.GHG_df_long.groupby(['Year','Land use category']).sum(numeric_only=True).reset_index()

        # Create a base chart with the necessary transformations and encodings
        base_chart = alt.Chart(GHG_crop_lvstk_total).encode(
            x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
            tooltip=[alt.Tooltip('Land use category:O', title='Landuse type'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')]
        )

        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('Land use category:N', legend=alt.Legend(
                                                                    title="Landuse type",
                                                                    orient='none',
                                                                    legendX=350, legendY=-40,
                                                                    direction='horizontal',
                                                                    titleAnchor='middle')),  
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name} (Mt CO2e)',
                    scale=alt.Scale(reverse=self.reverse_scale,zero=False)),  
        )

        final_chart = alt.layer(
            column_chart,
        ).properties(
            width=800,
            height=450
        )

        return GHG_crop_lvstk_total, final_chart
    
    def plot_GHG_dry_irr(self):
        # make the long format table
        GHG_lm_total = self.GHG_df_long.groupby(['Year','Irrigation']).sum(numeric_only=True).reset_index()

        base_chart = alt.Chart(GHG_lm_total).encode(
        x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
        tooltip=[alt.Tooltip('Irrigation', title='Irrigation'),
                alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')]
        ).properties(
            width=600,
            height=400
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('Irrigation:N',legend=alt.Legend(
                                                            title="Irrigation",
                                                            orient='none',
                                                            legendX=350, legendY=-40,
                                                            direction='horizontal',
                                                            titleAnchor='middle')),  
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name} (Mt CO2e)',
                    scale=alt.Scale(reverse=self.reverse_scale))
        )



        final_chart = alt.layer(
            column_chart,
        ).properties(
            width=800,
            height=450
        )

        return GHG_lm_total, final_chart
    
    def plot_GHG_lu_lm(self,year):
        '''Input: year: int'''
        GHG_lu_lm = self.GHG_df_long\
                           .groupby(['Year','Land use category','Land use','Irrigation'])\
                           .sum(numeric_only=True)\
                           .reset_index()

        df_this_yr = GHG_lu_lm.query('Year == @year').reset_index(drop=True)
        plot = alt.Chart(df_this_yr).mark_bar().encode(
            tooltip=[alt.Tooltip('Land use:O', title='Landuse'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')],
            x="Quantity (Mt CO2e):Q",
            y="Land use:O",
            color="Irrigation:N"
        ).properties(width=500)

        return df_this_yr,plot
    
    def plot_GHG_lu_source(self,year):
        '''Input: year: int'''
        GHG_lu_source = self.GHG_df_long\
                                .groupby(['Year','Land use','Irrigation','Sources'])\
                                .sum(numeric_only=True)\
                                .reset_index()
        
        df_this_yr = GHG_lu_source.query(f'Year == {year}')
        plot = alt.Chart(df_this_yr).mark_circle().encode(
            alt.X('Land use:O'),
            alt.Y('Sources:O'),
            alt.Color('Irrigation:O'),
            alt.Size('Quantity (Mt CO2e):Q'),
            tooltip=[alt.Tooltip('Land use:O', title='Landuse'),
                     alt.Tooltip('Sources:O', title=f'GHG source'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')],
        ).properties(width=500)

        return df_this_yr,plot




