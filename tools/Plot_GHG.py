import os
import altair as alt
import pandas as pd
from tqdm.auto import tqdm

# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import GHG_CATEGORY, GHG_NAMES, LU_CROPS, LU_LVSTKS, NON_AG_LANDUSE, PLOT_HEIGHT, PLOT_WIDTH




def plot_GHG_total(GHG_files, Net_emission):

    # Create a base chart with the necessary transformations and encodings
    column_chart_individual = alt.Chart(
        GHG_files
    ).mark_bar().encode(
        tooltip=[alt.Tooltip('base_name', title='GHG Category'),
                alt.Tooltip('GHG_sum_Mt:Q', title='Emissions (Mt CO2e)',format=",.2f")],
        x=alt.X('year:O',axis=alt.Axis(title="Year", labelAngle=-90)), 
        y=alt.Y('GHG_sum_Mt:Q',title='Emissions (Mt CO2e)'),  
        color=alt.Color('base_name:N',legend=alt.Legend(
                                                title=None,
                                                orient='none',
                                                legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.3,
                                                direction='vertical',
                                                titleAnchor='middle')), 
        
    )



    # Create a column chart to show the cumsum emissions
    column_chart_cumsum = alt.Chart(
        Net_emission
    ).mark_bar(
        color='grey',opacity=0.2
    ).transform_calculate(
        Cumulative_emissions =  'datum.year > 0 ? "Cumulative emissions" : "Cumulative emissions"'
    ).encode(  
        tooltip=[alt.Tooltip('Net_emission_cum:Q',title='Cumulative Quantity (Mt CO2e)',format=",.2f")],
        color=alt.Color('Cumulative_emissions:N',
                        scale=alt.Scale(range=['#181818'])  ,
                        legend=alt.Legend(title=None,
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.45,
                                        direction='vertical',
                                        titleAnchor='middle')),
        x=alt.X('year:O'),
        y=alt.Y('Net_emission_cum:Q',title='Emissions (Mt CO2e)'), 
    )


    # Create a line chart for net emissions
    line_chart_net = alt.Chart(
        Net_emission
    ).transform_calculate(
        Net_emission_color =  'datum.year > 0 ? "Net emissions" : "Net emissions"'
    ).mark_line(
        opacity=0.6
    ).encode(
        tooltip=[alt.Tooltip('Net_emission:Q',title='Net Quantity (Mt CO2e)',format=",.2f")],
        color=alt.Color('Net_emission_color:N',
                        scale=alt.Scale(range=['black']),
                        legend=alt.Legend(
                                        title=None,
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.48,
                                        direction='vertical',
                                        titleAnchor='middle')),
        x=alt.X('year:O'),
        y=alt.Y('Net_emission:Q',title='Emissions (Mt CO2e)'))


    # Combine the layers into a final chart
    final_chart = alt.layer(
        column_chart_cumsum,
        column_chart_individual,
        line_chart_net,
    ).properties(
        width=PLOT_WIDTH,
        height=PLOT_HEIGHT
    ).resolve_scale(
        color='independent'
    )


    return final_chart




