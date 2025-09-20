# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 11:50:38 2025

Oil Contract Value Calculator

@author: Sarah
"""

#===============================================================
# Imports

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.optimize import curve_fit
from datetime import date, timedelta

#===============================================================
# Functions

def sinusoid(x, A, w, phi):
    return A*np.sin(w*x + phi)

def date_to_day(date):
    
    date_input = pd.to_datetime(date, format="%m/%d/%y").date()
    
    day_input = (date_input - start_date).days
    
    return day_input

def day_to_price(day):
    
    day_input_array = np.array([day]).reshape(-1,1)
    
    extrap_trend = model.predict(day_input_array) 
    extrap_sinusoid_fit = sinusoid(day_input_array, A, w, phi)
    price_per_unit = extrap_trend + extrap_sinusoid_fit

    return price_per_unit

#===============================================================
# reading and organising data

df = pd.read_csv("Nat_Gas.csv") 

df['Dates'] = pd.to_datetime(df['Dates'], format="%m/%d/%y")

prices = df['Prices'].values # Prices is 1D NumPy array
dates = df['Dates'] # Dates column now saved as 1D NumPy array datetimelike values


# Converting dates into days passes since the start of the data set
start_date = date(2020,10,31)
end_date = date(2024,9,30)
months = []
year = start_date.year
month = start_date.month + 1

while True:
    current = date(year, month, 1) + timedelta(days=-1)
    months.append(current)
    if current.month == end_date.month and current.year == end_date.year:
        break
    else:
        month = ((month + 1) % 12) or 12
        if month == 1:
            year += 1
        
# array of days since start of data set aligning to dates in data set
days_from_beginning = [(day - start_date ).days for day in months]

days_2D = np.array(days_from_beginning).reshape(-1,1) # converting to SD array


#===============================================================
# analysis

# linear trend upwards

model = LinearRegression().fit(days_2D, prices)
trend = model.predict(days_2D) 

# annual sinusoidal trend

isolated_sinusoid = prices-trend

# initial guess parameters to ensure fit is tight
A_guess = isolated_sinusoid.max() - isolated_sinusoid.min()
w_guess = 2*np.pi / 365
phi_guess = 0
p0 = [A_guess, w_guess, phi_guess]

# fitting sinusoid to data to retrieve parameters
params, covarience = curve_fit(sinusoid, days_from_beginning, isolated_sinusoid, p0=p0)
A, w, phi = params

# modelled data
sinusoid_fit = sinusoid(np.array(days_from_beginning), A, w, phi)
model_fit = trend + sinusoid_fit


#===============================================================
# Menu for inputting date


MyInput = '0'
while MyInput != 'q':
        
    print('')
    print('For Plot of Oil Price with Model Predicted Oil Price, input 1.')
    print('')
    print('For a Oil Price Estimation for a Certain Date, input 2.')
    print('')

    MyInput = input('Enter input here:')
    if MyInput == '1':
        print('You have chosen Plot of Oil Price with Model Predicted Oil Price')
        
        plt.plot(days_from_beginning, prices, label ='Data')
        plt.plot(days_from_beginning, model_fit, label='Model', color='blue')
        plt.xlabel('Days since Data Record Began')
        plt.ylabel('Price of oil ($/MMBtu)')
        plt.title('Oil Price Data with Model Price')
        plt.legend()
        plt.savefig("gasforcast.png", dpi=300)

        plt.show()
    
    if MyInput == '2':
        print('')

        # Prediciton Calculator
        
        print('Provide Information for Oil Price Prediction below')
        print('')
        print('Format dates as m/d/y with year in shorthand eg.2023->23')
        print('')
        print('')

        # Input Information
        
        InjDateInput = input('Enter date of injection here:')
        print('')
        InjUnitPrice = float(input('Enter cost to inject per MMBtu here: $'))
        print('')
        WithDateInput = input('Enter date of withdrawal here:')
        print('')
        WithUnitPrice = float(input('Enter cost to withdrawal per MMBtu here: $'))
        print('')
        Amount = float(input('Enter amount of oil being stored in MMBtu here:'))
        print('')
        store_price = float(input('Enter cost to store 1MMBtu of oil for 1 day here:'))
        print('')

        # Injection
        
        day_inject = date_to_day(InjDateInput) # day num of injection
        price_unit_day_inject = day_to_price(day_inject) # price per unit on day of injection
        
        buy_price = price_unit_day_inject*Amount
        
        price_to_inject = InjUnitPrice*Amount
        
        # Withdrawal 
        
        day_withdrawal = date_to_day(WithDateInput)
        price_unit_day_withdraral = day_to_price(day_withdrawal) 
        
        price_to_with = WithUnitPrice*Amount
        
        sell_price = price_unit_day_withdraral*Amount
        
        # Storage 
        
        store_days = day_withdrawal - day_inject
        
        storage_price = store_price*store_days
        
        # Value of Contract
        
        profit = sell_price - ( buy_price + price_to_inject + price_to_with + storage_price )
        
        print('Profit Prediction: $', profit)
    



















