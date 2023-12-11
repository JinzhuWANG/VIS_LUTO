import os
import pandas as pd
import altair as alt

# set up working directory
if __name__ == '__main__':
    os.chdir('..')

from PARAMETERS import LU_CROPS,LU_LVSTKS,LU_UNALLOW,NON_AG_LANDUSE  

def merge_LVSTK_UAALLOW(df):
    """
    Merges the dataframes for different land use types (crop, non-agricultural, low value stock, and unallowed) 
    into a single dataframe and returns it.

    Parameters:
    df (pandas.DataFrame): The input dataframe containing land use data.

    Returns:
    pandas.DataFrame: The merged dataframe containing land use data for different types of land use.
    """
    df_crop = df[[True if i in LU_CROPS else False for i in  df['Land use']]]

    df_ep = df[[True if i in NON_AG_LANDUSE else False for i in  df['Land use']]]

    df_unallow = df[[True if i in LU_UNALLOW else False for i in  df['Land use']]]
    # df_unallow.index = pd.MultiIndex.from_tuples(tuple(df_unallow['Land use'].str.split(' - ')))
    # df_unallow = df_unallow.groupby(level=0).sum(numeric_only=True).reset_index(names='Land use')

    df_lvstk = df[[True if i in LU_LVSTKS else False for i in  df['Land use']]]
    df_lvstk.index = pd.MultiIndex.from_tuples(tuple(df_lvstk['Land use'].str.split(' - ')))
    df_lvstk = df_lvstk.groupby(level=0).sum(numeric_only=True).reset_index(names='Land use')

    return pd.concat([df_crop,df_ep,df_lvstk,df_unallow]).reset_index(drop=True)


def process_row(df, idx, year, column_names, processing_function=None):
    """
    Process a single row of data from a DataFrame.

    Args:
        df (pandas.DataFrame): The DataFrame containing the data to process.
        idx (int): The index of the row to process.
        year (int): The year associated with the row.
        column_names (list): A list of column names to use for the processed data.
        processing_function (function, optional): A function to apply to the processed data.

    Returns:
        pandas.DataFrame: The processed data row.
    """
    # Function to process a single row
    if idx == 0:
        # Process the first year
        data_row = df.iloc[:, -1].reset_index().query('(index != "Total") & (index != "All")')
        data_row.columns = column_names
        if processing_function:
            data_row = processing_function(data_row)
        data_row.insert(0, 'Year', year - 1)
    else:
        # Process the last row for the year
        data_row = df.iloc[-1, :].reset_index().query('(index != "Total") & (index != "All")')
        data_row.columns = column_names
        if processing_function:
            data_row = processing_function(data_row)
        data_row.insert(0, 'Year', year)

    return data_row

def get_AREA_lu(df):
    """
    Returns a pandas DataFrame containing processed data on land use and area (in km2) for each year in the input DataFrame.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing at least the columns 'year' and 'path', where 'year' is the year of the data and 'path' is the file path to the data file.

    Returns:
    pandas.DataFrame: A DataFrame containing processed data on land use and area (in km2) for each year in the input DataFrame.
    """
    area_df = []
    for idx, (_, row) in enumerate(df.iterrows()):
        year = row['year']
        file_path = row['path']
        df = pd.read_csv(file_path, index_col=0)

        # Process row and append
        processed_row = process_row(df, idx, year, ['Land use', 'Area (km2)'], merge_LVSTK_UAALLOW)
        area_df.append(processed_row)

    return pd.concat(area_df).reset_index(drop=True)

def get_AREA_lm(df):
    """
    Processes a DataFrame of irrigation data and returns a concatenated DataFrame of processed data.

    Args:
        df (pandas.DataFrame): A DataFrame containing irrigation data.

    Returns:
        pandas.DataFrame: A concatenated DataFrame of processed data.
    """
    area_df = []
    for idx, (_, row) in enumerate(df.iterrows()):
        year = row['year']
        file_path = row['path']
        df = pd.read_csv(file_path, index_col=0)

        # Define a processing function for irrigation data
        def process_irrigation(row):
            return row.replace({'0': 'Dry', '1': 'Irrigated'})

        # Process row and append
        processed_row = process_row(df, idx, year, ['Irrigation', 'Area (km2)'], process_irrigation)
        area_df.append(processed_row)

    return pd.concat(area_df).reset_index(drop=True)

    
