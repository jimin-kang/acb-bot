# all the import statements
import os
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup
import requests
import random
from flask import Flask, request
from pathlib import Path
from datetime import datetime
import textwrap


# global variables to be used by the app later.
app = Flask(__name__)
location_coords = {'x': '42.372400734', 'y': '-72.516410713'}
location_name = "Amherst"



@app.route('/', methods=['POST'])
def webhook():
    # get the message from the POST request
    data = request.get_json()

    # parse the data that we got from the POST request
    msg = parse_message(data)
    
    # send the message that we just got from parsing the input
    send_message(msg)

    # return the correct code
    return "ok", 200


def parse_message(data):
    '''
    This is where you are going to branch for any commands that you add.
    This could really be re-worked but this is what got brobot to where he is today
    '''
    # get the actual text from the message that was sent in the chat
    recievedMessage = data['text'].split('\n')
    print(f"RECEIVED MESSAGE:{recievedMessage}")
    print(f"EDITED MESSAGE:{recievedMessage[0].lower().strip()}")
    # branch to the correct function according to the text that we got
    if recievedMessage[0].lower().strip() == '!weather':
        msg = getWeather()
    elif recievedMessage[0].lower().strip() == '!hello':
        msg = "Hey {}!".format(data['name'])
    elif recievedMessage[0].lower().strip() == '!quote':
        msg = getQuote()
    elif recievedMessage[0].lower().strip() == '!fun':
        msg = getFun()
    elif recievedMessage[0].lower().strip() == '!news':
        msg = getNews()
    elif recievedMessage[0].lower().strip() == '!breakfast':
        msg = getMeal_Updated('Breakfast')
    elif recievedMessage[0].lower().strip() == '!lunch':
        msg = getMeal_Updated('Lunch')
    elif recievedMessage[0].lower().strip() == '!dinner':
        msg = getMeal_Updated('Dinner')
    elif recievedMessage[0].lower().strip() == '!gng':
        msg = getGNG()
    elif recievedMessage[0].lower().strip() == '!ligma':
        msg = getLigma()
    elif recievedMessage[0].lower().strip() == '!help':
        msg = '''
BrotherBot v1.13.0 Commands:

"!Weather" - Get the current and future weather for Amherst College

"!Hello" - Just to say hi

"!Quote" - To hear a quote

"!Fun" - To get the weekend's schedule

"!Breakfast/Lunch/Dinner" - to get the Valentine Dining Hall meals for the specified meal

"!gng" - to get the Grab and Go Menu for the day

"!Help" - print out some help for using broterbot
    '''

    # return the message to be printed out
    return msg


def send_message(msg):
    ''' This message literally just sends (the parameter) to the groupchat'''

    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
        }

    requests.post(url, json=data)


def getWeather():
    '''
    Scrape the weather API to see what the weather is like in Amherst.
    You can probably generalize the location if you wanted, but it would be more work to get
    any other place except amherst.
    
    NOTE: There are hardcoded variables at the top of this file that get this to work.
    '''

    # request the data
    r = requests.get('https://api.weather.gov/points/' + location_coords['x'] + ',' + location_coords['y'] + '/forecast')
    weather_response = r.json()

    # parse out the current weather from the API response
    current_weather = weather_response['properties']['periods'][0]['detailedForecast']
    weather_time = weather_response['properties']['periods'][0]['name']

    # parse out the future weather from the API response
    future_weather = weather_response['properties']['periods'][1]['detailedForecast']
    future_weather_time = weather_response['properties']['periods'][1]['name']

    # This is the final message
    msg = "The " + weather_time + " forecast in " + location_name + ": " + current_weather + "\n\n"
    msg += "The " + future_weather_time + " forecast in " + location_name + ": " + future_weather

    return msg

def getMeal(meal):
    '''
    This is the function to get the current meal. If they change the meal website, this will be broken.
    '''

    # get the current time to pass into the val page
    date = strftime("%Y-%m-%d", gmtime())

    # get the current val page
    msg = ''
    counter = 0
    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/menu')
    soup = BeautifulSoup(page.content, 'html.parser')
    for meal in soup.find_all(id='dining-menu-' + date + '-' + meal):
        for string in meal.strings:
            if counter % 2 == 1 or counter == 0:
                string += ':'
            counter += 1
            msg += string + '\n\n'
     
    return msg

def getMeal_Updated(meal):
    '''
    This is the function to get the current meal. If they change the meal website, this will be broken.
    '''

    today = datetime.today().strftime('%A, %B %d, %Y') #ex: Monday, August 29, 2022

    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/menu')
    soup = BeautifulSoup(page.content, 'html.parser')
    # results = soup.find_all(id='dining-menu-' + date + '-' + meal)
    results = soup.find(text=today)
    # print(results.parent)
    meals = results.parent.find_next('section').find_all('article')
    msg = ''
    lineNum = 0
    mealDict = {
        "Breakfast" : 0,
        "Lunch" : 1,
        "Dinner" : 2
    }
    mealNum = mealDict[meal]
    for string in meals[mealNum].strings:
      string = str(string)
      if string=="\n":
        # msg+="Q"+'\n'
        pass
      else:
        if lineNum==0: #formatting for first line stating the meal
          # pass
          # string+=":"
          string = string + ":"+"\n"
        else:
          #add indent to start of string
          if lineNum%2==1:
            # string = "    " + string + ":"
            string = "\n"+"***" + string + "***"
          else:
            # string = "        " + string
            string = string
          #if string is listing items, add an extra indent at start
          #textwrap.indent(text, amount*' ')
        #add new line
        msg+=string+'\n'
        lineNum+=1
    msg = "\n".join(msg.split("\n")[:-2])
    return msg

def getGNG():
    '''
    This is the function to get the GNG meal for the day. If they change the website, this is going to break
    '''

    # get the current time to pass into the val page
    date = strftime("%Y-%m-%d", gmtime())

    # get the current grab and go page
    msg = 'Grab and Go Hours (Typically) 11:00am - 2:30pm Monday - Friday\n\n'
    counter = 0
    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/dining-options-and-menus/grabngo/Menus')
    soup = BeautifulSoup(page.content, 'html.parser')
    for meal in soup.find_all(id='dining-menu-' + date + '-grab-n-go-link-menu-listing'):
        for string in meal.strings:
            if counter % 2 == 0:
                string += ':'
            counter += 1
            msg += string + '\n\n'
    return msg

def getQuote():

    '''
    This is the function to get an AP quote
    '''
    quotes = ['I will just be her side hoe', 'Yo those bus rides are gonna be litty', 'I gotta funny feeling about tonight',
            'You know... I could just delete my instagram', 'I am the bag', 'Nah bro, I just wanna be her baby daddy',
            'Do not touch my chunkys', 'I smell delicious', 'If I was on steroids and I looked like this, it would be a disappointment', "You don't know lil Tjay!?"]
    msg = random.choice(quotes)
    return msg

def getFun():

    '''
    This is the function to get the upcoming weekend schedule'
    '''
    msg = '''Gentlemen, we've had fun over the past few days but it's time to branch out now. We're throwing the first annual Baseball Barbeque behind Mayo at 5:30. We have WoLax, WoHockey, and potentially WoSquash on the lineup card today so we're starting with a bang. Let's start the semester right. 
    
    
    P.S. Shut up Robin
    '''
    return msg
def getNews():
    msg = 'Shut up Dove'
    return msg

def getLigma():
    msg = 'ligma balls bitch @Robin'
    return msg
