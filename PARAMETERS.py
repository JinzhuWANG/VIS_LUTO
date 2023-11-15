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
GHG_CATEGORY = {'TCO2E_DUNG_URINE': {"CH4":0.5,
                                     "CO2":0.5},
                'TCO2E_ENTERIC':{'CH4':1},
                'TCO2E_SOIL':{"N2O":1}}
