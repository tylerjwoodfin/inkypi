# /usr/bin/python3
# bitcoin_ticker v1.1
# Naviavia - https://github.com/naviavia/bitcoin_ticker

import requests
import json
from time import sleep
from inky import InkyPHAT
import argparse
from PIL import Image, ImageFont, ImageDraw
import os
from font_fredoka_one import FredokaOne
import datetime
from inky.auto import auto
import subprocess
import sys

#Variables
CURR_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
RESOURCES = CURR_DIR + "resources/"
TIME = datetime.datetime.now()
COURIER_FONT = RESOURCES + "fonts/Courierprime.ttf"
API_ENDPOINT = "https://api.kraken.com/0/public/Ticker"
DP = "{:.2f}" #change the value for the required decimal places

inky_display = inky_display = auto(ask_user=True, verbose=True)
inky_display.set_border(inky_display.WHITE)

# Return first task
def getTopTask():
    output = subprocess.check_output("ssh -t pi@192.168.1.123 -p 55701 'python3 /home/pi/Git/Tasks/tasks.py ls'", shell=True).decode(sys.stdout.encoding).strip()
    output = output.splitlines()[0][1:].strip()
    return output

# Parsing flip arguments
parser = argparse.ArgumentParser()
parser.add_argument('--flip', '-f', type=str, help="true = screen is flipped")
parser.add_argument('--pair', '-p', type=str, help="Enter currency pair")
parser.add_argument('--debug', '-d', type=str, help="true = enable debug")
args, _ = parser.parse_known_args()

#Select currency based on currency pair input
def findCurrency(currency):
    if currency == "GBP":
        return str("£")
    elif currency == "USD":
        return str("$")
    elif currency == "EUR":
        return str("€")
    elif currency == "CAD":
        return str("$")
    elif currency == "AUD":
        return str("$")
        
#If coin pair is entered, find correct currency
if args.pair is not None:
    COIN = str.upper(args.pair)
    CURRENCYEXTRACT = str.upper(args.pair)[-3:]
    CURRENCYSYMBOL = findCurrency(CURRENCYEXTRACT)
else:
    COIN = "XXBTZUSD"
    CURRENCYEXTRACT = "USD"
    CURRENCYSYMBOL = "$"

#GET ERROR
def getError():
    TICKER = API_ENDPOINT + "?pair=" + COIN
    r = requests.get(TICKER)
    json_data = r.text
    fj = json.loads(json_data)
    error = fj["error"]
    return (error)
  
if len(getError())!=0:
    print("Invalid coin pair: " + args.pair)

# Get current COIN price from Kraken API
def getCoinPrice():
    TICKER = API_ENDPOINT + "?pair=" + COIN
    try:
        r = requests.get(TICKER)
        json_data = r.text
        fj = json.loads(json_data)
        lastpriceFloat = fj["result"][COIN]["c"][0]
        return DP.format(float(lastpriceFloat))
    except requests.ConnectionError:
        print("API - ERROR")
    
# Get low COIN price from Kraken API
def getCoinPriceLow():
    TICKER = API_ENDPOINT + "?pair=" + COIN
    try:
        r = requests.get(TICKER)
        if r.status_code != 200:
            print(r.status_code)
        else:
            json_data = r.text
            fj = json.loads(json_data)
            lowpriceFloat = fj["result"][COIN]["o"]
            return DP.format(float(lowpriceFloat))
    except requests.ConnectionError:
        print("API - ERROR")
    
#Calculate the 24hour percentage change
def percentUpDown():
    if getCoinPrice() > getCoinPriceLow():
        return "+"
    else:
        return ""
                
if len(getError())==0:            
    PERCENTUPDOWN = str(percentUpDown())

def percent(a, b) : 
    result = int(((b - a) * 100) / a) 
    return result 
  
if len(getError())==0: 
    a, b = float(getCoinPriceLow()),float(getCoinPrice())
    PERCENTAGE = percent(a, b)
      
