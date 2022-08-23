# amherst-baseball-bot
A bot for the Amherst College baseball GroupMe. 

Features:
Say Hello
Say a funny quote
Get the dining hall meals.
Get the current weather.

Some things to come in the future maybe. 

Made by Kyler Kopacz '21, Chris Murphy '22, Charlie Estes '22, Daniel Qin '22, Jimin Kang '23

## **Setup**:

### **Make a Heroku account**
First, make a heroku account.

Once you do that, create a new app. 

Once you do that, connect that app to this github repo (or whatever repo you want).

### **Setup the groupme API stuff**
Sign into the GroupMe developer API site:

https://dev.groupme.com/bots

Next, make a new bot. Fill out the name, and which groupchat it is going to be placed into. 

For the callback URL, go back into your Heroku app, go to the settings tab, then under domains you should see something like "Your app can be found at: <LINK>"

Copy and paste that link into the callback URL field on the GroupMe API Bots creation thing.

Click finish, and the bot should be added to the group.

### **Get the bot ID and link it with Heroku**
Click on your bot information on the GroupMe API page and copy the "bot ID" field.

Go back into Heroku app, then settings tab again, then under "Config Vars", create a new config variable with the key as ```GROUPME_BOT_ID``` and the value is the value listed in the groupme api page.

Click done and then your bot should hopefully start working. 