class get_GHG_plots():


    def __init__(self, 
                 GHG_files:pd.DataFrame,
                 GHG_type:str,
                 GHG_value_name:str = 'GHG emissions (Mt CO2e)'):
        
        # Check if the GHG type is valid
        if GHG_type not in ['Agricultural Landuse','Agricultural Management', 
                            'Non-Agricultural Landuse', 'Transition Penalty']:
            
            raise ValueError('GHG_type can only be one of the following: \
                             ["Agricultural Landuse","Agricultural Management", \
                             "Non-Agricultural Landuse", "Transition Penalty"].')

        # Get GHG file paths under the given GHG type
        self.GHG_files = GHG_files.query(f'base_name == "{GHG_type}"').reset_index(drop=True)
        self.GHG_type = GHG_type
        self.GHG_value_name = GHG_value_name

        self.GHG_df = self.add_crop_lvstk_to_df()
        self.GHG_df_long = self.read_GHG_to_long()
        self.GHG_df_long = self.get_GHG_category()

        # Check if the total GHG is negative
        self.reverse_scale = True if self.GHG_df_long['Quantity (Mt CO2e)'].to_numpy(na_value=0).sum() < 0 else False
        

    ################################################################
    # Functions to get the GHG emissions of different categories   #
    ################################################################

    def add_crop_lvstk_to_df(self):

        # Read GHG emissions of ag lucc
        CSVs = []
        for _,row in self.GHG_files.iterrows():
            csv = pd.read_csv(row['path'],index_col=0,header=[0,1,2]).drop('SUM',axis=1)

            # Get the land use and land use category
            if self.GHG_type != 'Non-Agricultural Landuse':

                # Subset the crop landuse
                csv_crop = csv[[True if i in LU_CROPS else False for i in  csv.index]]
                csv_crop.index = pd.MultiIndex.from_product(([row['year']], csv_crop.index, ['Crop'],['Crop']))

                # Subset the livestock landuse
                csv_lvstk = csv[[True if i in LU_LVSTKS else False for i in  csv.index]]
                lvstk_old_index = csv_lvstk.index.str.split(' - ').tolist()

                # Add the year and land use category
                csv_lvstk.index = pd.MultiIndex.from_tuples(zip([row['year']] * len(lvstk_old_index), 
                                                                [i[0] for i in lvstk_old_index], 
                                                                [i[1] for i in lvstk_old_index],
                                                                ['Livestock']* len(lvstk_old_index)))

                # The csv.index has 4 levels -> [year, land use, land use category, land category]
                # where         year: int,                  [2010, 2011, ...,]
                #               land use: str,              [Apples, Beef, ...]
                #               land category: str          [modified land, natural land]
                #               land use category: str,     [Crop, Livestock]
                csv = pd.concat([csv_crop,csv_lvstk],axis=0)
            else:
                csv = csv[[True if i in NON_AG_LANDUSE else False for i in csv.index]]
                # Add the year and land use category, land category, so that the csv.index has 4 levels
                # which are matches the other GHG emissions data
                csv.index = pd.MultiIndex.from_product(([row['year']], 
                                                        csv.index, 
                                                        ['Non-Agricultural Landuse'],
                                                        ['Non-Agricultural Landuse']))
                
            # Append the csv to the list
            CSVs.append(csv)

        # Concatenate the csvs
        GHG_df = pd.concat(CSVs,axis=0)

        return GHG_df

        


    def read_GHG_to_long(self):
        
        # Define the index levels
        idx_level_name = ['Year','Land use','Land category','Land use category']

        # remove the first level in the multiindex columns
        GHG_df_long = self.GHG_df.copy()
        GHG_df_long = GHG_df_long.droplevel(0,axis=1)

        # Squeeze the multiindex columns into a single concatenated by "+"
        GHG_df_long.columns = ["+".join(i) for i in GHG_df_long.columns.tolist()]
        GHG_df_long = GHG_df_long.reset_index()
        GHG_df_long.columns = idx_level_name + GHG_df_long.columns.tolist()[4:]

        # Melt the table to long format
        GHG_df_long = GHG_df_long.melt(id_vars=idx_level_name,
                                            value_vars=GHG_df_long.columns.tolist()[3:],
                                            value_name='val_t')

        # Get the GHG emissions in Mt CO2e
        GHG_df_long['Quantity (Mt CO2e)'] = GHG_df_long['val_t'] / 1e6

        # Split the variable column into Irrigation and Sources
        GHG_df_long[['Irrigation','Sources']] = GHG_df_long['variable'].str.split('+',expand=True)

        # Replace the Sources with the GHG names
        GHG_df_long['Sources'] = GHG_df_long['Sources'].apply(lambda x: GHG_NAMES[x] if GHG_NAMES.get(x,None) else x)

        # Drop unnecessary columns and reorder the columns
        GHG_df_long.drop(['val_t','variable'],axis=1,inplace=True)
        GHG_df_long = GHG_df_long.reindex(columns= idx_level_name + ['Irrigation','Sources', 'Quantity (Mt CO2e)'])
        
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
    
        
    

