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
    receivedMessage = data['text'].split('\n')
    print(f"RECEIVED MESSAGE:{receivedMessage}")
    print(f"EDITED MESSAGE:{receivedMessage[0].lower().strip()}")
    # branch to the correct function according to the text that we got
    if receivedMessage[0].lower().strip() == '!weather':
        msg = getWeather()
    elif receivedMessage[0].lower().strip() == '!hello':
        msg = "Hey {}!".format(data['name'])
    elif receivedMessage[0].lower().strip() == '!quote':
        msg = getQuote()
    elif receivedMessage[0].lower().strip() == '!fun':
        msg = getFun()
    elif receivedMessage[0].lower().strip() == '!news':
        msg = getNews()
    elif receivedMessage[0].lower().strip() == '!breakfast':
        msg = getMeal_Updated('Breakfast')
    elif receivedMessage[0].lower().strip() == '!lunch':
        msg = getMeal_Updated('Lunch')
    elif receivedMessage[0].lower().strip() == '!dinner':
        msg = getMeal_Updated('Dinner')
    elif receivedMessage[0].lower().strip() == '!latenight':
        msg = getMeal_Updated('Late Night')
    elif receivedMessage[0].lower().strip() == '!gng':
        msg = getGNG()
    elif receivedMessage[0].lower().strip() == '!ligma':
        msg = getLigma()
    elif receivedMessage[0].lower().strip() == '!communism':
        msg = getCommunism()
    elif receivedMessage[0].lower().strip() == '!help':
        msg = getHelp()
    return msg

def getHelp():
    msg = '''
BrotherBot v1.13.0 Commands:

"!Weather" - Get the current and future weather for Amherst College

"!Hello" - Just to say hi

"!Quote" - To hear a quote

"!Fun" - To get the weekend's schedule

"!Breakfast/Lunch/Dinner/Late Night" - Get the Valentine Dining Hall meals for the specified meal

"!gng" - Get the Grab and Go Menu for the day

"!News" - Get the latest Mammo news letter

"!Communism" - Learn about the economic theory of Communism

"!Help" - To get BroBot commands
    '''
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
    #if day number is single digit, remove the extra 0 (ex: September 01 -> September 1)
    dayNum = today.split(" ")[2] #day number will be the third element in "Monday, August 29, 2022" format
    if dayNum.startswith("0"):
      dayNum_edited = dayNum[1:]
      today = today.replace(dayNum, dayNum_edited, 1)
    
    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/menu', verify = False)
    soup = BeautifulSoup(page.content, 'html.parser')
    # results = soup.find_all(id='dining-menu-' + date + '-' + meal)
    results = soup.find(text=today)
    # print(results.parent)
    meals = results.parent.find_next('section').find_all('article')
    #print(results.parent.find_next('section'))
    msg = ''
    lineNum = 0
    mealDict = {
        "Breakfast" : 0,
        "Lunch" : 1,
        "Dinner" : 2,
        "Late Night" : 3
    }
    
    mealNum = mealDict[meal]
    if mealNum < 3:
        # Formatting the meals
        for string in meals[mealNum].strings:
            string = str(string)
            if string=="\n":
                pass
            else:
                if lineNum==0:
                    string = string + ":"+"\n"
                else:
                    if lineNum%2==1:
                        string = "\n"+"***" + string + "***"
                    else:
                        string = string
                msg+=string+'\n'
                lineNum+=1
        msg = "\n".join(msg.split("\n")[:-2])

    if mealNum >= len(meals):
        return 'No Late Night Today'
    elif mealNum == 3:
        for index, i in enumerate(meals[mealNum].strings):
            i = str(i)
            if i =="\n":
                continue
            if lineNum == 0:
                i+="\n\n"
            lineNum+=1
            i = i.replace('; ','\n')
            msg+=i
    return msg

def getGNG():
    '''
    This is the function to get the current meal. If they change the meal website, this will be broken.
    '''
    today = datetime.today().strftime('%A, %B %d, %Y') #ex: Monday, August 29, 2022
    weekend = ['Saturday','Sunday']
    for i in weekend:
        if i in today:
            return "No Grab-n-Go today"
    #if day number is single digit, remove the extra 0 (ex: September 01 -> September 1)
    dayNum = today.split(" ")[2] #day number will be the third element in "Monday, August 29, 2022" format
    if dayNum.startswith("0"):
      dayNum_edited = dayNum[1:]
      today = today.replace(dayNum, dayNum_edited, 1)

    page = requests.get('https://www.amherst.edu/campuslife/housing-dining/dining/dining-options-and-menus/grab-n-go-menu', verify = False)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(text=today)
    meals = results.parent.parent.parent.strings
    copyMeals = []
    chars = 'qwertyuiopasdfghjklzxcvbnm,.1234567890"QWERTYUIOPASDFGHJKLZXCVBNM &'
    for i in meals:
        line = ''
        for j in i:
            if j in chars:
                line+=j
        if not line == '':
            copyMeals.append(line)
    msg = ''
    for i in copyMeals:
        msg+=i
        msg+='\n\n'
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
    
    print("Fun function called")
    
    msg = 'Ask Newbie'

    return msg

def getNews():
    msg = 'Shut up Dove'
    return msg

def getLigma():
    msg = 'ligma balls bitch @Robin'
    return msg

def getCommunism():
    msg = 'https://en.wikipedia.org/wiki/Red_Terror\n' \
          'https://en.wikipedia.org/wiki/Soviet_famine_of_1930%E2%80%931933\n' \
          'https://en.wikipedia.org/wiki/Great_Purge\n' \
          'https://en.wikipedia.org/wiki/Soviet_war_crimes\n' \
          'https://en.wikipedia.org/wiki/Great_Chinese_Famine\n' \
          'https://en.wikipedia.org/wiki/1989_Tiananmen_Square_protests_and_massacre'
    return msg
