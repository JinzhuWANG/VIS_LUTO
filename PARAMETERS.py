


# Get the root directory of the data
DATA_ROOT = "/home/jinzhu/docker_data/LUTO_DATA/2023_12_12__09_28_38_hard_mincost_RF5_P1e5_2010-2050_timeseries_-265Mt/"

# Define the plot settings
PLOT_WIDTH = 500
PLOT_HEIGHT = 300




# Define crop-lvstk land uses
LU_CROPS = ['Apples','Citrus','Cotton','Grapes','Hay','Nuts','Other non-cereal crops',
            'Pears','Plantation fruit','Rice','Stone fruit','Sugar','Summer cereals',
            'Summer legumes','Summer oilseeds','Tropical stone fruit','Vegetables',
            'Winter cereals','Winter legumes','Winter oilseeds']

LU_LVSTKS = ['Beef - modified land','Beef - natural land','Dairy - modified land',
             'Dairy - natural land','Sheep - modified land','Sheep - natural land']

LU_UNALLOW = ['Unallocated - modified land','Unallocated - natural land']



# Define the file name patterns for each category
GHG_FNAME2TYPE = {'GHG_emissions_separate_agricultural_landuse': 'Agricultural Landuse',
                  'GHG_emissions_separate_agricultural_management': 'Agricultural Management',
                  'GHG_emissions_separate_no_ag_reduction': 'Non-Agricultural Landuse',
                  'GHG_emissions_separate_transition_penalty': 'Transition Penalty'}

# Define all land uses for each category
AG_LANDUSE = ['Apples', 'Beef - modified land', 'Beef - natural land', 'Citrus', 'Cotton', 'Dairy - modified land', 
              'Dairy - natural land', 'Grapes', 'Hay', 'Nuts', 'Other non-cereal crops', 'Pears', 'Plantation fruit', 
              'Rice', 'Sheep - modified land', 'Sheep - natural land', 'Stone fruit', 'Sugar', 'Summer cereals', 
              'Summer legumes', 'Summer oilseeds', 'Tropical stone fruit', 'Unallocated - modified land', 
              'Unallocated - natural land', 'Vegetables', 'Winter cereals', 'Winter legumes', 'Winter oilseeds']

NON_AG_LANDUSE = ['Environmental Plantings']


# Define the GHG categories

GHG_NAMES = {
    'TCO2E_CHEM_APPL': 'Chemical Application',
    'TCO2E_CROP_MGT': 'Crop Management',
    'TCO2E_CULTIV': 'Cultivation',
    'TCO2E_FERT_PROD': 'Fertiliser production',
    'TCO2E_HARVEST': 'Harvesting',
    'TCO2E_IRRIG': 'Irrigation',
    'TCO2E_PEST_PROD': 'Pesticide production',
    'TCO2E_SOWING': 'Sowing',
    'TCO2E_ELEC': 'Electricity Use livestock',
    'TCO2E_FODDER': 'Fodder production',
    'TCO2E_FUEL': 'Fuel Use livestock',
    'TCO2E_IND_LEACH_RUNOFF': 'Agricultural soils: Indirect leaching and runoff',
    'TCO2E_MANURE_MGT': 'Livestock Manure Management (biogenic)',
    'TCO2E_SEED': 'Pasture Seed production',
    'TCO2E_SOIL': 'Agricultural soils: Direct Soil Emissions (biogenic)',
    'TCO2E_DUNG_URINE': 'Agricultural soils: Animal production, dung and urine',
    'TCO2E_ENTERIC': 'Livestock Enteric Fermentation (biogenic)',

    'TCO2E_Asparagopsis taxiformis': 'Asparagopsis taxiformis', 
    'TCO2E_Precision Agriculture': 'Precision Agriculture',
    'TCO2E_Ecological Grazing': 'Ecological Grazing',
}

