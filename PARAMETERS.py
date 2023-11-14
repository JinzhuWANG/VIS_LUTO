# Define crop-lvstk land uses
LU_crops = ['Apples','Citrus','Cotton','Grapes','Hay','Nuts','Other non-cereal crops',
            'Pears','Plantation fruit','Rice','Stone fruit','Sugar','Summer cereals',
            'Summer legumes','Summer oilseeds','Tropical stone fruit','Vegetables',
            'Winter cereals','Winter legumes','Winter oilseeds']

LU_lvstk = ['Beef - modified land','Beef - natural land','Dairy - modified land',
             'Dairy - natural land','Sheep - modified land','Sheep - natural land']


# Define the file name patterns for each category
GHG_fname2type = {'GHG_emissions_separate_agricultural_landuse': 'Agricultural Landuse',
                  'GHG_emissions_separate_agricultural_management': 'Agricultural Management',
                  'GHG_emissions_separate_no_ag_reduction': 'Non-Agricultural Landuse',
                  'GHG_emissions_separate_transition_penalty': 'Transition Penalty'}