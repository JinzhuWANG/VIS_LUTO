import os
import concurrent.futures

import numpy as np
import pandas as pd
import rasterio

from pathlib import Path
from tqdm import tqdm

# set up working directory
if __name__ == '__main__':
    os.chdir('..')



# function to write colormap to tif
def hex_color_to_numeric(hex_color):
    # Remove the '#' character (if present)
    hex_color = hex_color.lstrip('#')

    # Get the red, green, blue, and (optional) alpha components
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    if len(hex_color) == 8:  # If the color includes an alpha channel
        alpha = int(hex_color[6:8], 16) 
        return red, green, blue, alpha
    else:
        return red, green, blue, 255


# function to convert hex color to numeric
def color_hex2num(csv_path:str=f'tools/color_map.csv'):
    lu_colors = pd.read_csv(csv_path)
    lu_colors['color_num'] = lu_colors['color_HEX'].apply(lambda x: hex_color_to_numeric(x))
    lu_colors_dict = lu_colors.set_index('lu_code')['color_num'].to_dict()  
    return lu_colors_dict




# function to parallelize a process
class ParallelConvertDecorator:
    def __init__(self, max_workers=None, input_files=None):
        self.max_workers = max_workers
        self.input_files = input_files

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if not self.input_files:
                raise ValueError("You must provide a list of input files.")

            # Create a ProcessPoolExecutor to run the function in parallel
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                # Submit each file to the executor
                for input_file in self.input_files:
                    # set binary_color to True if the tif is land use tif
                    kwargs['binary_color'] = False if 'lu' in input_file else True
                    kwargs['lu_tif'] = input_file

                    future = executor.submit(func, *args, **kwargs)
                    futures.append(future)
                
                # Get the results as they are completed
                for future in tqdm(concurrent.futures.as_completed(futures),
                                   total=len(futures)):
                    pass

            return None

        return wrapper


# function to convert a 1-band arrary to 4-band (RGBA) array with colormap
def convert_1band_to_4band(lu_tif:str, 
                           color_dict:dict = color_hex2num(),
                           band:int = 1,
                           binary_color:bool = False):
    """Convert a 1-band array to 4-band (RGBA) array with colormap"""

    # check if the color_dict needs to be binarizd
    if binary_color:
        color_dict = {0:(31, 31, 31, 160), 1:(255, 255, 255,160)}

    # get the file name without extension
    lu_base = os.path.basename(lu_tif).split('.')[0]
    lu_parent = Path(lu_tif).parent.absolute()

    # get the tif array and meta
    with rasterio.open(lu_tif,'r+') as src:

        # get the array and meta
        lu_arr = src.read(band)
        # get the meta
        lu_meta = src.meta
        # set the color of nodata value to transparent
        color_dict[src.meta['nodata']] = (0, 0, 0, 0)


    # update meta
    lu_meta.update(count=4,dtype='uint8', compress='lzw', nodata=0)
    # convert the 1-band array to 4-band (RGBA) array
    arr_4band = np.zeros((lu_meta['height'], lu_meta['width'], 4), dtype='uint8') 
    
    for k, v in color_dict.items():
        arr_4band[lu_arr == k] = v

    # convert HWC to CHW
    arr_4band = arr_4band.transpose(2, 0, 1)

    # write 4band array to tif
    with rasterio.open(f'{lu_parent}/{lu_base}_color4band.tiff', 
                       'w', 
                       **lu_meta) as dst:
        dst.write(arr_4band)


    return f'{lu_parent}/{lu_base}_colored.tiff'



# function to generate SLD from csv
def create_sld(pixel_values:list = None, 
               color_values:list = None,
               save_path:str = 'tools/colormap.sld'):
    sld_template = '''<?xml version="1.0" encoding="UTF-8"?>
    <sld:StyledLayerDescriptor xmlns:sld="http://www.opengis.net/sld" version="1.0.0">
        <sld:NamedLayer>
            <sld:Name>Generated Layer</sld:Name>
            <sld:UserStyle>
                <sld:FeatureTypeStyle>
                    <sld:Rule>
                        <sld:RasterSymbolizer>
                            <sld:ColorMap>'''

    for color, value in zip(color_values, pixel_values):
        sld_template += f'<sld:ColorMapEntry color="{color}" quantity="{value}" label="{value}"/>\n'

    sld_template += '''                            </sld:ColorMap>
                        </sld:RasterSymbolizer>
                    </sld:Rule>
                </sld:FeatureTypeStyle>
            </sld:UserStyle>
        </sld:NamedLayer>
    </sld:StyledLayerDescriptor>'''

    # Save the SLD content to a file
    with open(save_path, 'w') as file:
        file.write(sld_template)


def create_qml_from_csv(pixel_values:list = None, 
                        color_values:list = None,
                        lable_values:list = None,
                        save_path:str = 'tools/colormap.qml'):
    
    # Start of the QML template
    qml_template_start = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
    <qgis hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories" minScale="1e+08" version="3.26.3-Buenos Aires" maxScale="0">
    <!-- (Other parts of the QML file) -->
    <rasterrenderer type="paletted" alphaBand="-1" opacity="1" band="1" nodataColor="">
        <rasterTransparency/>
        <minMaxOrigin>
        <!-- (minMaxOrigin content) -->
        </minMaxOrigin>
        <colorPalette>'''

    # Initialize palette_entries
    palette_entries = ''

    # Loop through the DataFrame and create palette entries
    for value, rgba, lable in zip(pixel_values, color_values,lable_values):
        color = f'#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}'  # Convert RGB to HEX
        alpha = rgba[3]
        palette_entries += f'\n <paletteEntry label="{lable}" alpha="{alpha}" color="{color}" value="{value}"/>'

        # End of the QML template
        qml_template_end = '''    </colorPalette>
        <colorramp type="randomcolors" name="[source]">
        <!-- (Color ramp content) -->
        </colorramp>
    </rasterrenderer>
    <!-- (Rest of the QML file) -->
    </qgis>'''

    style_xml = qml_template_start + palette_entries + qml_template_end
    # Save the SLD content to a file
    with open(save_path, 'w') as file:
        file.write(style_xml)

