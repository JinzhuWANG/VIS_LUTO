import os
import altair as alt
import pandas as pd
from tqdm.auto import tqdm

# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import GHG_CATEGORY, LU_CROPS, LU_LVSTKS, NON_AG_LANDUSE



class get_GHG_plots():
    """
The `get_GHG_plots` class is responsible for generating plots related to greenhouse gas (GHG) emissions. It takes in GHG data in the form of a pandas DataFrame, the type of GHG, and an optional GHG value name. The class provides methods to plot GHG emissions by land use category, by irrigation type, by GHG category, and by land use and GHG source.

Example Usage:
    # Create an instance of the get_GHG_plots class
    ghg_plots = get_GHG_plots(GHG_files, 'Agricultural Landuse')

    # Plot GHG emissions by land use category
    ghg_crop_lvstk_total, crop_lvstk_chart = ghg_plots.plot_GHG_crop_lvstk()
    crop_lvstk_chart.show()

    # Plot GHG emissions by irrigation type
    ghg_lm_total, lm_chart = ghg_plots.plot_GHG_dry_irr()
    lm_chart.show()

    # Plot GHG emissions by GHG category
    ghg_category_total, category_chart = ghg_plots.plot_GHG_category()
    category_chart.show()

    # Plot GHG emissions by land use and irrigation type for a specific year
    year = 2022
    lu_lm_df, lu_lm_plot = ghg_plots.plot_GHG_lu_lm(year)
    lu_lm_plot.show()

    # Plot GHG emissions by land use and GHG source for a specific year
    lu_source_df, lu_source_plot = ghg_plots.plot_GHG_lu_source(year)
    lu_source_plot.show()

Methods:
    - __init__(self, GHG_files:pd.DataFrame, GHG_type:str, GHG_value_name:str = 'GHG emissions (Mt CO2e)'): Initializes the get_GHG_plots class by setting the GHG files, GHG type, and GHG value name. It also checks if the GHG type is valid.
    - read_GHG_to_long(self): Reads the GHG emissions data and converts it to a long format, where each variable is in one column.
    - get_GHG_category(self): Categorizes the GHG emissions into CO2 and non-CO2 GHGs.
    - plot_GHG_crop_lvstk(self): Plots GHG emissions by land use category. The plot can be either a bar chart or a line chart depending on the GHG type.
    - plot_GHG_dry_irr(self): Plots GHG emissions by irrigation type using a bar chart.
    - plot_GHG_category(self): Plots GHG emissions by GHG category using a bar chart.
    - plot_GHG_lu_lm(self, year): Plots GHG emissions by land use and irrigation type for a specific year using a bar chart.
    - plot_GHG_lu_source(self, year): Plots GHG emissions by land use and GHG source for a specific year using a scatter plot.

Fields:
    - GHG_files: A pandas DataFrame containing the GHG emissions data.
    - GHG_type: A string representing the type of GHG.
    - GHG_value_name: A string representing the name of the GHG value. Default is 'GHG emissions (Mt CO2e)'.
    - GHG_df_long: A pandas DataFrame containing the GHG emissions data in long format.
    - reverse_scale: A boolean indicating whether the scale of the GHG emissions should be reversed.
"""

    def __init__(self, GHG_files: pd.DataFrame, GHG_type: str, GHG_value_name: str = 'GHG emissions (Mt CO2e)'):
        """
        Initializes a Plot_GHG object.

        Parameters:
        -----------
        GHG_files : pd.DataFrame
            A pandas DataFrame containing information about GHG files.
        GHG_type : str
            The type of GHG to plot. Must be one of the following: 
            ["Agricultural Landuse","Agricultural Management","Non-Agricultural Landuse","Transition Penalty"].
        GHG_value_name : str, optional
            The name of the GHG emissions column in the GHG files. Default is 'GHG emissions (Mt CO2e)'.

        Raises:
        -------
        ValueError
            If GHG_type is not one of the valid options.

        """
    def __init__(self, 
                 GHG_files:pd.DataFrame,
                 GHG_type:str,
                 GHG_value_name:str = 'GHG emissions (Mt CO2e)'):

        # Get GHG file paths under the given GHG type
        self.GHG_files = GHG_files.query(f'base_name == "{GHG_type}"').reset_index(drop=True)
        self.GHG_type = GHG_type
        self.GHG_value_name = GHG_value_name
        self.GHG_df_long = self.read_GHG_to_long()
        self.GHG_df_long = self.get_GHG_category()

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
    





    def get_GHG_category(self):

        # 1) get CO2 GHG
        GHG_CO2 = self.GHG_df_long.query('~Sources.isin(@GHG_CATEGORY.keys())').copy()
        GHG_CO2['GHG Category'] = 'CO2'

        # 2) get non-CO2 GHG
        GHG_nonCO2 = self.GHG_df_long.query('Sources.isin(@GHG_CATEGORY.keys())').copy()
        GHG_nonCO2['GHG Category'] = GHG_nonCO2['Sources'].apply(lambda x: GHG_CATEGORY[x].keys())
        GHG_nonCO2['Multiplier'] = GHG_nonCO2['Sources'].apply(lambda x: GHG_CATEGORY[x].values())
        GHG_nonCO2 = GHG_nonCO2.explode(['GHG Category','Multiplier']).reset_index(drop=True)
        GHG_nonCO2['Quantity (Mt CO2e)'] = GHG_nonCO2['Quantity (Mt CO2e)'] * GHG_nonCO2['Multiplier']
        GHG_nonCO2 = GHG_nonCO2.drop(columns=['Multiplier'])

        return pd.concat([GHG_CO2,GHG_nonCO2],axis=0).reset_index(drop=True)
    






    def plot_GHG_crop_lvstk(self):

        # get the df
        GHG_crop_lvstk_total = self.GHG_df_long.groupby(['Year','Land use category']).sum()['Quantity (Mt CO2e)'].reset_index()

        # Create a base chart with the necessary transformations and encodings
        base_chart = alt.Chart(GHG_crop_lvstk_total).encode(
            x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
            tooltip=[alt.Tooltip('Land use category:O', title='Landuse type'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')]
        )


        if self.GHG_type != 'Non-Agricultural Landuse':
            chart = base_chart.mark_bar().encode(
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
            
        else:
            # use line chart
            chart = base_chart.mark_line().encode(
            color=alt.Color('Land use category:N',
                            legend=alt.Legend(title="Landuse type",
                                                orient='none',
                                                legendX=350, legendY=-40,
                                                direction='horizontal',
                                                titleAnchor='middle')),
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name} (Mt CO2e)',
                    scale=alt.Scale(reverse=self.reverse_scale)),
        )
            

        final_chart = alt.layer(
            chart,
        ).properties(
            width=800,
            height=450
        )

        return GHG_crop_lvstk_total, final_chart
    



    
    def plot_GHG_dry_irr(self):
        # make the long format table
        GHG_lm_total = self.GHG_df_long.groupby(['Year','Irrigation']).sum()['Quantity (Mt CO2e)'].reset_index()

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
    





    def plot_GHG_category(self):
        # make the long format table
        GHG_category_total = self.GHG_df_long.groupby(['Year','GHG Category']).sum()['Quantity (Mt CO2e)'].reset_index()

        base_chart = alt.Chart(GHG_category_total).encode(
                x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
                tooltip=[alt.Tooltip('GHG Category', title='GHG Category'),
                         alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')]
        ).properties(
            width=600,
            height=400
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('GHG Category:N',legend=alt.Legend(
                                                            title="GHG Category",
                                                            orient='none',
                                                            legendX=320, legendY=-30,
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

        return GHG_category_total, final_chart
    


    def plot_GHG_sources(self):

        # plot the GHG emissions of different Sources across years
        GHG_sources_total = self.GHG_df_long.groupby(['Year','Sources']).sum()['Quantity (Mt CO2e)'].reset_index()

        base_chart = alt.Chart(GHG_sources_total).encode(
                x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
                tooltip=[alt.Tooltip('Sources', title='GHG Sources'),
                        alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}')]
        ).properties(
            width=600,
            height=400
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('Sources:N',legend=alt.Legend(
                                                        title="GHG Sources",
                                                        orient='none',
                                                        legendX=320, legendY=-30,
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

        return GHG_sources_total, final_chart



    
    
    def plot_GHG_lu_lm(self,year):
        '''Input: year: int'''
        GHG_lu_lm = self.GHG_df_long\
                           .groupby(['Year','Land use category','Land use','Irrigation'])\
                           .sum()['Quantity (Mt CO2e)']\
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
                                .sum()['Quantity (Mt CO2e)']\
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




