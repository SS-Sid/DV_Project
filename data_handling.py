### toolkit
import pandas as pd
import os

# data ingestion
data_path = 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv'
df = pd.read_csv(data_path)

# data cleaning
### rename columns in generalized notations
## total energy
df.rename(columns={'primary_energy_consumption': 'energy_consumption'}, inplace=True)
df.rename(columns={'energy_per_capita': 'energy_cons_per_capita'}, inplace=True)

## fossil fuels
df.rename(columns={'fossil_fuel_consumption': 'fossil_consumption'}, inplace=True)
df.rename(columns={'fossil_energy_per_capita': 'fossil_cons_per_capita'}, inplace=True)

## gas
df.rename(columns={'gas_energy_per_capita': 'gas_cons_per_capita'}, inplace=True)

## hydro
df.rename(columns={'hydro_energy_per_capita': 'hydro_cons_per_capita'}, inplace=True)

## low_carbon
df.rename(columns={'low_carbon_energy_per_capita': 'low_carbon_cons_per_capita'}, inplace=True)

## nuclear
df.rename(columns={'nuclear_energy_per_capita': 'nuclear_cons_per_capita'}, inplace=True)

## oil
df.rename(columns={'oil_energy_per_capita': 'oil_cons_per_capita'}, inplace=True)

## other renewables
df.rename(columns={'other_renewable_consumption': 'other_renewables_consumption'}, inplace=True)
df.rename(columns={'other_renewable_electricity': 'other_renewables_electricity'}, inplace=True)
df.rename(columns={'other_renewable_exc_biofuel_electricity': 'other_renewables_exc_biofuel_electricity'}, inplace=True)
df.rename(columns={'other_renewables_energy_per_capita': 'other_renewables_cons_per_capita'}, inplace=True)

## renewables
df.rename(columns={'renewables_energy_per_capita': 'renewables_cons_per_capita'}, inplace=True)

## solar
df.rename(columns={'solar_energy_per_capita': 'solar_cons_per_capita'}, inplace=True)

## wind
df.rename(columns={'wind_energy_per_capita': 'wind_cons_per_capita'}, inplace=True)



## electricity
df.rename(columns={'carbon_intensity_elec': 'electricity_carbon_intensity'}, inplace=True)
df.rename(columns={'greenhouse_gas_emissions': 'electricity_greenhouse_gas_emissions'}, inplace=True)
df.rename(columns={'per_capita_electricity': 'electricity_prod_per_capita'}, inplace=True)
df.rename(columns={'net_elec_imports': 'electricity_net_imports'}, inplace=True)
df.rename(columns={'net_elec_imports_share_demand': 'electricity_net_imports_share_demand'}, inplace=True)
df.rename(columns={'electricity_generation': 'electricity_production'}, inplace=True)


### save data
file_path = os.path.abspath(__file__)
file_dir = os.path.dirname(file_path)
data_dir = os.path.join(file_dir, 'data')
# check if data directory exists and create it if it doesn't
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# save subset of data 
# between 1960 and 2020
df = df[(df['year'] >= 1960) & (df['year'] <= 2020)]

# save data
df.to_csv(os.path.join(data_dir, 'energy_data_clean.csv'), index=False)
print('Data saved to: ', os.path.join(data_dir, 'energy_data_clean.csv'))