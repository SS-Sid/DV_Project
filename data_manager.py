import os
import pandas as pd
import pycountry

### declare constant information
metric_label_map = {
    # energy consumption by source
    'consumption'                   : 'Primary Energy Consumption (TWh)',
    'cons_change_twh'               : 'Annual Consumption Change (TWh)',
    'cons_change_pct'               : 'Annual Consumption Change (%)',
    'share_energy'                  : 'Share of Energy Primary Energy Consumption (%)',
    'cons_per_capita'               : 'Primary Energy Consumption per Capita (kWh)',
    'per_gdp'                       : 'Energy Consumption Per unit GDP (KWh)',


    # source production
    'production'                    : 'Production (TWh)',
    'prod_change_twh'               : 'Annual Production Change (TWh)',
    'prod_change_pct'               : 'Annual Production Change (%)',
    'prod_per_capita'               : 'Production per Capita (kWh)',


    # electricity generation by source
    'electricity'                   : 'Electricity Generation (TWh)',
    'share_elec'                    : 'Share of Electricity Generation (%)', 
    'elec_per_capita'               : 'Electricity Generation per Capita (kWh)',
    
    'net_imports'                   : 'Net Imports (TWh)',
    'net_imports_share_demand'      : 'Net Imports as Share of Demand (%)',
    'demand'                        : 'Demand (TWh)',
    
    'carbon_intensity'              : 'Carbon Intensity (gCO2/kWh)',
    'greenhouse_gas_emissions'      : 'Greenhouse Gas Emissions in production (MtCO2e)',
    
    'share_elec_exc_biofuel'        : 'Share of Electricity Excluding Biofuel (%)',
    'elec_per_capita_exc_biofuel'   : 'Electricity Generation per Capita Excluding Biofuel (kWh)',
    'exc_biofuel_electricity'       : 'Electricity Generation Excluding Biofuel (TWh)',
}

source_label_map = {
    'biofuel'           : 'Biofuel',
    'coal'              : 'Coal',
    'electricity'       : 'Electricity',
    'energy'            : 'Total',
    'fossil'            : 'Fossil',
    'gas'               : 'Gas',
    'hydro'             : 'Hydro',
    'low_carbon'        : 'Low Carbon',
    'nuclear'           : 'Nuclear',
    'oil'               : 'Oil',
    'other_renewables'  : 'Other Renewables',
    'renewables'        : 'Renewables',
    'solar'             : 'Solar',
    'wind'              : 'Wind'
}


class DataManager:
    def __init__(self, df_name):
        file_path = os.path.abspath(__file__)
        self.project_dir = os.path.dirname(file_path)
        
        self.df = self._prepare_df(df_name)

        self.all_cols = self.df.columns.tolist()
        self._prepare_source_metric_map()
        self._prepare_mapped_unmapped_cols()
        self._prepare_country_region_map()


    def _prepare_df(self, df_name):
        df = pd.read_csv(os.path.join(self.project_dir, 'data', df_name))

        print(f'Loaded {df_name}')
        return df    


    def _prepare_source_metric_map(self):
        ### get source-metric mappings
        self.source_metric_map = {}
        for source in source_label_map.keys():
            self.source_metric_map[source] = []

            for col in self.all_cols:
                col_metric = (source + '_').join(col.split(source + '_')[1:])
                col_source = col.split('_' + col_metric)[0]

                if col_source == source:
                    self.source_metric_map[source].append(col_metric)
        
        print(f'Metrics mapped to sources')


    def _prepare_mapped_unmapped_cols(self):
        ### get unmapped columns
        self.source_metric_list = []
        for source in self.source_metric_map:
            for metric in self.source_metric_map[source]:
                self.source_metric_list.append(source + '_' + metric)

        self.remaining_cols = [col for col in self.all_cols if col not in self.source_metric_list]

        print(f'Extracted Unmapped columns and Mapped columns')


    def _prepare_country_region_map(self):
        ### separate countries and non-countries
        # filter out the regions that are not countries
        all_regions = self.df['country'].unique()

        self.countries = []
        self.non_countries = []
        for region in all_regions:
            try:
                pycountry.countries.lookup(region)
                self.countries.append(region)
            except:
                self.non_countries.append(region)
        
        print(f'Extracted countries and non-countries')