################################################################
# Functions to plot the GHG emissions of different categories  #
################################################################


    def plot_GHG_crop_lvstk(self):

        # get the df
        GHG_crop_lvstk_total = self.GHG_df_long.groupby(['Year','Land use category','Land category']).sum()['Quantity (Mt CO2e)'].reset_index()
        GHG_crop_lvstk_total['Landuse_land_cat'] = GHG_crop_lvstk_total.apply(lambda x: (x['Land use category'] + ' - ' + x['Land category']) 
                                        if (x['Land use category'] != x['Land category']) else x['Land use category'], axis=1)

        # Create a base chart with the necessary transformations and encodings
        base_chart = alt.Chart(GHG_crop_lvstk_total).encode(
            x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
            tooltip=[alt.Tooltip('Landuse_land_cat:O', title='Landuse type'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")]
        )



        chart = base_chart.mark_bar().encode(
        color=alt.Color('Landuse_land_cat:N', 
                        legend=alt.Legend(
                                        title="Landuse type",
                                        orient='none',
                                        legendX=PLOT_WIDTH*0.23, legendY=-30,
                                        direction='horizontal',
                                        titleAnchor='middle')),
        y=alt.Y('Quantity (Mt CO2e):Q',
                title=f'{self.GHG_value_name}',
                scale=alt.Scale(reverse=self.reverse_scale,zero=False)),  
        )
             

        final_chart = alt.layer(
            chart,
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )

        return GHG_crop_lvstk_total, final_chart
    



    
    def plot_GHG_dry_irr(self):
        # make the long format table
        GHG_lm_total = self.GHG_df_long.groupby(['Year','Irrigation']).sum()['Quantity (Mt CO2e)'].reset_index()

        base_chart = alt.Chart(GHG_lm_total).encode(
        x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
        tooltip=[alt.Tooltip('Irrigation', title='Irrigation'),
                alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")]
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('Irrigation:N',legend=alt.Legend(
                                                            title="Irrigation",
                                                            orient='none',
                                                            legendX=PLOT_WIDTH*0.4, legendY=-30,
                                                            direction='horizontal',
                                                            titleAnchor='middle')),  
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name}',
                    scale=alt.Scale(reverse=self.reverse_scale))
        )



        final_chart = alt.layer(
            column_chart,
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )

        return GHG_lm_total, final_chart
    





    def plot_GHG_category(self):
        # make the long format table
        GHG_category_total = self.GHG_df_long.groupby(['Year','GHG Category']).sum()['Quantity (Mt CO2e)'].reset_index()

        base_chart = alt.Chart(GHG_category_total).encode(
                x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
                tooltip=[alt.Tooltip('GHG Category', title='GHG Category'),
                         alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")]
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('GHG Category:N',legend=alt.Legend(
                                                            title="GHG Category",
                                                            orient='none',
                                                            legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.5,
                                                            direction='vertical',
                                                            titleAnchor='middle')),  
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name}',
                    scale=alt.Scale(reverse=self.reverse_scale))
        )



        final_chart = alt.layer(
            column_chart,
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )

        return GHG_category_total, final_chart
    


    def plot_GHG_sources(self):

        # plot the GHG emissions of different Sources across years
        GHG_sources_total = self.GHG_df_long.groupby(['Year','Sources']).sum()['Quantity (Mt CO2e)'].reset_index()

        base_chart = alt.Chart(GHG_sources_total).encode(
                x=alt.X('Year:O',axis=alt.Axis(title="Year", labelAngle=-90)),  # Treat year as an ordinal data type
                tooltip=[alt.Tooltip('Sources', title='GHG Sources'),
                        alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")]
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        )


        column_chart = base_chart.mark_bar().encode(
            color=alt.Color('Sources:N',legend=alt.Legend(
                                                        title="GHG Sources",
                                                        orient='none',
                                                        legendX=PLOT_WIDTH + 10, legendY=PLOT_HEIGHT*0.25,
                                                        direction='vertical',
                                                        titleAnchor='middle')),  
            y=alt.Y('Quantity (Mt CO2e):Q',
                    title=f'{self.GHG_value_name}',
                    scale=alt.Scale(reverse=self.reverse_scale))
        )



        final_chart = alt.layer(
            column_chart,
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT
        ).configure_legend(
            labelLimit = 0
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
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")],
            x="Quantity (Mt CO2e):Q",
            y="Land use:O",
            color=alt.Color("Irrigation:N",legend=alt.Legend(
                                                        title="Irrigation",
                                                        orient='none',
                                                        legendX=PLOT_WIDTH*0.4, legendY=-40,
                                                        direction='horizontal',
                                                        titleAnchor='middle'))
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT)

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
            alt.Y('Sources:O',axis=alt.Axis(labelLimit=400)),
            alt.Color('Irrigation:O',legend=alt.Legend(
                                                        title="Irrigation",
                                                        orient='none',
                                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.3,
                                                        direction='vertical',
                                                        titleAnchor='start')),
            alt.Size('Quantity (Mt CO2e):Q',legend=alt.Legend(
                                                        title='Qantity (Mt CO2e)',
                                                        orient='none',
                                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.5,
                                                        direction='vertical',
                                                        titleAnchor='start')),
            tooltip=[alt.Tooltip('Land use:O', title='Landuse'),
                     alt.Tooltip('Sources:O', title=f'GHG source'),
                     alt.Tooltip('Quantity (Mt CO2e):Q', title=f'{self.GHG_value_name}',format=",.2f")],
        ).properties(
            width=PLOT_WIDTH,
            height=PLOT_HEIGHT)

        return df_this_yr,plot