GHG_CATEGORY = {'Agricultural soils: Animal production, dung and urine': {"CH4":0.5,"CO2":0.5},
                'Livestock Enteric Fermentation (biogenic)':{'CH4':1},
                'Agricultural soils: Direct Soil Emissions (biogenic)':{"N2O":1},
                
                'Asparagopsis taxiformis':{'Asparagopsis taxiformis':1},
                'Precision Agriculture':{'Precision Agriculture':1},
                'Ecological Grazing':{'Ecological Grazing':1}}


# Text to look for in adding tags
NOTEBOOK_META_DICT = {
    "# HIDDEN": "remove-cell",  # Remove the whole cell
    "# NO CODE": "remove-input",  # Remove only the input
    "# HIDE CODE": "hide-input"  # Hide the input w/ a button to show
}


# The category and base corespondences for proper names
CAT2NAME = {'lumap': 'Agricultural Land-use all category',
            'lumap_separate_Agricultural Land-use': 'Agricultural Land-use single category',
            'ammap': 'Agriculture Management',
            'lumap_separate_Non-Agricultural Land-use': 'Non-Agricultural Land-use ',
            'lmmap': 'Dry and Irrigated Land-use'}

BASE2NAME = {'Agricultural Land-use_00_Apples_color4band': 'Apples',
            'Agricultural Land-use_01_Beef - modified land_color4band': 'Beef - modified land',
            'Agricultural Land-use_02_Beef - natural land_color4band': 'Beef - natural land',
            'Agricultural Land-use_03_Citrus_color4band': 'Citrus',
            'Agricultural Land-use_04_Cotton_color4band': 'Cotton',
            'Agricultural Land-use_05_Dairy - modified land_color4band': 'Dairy - modified land',
            'Agricultural Land-use_06_Dairy - natural land_color4band': 'Dairy - natural land',
            'Agricultural Land-use_07_Grapes_color4band': 'Grapes',
            'Agricultural Land-use_08_Hay_color4band': 'Hay',
            'Agricultural Land-use_09_Nuts_color4band': 'Nuts',
            'Agricultural Land-use_10_Other non-cereal crops_color4band': 'Other non-cereal crops',
            'Agricultural Land-use_11_Pears_color4band': 'Pears',
            'Agricultural Land-use_12_Plantation fruit_color4band': 'Plantation fruit',
            'Agricultural Land-use_13_Rice_color4band': 'Rice',
            'Agricultural Land-use_14_Sheep - modified land_color4band': 'Sheep - modified land',
            'Agricultural Land-use_15_Sheep - natural land_color4band': 'Sheep - natural land',
            'Agricultural Land-use_16_Stone fruit_color4band': 'Stone fruit',
            'Agricultural Land-use_17_Sugar_color4band': 'Sugar',
            'Agricultural Land-use_18_Summer cereals_color4band': 'Summer cereals',
            'Agricultural Land-use_19_Summer legumes_color4band': 'Summer legumes',
            'Agricultural Land-use_20_Summer oilseeds_color4band': 'Summer oilseeds',
            'Agricultural Land-use_21_Tropical stone fruit_color4band': 'Tropical stone fruit',
            'Agricultural Land-use_22_Unallocated - modified land_color4band': 'Unallocated - modified land',
            'Agricultural Land-use_23_Unallocated - natural land_color4band': 'Unallocated - natural land',
            'Agricultural Land-use_24_Vegetables_color4band': 'Vegetables',
            'Agricultural Land-use_25_Winter cereals_color4band': 'Winter cereals',
            'Agricultural Land-use_26_Winter legumes_color4band': 'Winter legumes',
            'Agricultural Land-use_27_Winter oilseeds_color4band': 'Winter oilseeds',
            'Non-Agricultural Land-use_00_Environmental Plantings_color4band': 'Environmental Plantings',
            'lumap_color4band': 'Land-use Map',
            'lmmap_color4band': 'Dry Irriagted Land-use Map'}