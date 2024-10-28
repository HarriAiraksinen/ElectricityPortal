import datetime
import pandas as pd
import streamlit as st

Price = "https://raw.githubusercontent.com/HarriAiraksinen/ElectricityPortal/refs/heads/main/sahkon-hinta-010121-240924.csv"
Usage = "https://raw.githubusercontent.com/HarriAiraksinen/ElectricityPortal/refs/heads/main/Electricity_20-09-2024.csv"
# Electricity_Price = pd.read_csv('sahkon-hinta-010121-240924.csv')
Electricity_Price = pd.read_csv(Price)
# Electricity_Usage = pd.read_csv('Electricity_20-09-2024.csv',delimiter=';')
Electricity_Usage = pd.read_csv(Usage,delimiter=';')

# Change time format of both files to Pandas datetime
Electricity_Price['Time'] = pd.to_datetime(Electricity_Price['Time'],format = '%d-%m-%Y %H:%M:%S')
Electricity_Usage['Time'] = Electricity_Usage['Time'].str.strip()
Electricity_Usage['Time'] = pd.to_datetime(Electricity_Usage['Time'],format = '%d.%m.%Y %H:%M')

# Join the two data frames according to time
PriceAndUsage = pd.merge(Electricity_Price,Electricity_Usage, on = 'Time', how = 'inner')

PriceAndUsage['Energy (kWh)'] = PriceAndUsage['Energy (kWh)'].str.replace(',', '.').astype(float)
PriceAndUsage['Temperature'] = PriceAndUsage['Temperature'].str.replace(',', '.').astype(float)

# Calculate the hourly bill paid (using information about the price and the consumption)
PriceAndUsage['PriceTotalPerHour'] = pd.to_numeric(PriceAndUsage['Price (cent/kWh)']) * pd.to_numeric(PriceAndUsage['Energy (kWh)'])

# Calculated grouped values of daily, weekly or monthly consumption, bill, average price and average temperature
d1 = st.date_input("Start time", datetime.date(PriceAndUsage['Time'][0].year, PriceAndUsage['Time'][0].month, PriceAndUsage['Time'][0].day))
d2 = st.date_input("End time", datetime.date(PriceAndUsage['Time'][len(PriceAndUsage)-1].year, PriceAndUsage['Time'][len(PriceAndUsage)-1].month, PriceAndUsage['Time'][len(PriceAndUsage)-1].day))
st.write("Showing range:", d1, " - ", d2)

FixedPrice = st.number_input('Compare against fixed electricity price. Enter value in cents.')

d1 = pd.to_datetime(d1)
d2 = pd.to_datetime(d2)

PriceAndUsage=PriceAndUsage[PriceAndUsage['Time']>d1]
PriceAndUsage=PriceAndUsage[PriceAndUsage['Time']<d2]


st.write("Total consumption over the period:", PriceAndUsage['Energy (kWh)'].sum().round(), " KWh")
st.write("Total bill over the period:", round(PriceAndUsage['PriceTotalPerHour'].sum()/100,0), "€ - With fixed price:", round((PriceAndUsage['Energy (kWh)'].sum() * FixedPrice) / 100, 0), " €")
st.write("Average hourly price:", PriceAndUsage['Price (cent/kWh)'].mean().round(2), "cents")
st.write("Average paid price:", pd.to_numeric(round(PriceAndUsage['PriceTotalPerHour'].sum(),0)/PriceAndUsage['Energy (kWh)'].sum().round()).mean().round(2), "cents")

options = {
    "Daily": 'd',
    "Weekly": 'W',
    "Monthly": 'M',
    "Yearly": 'Y'
}

selected_option = st.selectbox("Averaging period:", list(options.keys()))
returned_value = options[selected_option]
st.write(f"Selected option: {selected_option}")

freq_value = options[selected_option]

consumption = (PriceAndUsage.groupby(pd.Grouper(key = 'Time', freq = freq_value))[['Energy (kWh)']].sum()).reset_index()
price = (PriceAndUsage.groupby(pd.Grouper(key = 'Time', freq = freq_value))[['Price (cent/kWh)']].sum()).reset_index()
bill = (PriceAndUsage.groupby(pd.Grouper(key = 'Time', freq = freq_value))[['PriceTotalPerHour']].sum()/100).reset_index()
temp = (PriceAndUsage.groupby(pd.Grouper(key = 'Time', freq = freq_value))[['Temperature']].mean()).reset_index()

st.line_chart(consumption, x = 'Time', y = 'Energy (kWh)',y_label= 'Electricity consumption [KWh]', x_label='Time')
st.line_chart(price, x = 'Time', y = 'Price (cent/kWh)',y_label= 'Electricity price [cents]', x_label='Time')
st.line_chart(bill, x = 'Time', y = 'PriceTotalPerHour',y_label= 'Electricity bill [€]', x_label='Time')
st.line_chart(temp, x = 'Time', y = 'Temperature',y_label= 'Temperature', x_label='Time')

st.table(temp)
