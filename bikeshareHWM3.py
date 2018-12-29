# -*- coding: utf-8 -*-
"""
Created on Sat Oct 20 08:02:27 2018

@author: WeiMeng
"""

import pandas as pd
import numpy as np
from scipy import stats

CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }

def load_data(city, month='all', day='all'):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - pandas DataFrame containing city data filtered by month and day
    """
    
    # load data file into a dataframe
    df = pd.read_csv(CITY_DATA[city])

    # convert the Start Time and End time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])
    # extract month and day of week from Start Time to create new columns
    df['month'] = df['Start Time'].dt.month
    df['day_of_week'] = df['Start Time'].dt.weekday_name 


    # filter by month if applicable
    if month != 'all':
        # create dictionary to get the corresponding int
        month_dict = {'january':1, 'february':2, 'march':3, 'april':4, 'may':5, 'june':6}
        # filter by month to create the new dataframe
        # use list comprehension to combine filter of more than 1 month
        filtered_frame=[df[df['month']==month_dict[temp]] for temp in month]
        df=pd.concat(filtered_frame)

    # filter by day of week if applicable
    if day != 'all':
        # use list comprehension to combine filter of more than 1 month
        filtered_frame=[df[df['day_of_week']==temp.title()] for temp in day]
        df = pd.concat(filtered_frame)
    
    return df
########################################
## Main program    
# Input for city, accounting for typos and invalid city entries
run_analysis=True
continue_query=True
city='Null'
valid_days=('monday','tuesday','wednesday','thursday','friday','saturday','sunday')
valid_months=('january','february','march','april','may','june')
filterByDays=set() #variable as set
filterByMonths=set()

while not(city in CITY_DATA):
    city=input('Enter City or Type Q to quit: ').lower()
    if city=='q':   
        run_analysis=False 
        break
if run_analysis:
    print(city, 'has been chosen')
else:
    print('No City is chosen, exit programme')

# filter data
if run_analysis:    
    tofilter=input('Would you like to filter your data by day of the week or month? Y for yes and N for No: ')
    if tofilter.lower()=='y':
        temp=input('Enter the day of week or month to filter: ').lower()
        while continue_query: # to continue query until user stop
            if temp in valid_days: # variable entered is one of the days in the week
                filterByDays.add(temp)
                temp=input('Type Q to exit filtering or add days or month to continue: ').lower()
                # duplicate name is accounted for by the use of set variable
            elif temp in valid_months:
                filterByMonths.add(temp)
                temp=input('Type Q to exit filtering or add days or month to continue: ').lower()
            else:
                temp=input('invalid entry, press Q to exit filter or retype to continue: ').lower()
            
            if temp=='q':
                continue_query=False
                
        if len(filterByDays)>0 and len(filterByMonths)>0:  
            print('You have chosen to filter by ',filterByDays)
            print('You have chosen to filter by ',filterByMonths)
            df = load_data(city, filterByMonths, filterByDays)
        elif len(filterByDays)>0 and len(filterByMonths)==0:
            print('You have chosen to filter by {} only'.format(filterByDays))
            df = load_data(city, 'all', filterByDays)
        elif len(filterByDays)==0 and len(filterByMonths)>0:
            print('You have chosen to filter by {} only'.format(filterByMonths))
            df = load_data(city, filterByMonths)
        else:
            print('No filter chosen')
            df = load_data(city)
    else:
        print('No filter chosen')
        df = load_data(city)
    show_input=input('Would you like to see the filtered database (Y for yes, N for no): ').lower()
    
    toshow=True # default setting  
    first=0
    last=5      
    while toshow:
        if show_input=='y':
            print(df[first:last])
            first+=5
            last+=5
            last=min([last,len(df)])
            show_input=input('Would you like to see more filtered database (Y for yes, N for no): ').lower()
        elif show_input=='n': 
            print('You have chosen No, Exit now')
            toshow=False
        else:
            print('Not a valid entry, assume no')
            toshow=False
        
    # calculate the mode popular travelling time, using mode
    print('The most popular time of travel by month: ',valid_months[df['month'].mode()[0]-1])
    print('The most popular time of travel by day of week: ',df['day_of_week'].mode()[0])
    print('The most popular time of travel by hour of day: {}00 hrs'.format(df['Start Time'].dt.hour.mode()[0]))
    
    # calculate the mode popular travelling start and end station, using mode
    print('The most popular start station is: ',df['Start Station'].mode()[0])
    print('The most popular end station is: ',df['End Station'].mode()[0])
    
    # combine the start and end station to ascertain route
    df['route']= df['Start Station']+' to '+df['End Station']
    print('The most popular route is: ',df['route'].mode()[0])
    
    # mean of time delta to report travelling time 
    print('The average travel time is: ', (df['End Time']-df['Start Time']).mean())
    
    # use set to define the different type of subscribers
    type_of_subscribers=set(df['User Type'])
    temp=df.groupby('User Type').count()['Start Time'] # use 'Start Time' as a reference column to read out data
    for type_of_subscriber in type_of_subscribers:
        print('Among {} users, {} are {}'.format(temp.sum(),temp[type_of_subscriber],type_of_subscriber))
        
    # use set to define the different gender type, we choose to use fillna() here so that the original data is not changed
    genders=set(df['Gender'].fillna(0)) # genders contain {male, female, 0}
    temp=df.fillna(0).groupby('Gender').count()['Start Time'] # use 'Start Time' as a reference column to read out data
    # temp has all NaN replaced with 0
    for gender in genders:
        if gender != 0:
            print('Among {} valid entries, {} are / is {}'.format(temp.sum(),temp[gender],gender))
        else:
            print('Among {} valid entries, {} are / is Not valid'.format(temp.sum(),temp[gender]))
    
    # Print age
    print('The oldest user is: ',2018-df.fillna(9999)['Birth Year'].min())
    print('The youngest user is: ',2018-df.fillna(0)['Birth Year'].max())
    
    # range_values is a tuple with the various boundary values of the age range: between 0 to 20 (cat 1), 20 to 40 (cat 2) etc
    range_values=(0,10,20,30,40,50, 60, 70, 80, 90, 100, 999)
    range_cat=['NA','Less than 10', '> 10 and <= 20','> 20 and <= 30','> 30 and <= 40','> 40 and <= 50','> 50 and <= 60','> 60 and <= 70','> 70 and <= 80','> 80 and <= 90','> 90 and <= 100','> 100' ]
    
    for i in range(len(range_values)-1):
        if i==0:
            # temp contain the index for the category of range_cat. i.e. if temp[1] =1 => the age range is range_cat[temp[1]] or > 0 and <=20 etc
            # the 2018-birth year is compared with the range, if true , then multiply with the respective index of range_cat
            temp=(i+1)*np.array([((2018-df['Birth Year'])>=range_values[i]) & ((2018-df['Birth Year'])<range_values[i+1])])
        else:
            # we need to convert to np.array so that we can do temp +=..., otherwise, we cannot simply add the values in 2 lists 
            temp+=(i+1)*np.array([((2018-df['Birth Year'])>=range_values[i]) & ((2018-df['Birth Year'])<range_values[i+1])])
    
    # convert temp to Series so that we can filter out the NAs or index 0
    temp=pd.Series(temp[0])
    temp=temp[temp>0]
    # get the mode
    commonAgeRange=temp.mode()[0]
    print('The most common age range of user is: ',range_cat[commonAgeRange])