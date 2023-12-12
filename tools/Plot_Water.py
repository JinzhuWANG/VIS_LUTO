import os
import altair as alt
import pandas as pd


# set up working directory
if __name__ == '__main__': 
    os.chdir('..')

from PARAMETERS import  LU_CROPS, LU_LVSTKS, PLOT_HEIGHT, PLOT_WIDTH

def get_water_df(water_dfs):
    dfs = []
    for _,row in water_dfs.iterrows():
        df = pd.read_csv(row['path'], index_col=0).reset_index(drop=True)
        # insert year column
        df.insert(0, 'year', row['year'])
        df['TOT_WATER_REQ_ML'] = df['TOT_WATER_REQ_ML'].str.replace(',','').astype(float)
        df['WATER_USE_LIMIT_ML'] = df['WATER_USE_LIMIT_ML'].str.replace(',','').astype(float)
        df['ABS_DIFF_ML'] = df['ABS_DIFF_ML'].str.replace(',','').astype(float)
        dfs.append(df)
        
    return pd.concat(dfs, axis=0).reset_index(drop=True)


# plot the PROPORTION_% change overtime using line plot
def plot_water_percent(water_df):

    plot = alt.Chart(water_df).mark_line(size=5).encode(
        x='year:N',
        y=alt.Y('PROPORTION_%:Q', title='Proportion to limit (%)'),
        color=alt.Color('REGION_NAME:N',
                        legend=alt.Legend(
                                        title='Region',
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.4,
                                        direction='vertical',
                                        titleAnchor='start')),
    )

    plot_pts = alt.Chart(water_df).mark_point(opacity=0,size=300).encode(
        x='year:O',
        y=alt.Y('PROPORTION_%:Q', title='Proportion (%)'),
        color=alt.Color('REGION_NAME:N',legend=None),
        tooltip=[alt.Tooltip('REGION_NAME:N', title='Region'),
                                    alt.Tooltip('PROPORTION_%:Q', title='Proportion (%)'),
                                    alt.Tooltip('year:O', title='Year')]
    )

    finale_plot = (plot_pts + plot).resolve_scale(
        color='independent').properties(
                width=PLOT_WIDTH,
                height=PLOT_HEIGHT)
    
    return finale_plot



def plot_water_use_volum(water_df):
    plot = alt.Chart(water_df).mark_line(size=5).encode(
        x='year:N',
        y=alt.Y('TOT_WATER_REQ_ML:Q', title='Water Requirement (ML)'),
        color=alt.Color('REGION_NAME:N',
                        legend=alt.Legend(
                                        title='Region',
                                        orient='none',
                                        legendX=PLOT_WIDTH+10, legendY=PLOT_HEIGHT*0.4,
                                        direction='vertical',
                                        titleAnchor='start')),
    )

    plot_pts = alt.Chart(water_df).mark_point(opacity=0,size=300).encode(
        x='year:O',
        y=alt.Y('TOT_WATER_REQ_ML:Q', title='Water Requirement (ML)'),
        color=alt.Color('REGION_NAME:N',legend=None),
        tooltip=[alt.Tooltip('REGION_NAME:N', title='Region'),
                                    alt.Tooltip('TOT_WATER_REQ_ML:Q', title='Water Requirement (ML)'),
                                    alt.Tooltip('year:O', title='Year')]
    )

    finale_plot = (plot_pts + plot).resolve_scale(
        color='independent').properties(
                width=PLOT_WIDTH,
                height=PLOT_HEIGHT)
        
    return finale_plot