#Check for file, if it doesn't exist create, otherwise read file
file_exists = os.path.isfile(CURR_DIR + "/" + "previousprice")

def updatePriceFile():
    f = open(CURR_DIR + "/" + "previousprice", "w")
    f.write(getCoinPrice())
    return float(getCoinPrice())
    
def previousPriceFile():
    if file_exists:
        ObjRead = open(CURR_DIR + "/" + "previousprice", "r")
        return ObjRead.read() or "-1";
        ObjRead.close()
    else:
        print("Price file not found")
        f = open(CURR_DIR + "/" + "previousprice", "w")
        f.write(getCoinPrice())
        return float(getCoinPrice())
        
if len(getError())==0:
    PREVIOUS_PRICE = str(previousPriceFile())
    PREVIOUS_PRICE_COMMAS = "{:,}".format(float(PREVIOUS_PRICE))
    updatePriceFile()
    
# Get price and format
if len(getError())==0:
    COINPRICELOW = float(getCoinPriceLow())
    COINPRICE = float(getCoinPrice())
    NUMBER_WITH_COMMAS = "{:,}".format(COINPRICE)

#Flip screen is false argument not passed
if args.flip != "false":
    inky_display.h_flip = True
    inky_display.v_flip = True

# get BTC logo
if len(getError())==0:
    BTCLOGO = RESOURCES + "btc.png"
    btcimg = Image.open(BTCLOGO)

#Compare current and previous prices & build price to display
if len(getError())==0:
    if (float(COINPRICE) >= float(PREVIOUS_PRICE)):
        print("Going UP")
        COINPRICE = CURRENCYSYMBOL + NUMBER_WITH_COMMAS
        ICON = RESOURCES + "icon-up.png"
        iconimg = Image.open(ICON)
    else:
        print("Going DOWN")
        COINPRICE = CURRENCYSYMBOL + NUMBER_WITH_COMMAS
        ICON = RESOURCES + "icon-down.png"
        iconimg = Image.open(ICON)

if len(getError())==0:
    if args.debug == "true":
        print("The selected pair is " + COIN)
        print("The selected currency " + CURRENCYSYMBOL + "(" + CURRENCYEXTRACT + ")")
        print("The price has changed " + PERCENTUPDOWN + str(PERCENTAGE) + "% in last 24h's")
        print("The low price is " + CURRENCYSYMBOL + "{:,}".format(COINPRICELOW))
        print("The previous price is " + CURRENCYSYMBOL + PREVIOUS_PRICE_COMMAS)
        print("The current price is " + CURRENCYSYMBOL + NUMBER_WITH_COMMAS)
        print("The ICON is " + ICON)
        

# Create a new canvas to draw on
img = Image.open(RESOURCES + "backdrop.png").resize(inky_display.resolution)
draw = ImageDraw.Draw(img)

# load the fonts, and text size
font = ImageFont.truetype(FredokaOne, 24)
fontTopTask = ImageFont.truetype(FredokaOne, 35)
font3 = ImageFont.truetype(COURIER_FONT, 50)

# Text to display and location
if len(getError())==0:
    print(getTopTask())
    img.paste(btcimg, (0, 45)) 
    img.paste(iconimg, (175, 7))
    draw.text((70, 45), str(COINPRICE), inky_display.RED, font=font3)
    draw.text((0, 100), f"{TIME.strftime('%B %d, %Y %l:%M %p')}, {PERCENTUPDOWN + str(PERCENTAGE)}% (24h)", inky_display.BLACK, font=font)
    draw.text((0, 150), "Top Task:", inky_display.YELLOW, font=fontTopTask)
    draw.text((0, 190), getTopTask(), inky_display.BLACK, font=font)
else:
    draw.text((20, 45), "INVALID PAIR", inky_display.RED, font=font3)

# Display the text
inky_display.set_image(img)
inky_display.show()
