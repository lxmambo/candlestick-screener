from flask import Flask, render_template, request
from patterns import patterns
import yfinance as yf
import pandas as pd
import talib
import os,sys,csv

app = Flask(__name__)

@app.route('/')
def index():
    #when we select a pattern on the dropbox it sents a query parameter
    #to the url and flask needs to capture that into a variable
    #we need to get some information about the request
    #request is an object that has information about the request
    #including the ip address that it came from, any post form variables
    pattern = request.args.get('pattern',None)
    #get all arguments and get the argument called pattern. If is not
    #present we give a default of none

    stocks = {} #stocks are going to be a dictionary

    with open('datasets/companies.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company':row[1]}
            #the key of the dictionary is going to be the symbol
            #and point to another dictionary and we will
            #have the company name in that dictionary and also
            #if there is a bullish or bearish pattern
            #row[0] is the symbol, the key
            #the key of 'stocks' points to another dictionary?

    print(stocks)
    if pattern:
        #we need to apply the function in 'pattern' to all the 
        #datasets extracted from yfinance
        #os.listdir() method lists all the files in a directory and then
        #we can loop through it.
        datafiles = os.listdir('datasets/daily')
        for filename in datafiles:
            #we will use pandas to read the dataset into a dataframe
            #pandas.read_csv() function makes a csv file into dataframe
            df = pd.read_csv('datasets/daily/{}'.format(filename))
            #if we have a name of a function in a string, how we call it in 
            #talib dynamically. getattr() -> if the string is the name of one
            # of the object's attributs, ther result is the value of that
            # attribute. getattr(x, 'foobar') resutl is x.foobar
            pattern_function = getattr(talib, pattern)
            
            symbol = filename.split('.')[0]
            try:
                result = pattern_function(df['Open'],df['High'],df['Low'],df['Close'])
                #we want to focus in the last result. a funçao tail do pandas retorna
                #as últimas linhas (5 por default)
                last = result.tail(1).values[0] #como retorna uma lista de um só valor...
                #print(last)
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
                #print("{} triggered {}".format(filename, pattern))
            except:
                pass
    return render_template('index.html', patterns=patterns, stocks=stocks, current_pattern = pattern)
    #sending a variable to the html template
    #is called patterns and passes the patterns
    #it also passes the stocks to the template, and also pattern

#this function is going to take a snapshot
#of the daily closes of all the stocks in the S&P500 -> at the end each day
#we run automatically and get a snapshot and scan trading ideas
@app.route('/snapshot')
def snapshot():
    #open the file with the tickers and companies names
    #f is a reference to the file
    with open('datasets/companies.csv') as f:
        #read the contents of the file and split lines
        #gets the lines in the file and puts it 
        #on a python list
        companies = f.read().splitlines()
        for company in companies:
            #the symbol will be the first token if the
            #company is split at the comma
            symbol = company.split(',')[0]
            #yf.download returns a pandas dataframe -> df
            df = yf.download(symbol, start="2020-01-01", end="2020-08-22")
            #it records the data in the daily subfolder
            #if we want to have data for other time frames...weekly, hourly...
            df.to_csv('datasets/daily/{}.csv'.format(symbol))
            #we can load each of the files generated into a dataframe
            #to which we can apply TA-Lib functions