def get_AREA_am(df):
    """
    Given a pandas DataFrame `df` containing information about land use and area in different years,
    this function returns a new DataFrame containing the area of each land use category in each year.
    The input DataFrame `df` should have the following columns:
    - 'path': the file path of the data file
    - 'year': the year of the data
    - 'Area prior [ km2 ]': the area of each land use category before any changes
    - 'Area after [ km2 ]': the area of each land use category after any changes
    - 'Land use': the name of each land use category
    """
    
    # read all the switches
    switches = []
    for idx,(_,row) in enumerate(df.iterrows()):

        path = row['path']
        year = row['year']
        file_path = row['path']
        df = pd.read_csv(file_path,index_col=0)

        # check if this is the first row
        if idx == 0:
            first_year = df[['Area prior [ km2 ]']].reset_index(names='Land use').query('`Land use` != "Total"')
            first_year.columns = ['Land use','Area (km2)']
            first_year.insert(0,'Year',year - 1)
            switches.append(first_year)
        
        # get the last row, which is the area in the year
        last_row = df[['Area after [ km2 ]']].reset_index(names='Land use').query('`Land use` != "Total"')
        last_row.columns = ['Land use','Area (km2)']
        last_row.insert(0,'Year',year)
        switches.append(last_row)

    return pd.concat(switches).reset_index(drop=True)




def plot_area_lu(df):
    """
    Plots a bar chart of land use area over time.

    Parameters:
    df (pandas.DataFrame): A pandas DataFrame containing columns 'Year', 'Area (km2)', and 'Land use'.

    Returns:
    altair.vegalite.v4.api.Chart: An Altair bar chart showing land use area over time.
    """
    plot = alt.Chart(df).mark_bar().encode(
        x = alt.X('Year:O',title='Year'),
        y = alt.Y('Area (km2):Q',title='Area (km2)',scale=alt.Scale(domain=[0, 4700000])),
        color = alt.Color('Land use:N',
                        title='Land use',
                        scale=alt.Scale(scheme='category20'),
                        legend=alt.Legend(
                                            title="Land use",
                                            orient='none',
                                            legendX=720, legendY=90,
                                            direction='vertical',
                                            titleAnchor='start')),
        tooltip = ['Year','Land use','Area (km2)']
    ).properties(
        width=700,
        height=500
    )

    return plot



def plot_area_lm(df):
    """
    Plots the area change over time.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the data to be plotted.

    Returns:
    --------
    altair.vegalite.v4.api.Chart
        The Altair chart object representing the plot.
    """
    # plot the area change over time
    plot = alt.Chart(df).mark_bar().encode(
        x = alt.X('Year:O',title='Year'),
        y = alt.Y('Area (km2):Q',title='Area (km2)',scale=alt.Scale(domain=[0, 4700000])),
        color = alt.Color('Irrigation:N',
                          title='Irrigation',
                          legend=alt.Legend(
                                            title="Irrigation",
                                            orient='none',
                                            legendX=280, legendY=-40,
                                            direction='horizontal',
                                            titleAnchor='middle')),
        tooltip = ['Year','Irrigation','Area (km2)']
    ).properties(
        width=700,
        height=500
    )

    return plot



def plot_area_am_total(df):
    """
    Plots the area change over time for different agricultural management types.

    Parameters:
    df (pandas.DataFrame): The input DataFrame containing the data to be plotted.

    Returns:
    alt.Chart: The Altair chart object representing the plot.
    """
    
    # plot the area change over time
    plot = alt.Chart(df).mark_bar().encode(
        x = alt.X('Year:O',title='Year'),
        y = alt.Y('Area (km2):Q',title='Area (km2)'),
        color = alt.Color('Agricultural management:N',title='Agricultural management',legend=alt.Legend(
                                                                        title="Agricultural management",
                                                                        orient='none',
                                                                        legendX=150, legendY=-40,
                                                                        direction='horizontal',
                                                                        titleAnchor='middle')),
        tooltip = ['Year','Agricultural management','Area (km2)']
    ).properties(
        width=700,
        height=500
    )

    return plot


def plot_area_am_lu(df):
    """
    Plots the total area of land use between years.

    Parameters:
    -----------
    df : pandas.DataFrame
        A pandas DataFrame containing the data to be plotted. It should have columns 'Year', 'Area (km2)', and 'Land use'.

    Returns:
    --------
    altair.vegalite.v4.api.Chart
        An Altair chart object representing the plot.
    """
    # plot the total area of land use between years
    plot = alt.Chart(df).mark_bar().encode(
        x = alt.X('Year:O',title='Year'),
        y = alt.Y('Area (km2):Q',title='Area (km2)'),
        color = alt.Color('Land use:N',title='Land use',
                          scale=alt.Scale(scheme='turbo'),
                          legend=alt.Legend(
                                            title="Agricultural management",
                                            orient='none',
                                            legendX=710, legendY=90,
                                            direction='vertical',
                                            titleAnchor='start')),
        tooltip = ['Year','Land use','Area (km2)']
    ).properties(
        width=700,
        height=500
    )

    return plot
