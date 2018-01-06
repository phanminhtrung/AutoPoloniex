import time, json, requests
import sys
from _sha512 import sha512
from nt import read
from json import loads
from urllib import parse
import base64
from urllib.parse import urlencode
from urllib import request
from urllib.request import Request
from urllib.request import urlopen
from requests.api import get
import urllib.parse
import urllib
import json
import time
import hmac,hashlib
import datetime
import threading
import os
 
def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))
 
class poloniex:
    
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
 
    def post_process(self, before):
        after = before
 
        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                           
        return after
 
    def api_query(self, command, req={}):
        #print("vo dc api_query")
        if(command == "returnTicker" or command == "return24Volume"):
            response = requests.request("GET",'https://poloniex.com/public?command=' + command)
            return json.loads(response.text)
        elif(command == "returnOrderBook"):
            response = requests.request("GET",'https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair']) +"&depth=5")
            status_code = response.status_code           
            if status_code == 429:
                print ("rate limit, wait for 90 seconds")
                countdown(90)
                #time.sleep(90)
            elif status_code == 403:
                print ("need to open VPN")
            elif status_code == 200:
                jsontopython = json.loads(response.text)
                return json.loads(response.text)
        elif(command == "returnMarketTradeHistory"):
            response = requests.request("GET",'https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair']))
            return json.loads(response.text)
        else:
            #print("vo dc authen api")
            req['command'] = command
            req['nonce'] = int(time.time()*1000) + 9176125713076442143
            post_data = urllib.parse.urlencode(req).encode('utf-8')
            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest() 
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }
 
            #ret = urllib.request.Request('https://poloniex.com/tradingApi', req, headers)
            response = requests.post('https://poloniex.com/tradingApi', data=req, headers=headers)
            if command == "buy" or command == "sell":
                print(response.text)
            status_code = response.status_code          
            if status_code == 429:
                print ("rate limit, wait for 90 seconds")
                countdown(90)
                #time.sleep(90)
            elif status_code == 403:
                print ("need to open VPN")
            elif status_code == 200:
                jsontopython = json.loads(response.text)
                #print("Lenh gui di thanh cong")  
                return self.post_process(jsontopython)
            else:
                jsontopython = json.loads(response.text)
                return self.post_process(jsontopython)
            
        
 
    def returnTicker(self):
        return self.api_query("returnTicker")
 
    def return24Volume(self):
        return self.api_query("return24Volume")
 
    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})
 
    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})
 
 
    # Returns all of your balances.
    # Outputs:
    # {"BTC":"0.59098578","LTC":"3.31117268", ... }
    def returnBalances(self):
        #print("vo dc returnBalances")
        return self.api_query('returnBalances')
 
    # Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # orderNumber   The order number
    # type          sell or buy
    # rate          Price the order is selling or buying at
    # Amount        Quantity of order
    # total         Total value of order (price * quantity)
    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})
 
 
    # Returns your trade history for a given market, specified by the "currencyPair" POST parameter
    # Inputs:
    # currencyPair  The currency pair e.g. "BTC_XCP"
    # Outputs:
    # date          Date in the form: "2014-02-19 03:44:59"
    # rate          Price the order is selling or buying at
    # amount        Quantity of order
    # total         Total value of order (price * quantity)
    # type          sell or buy
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})
 
    # Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is buying at
    # amount        Amount of coins to buy
    # Outputs:
    # orderNumber   The order number
    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount, "fillOrKill":"0"})
 
    # Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount". If successful, the method will return the order number.
    # Inputs:
    # currencyPair  The curreny pair
    # rate          price the order is selling at
    # amount        Amount of coins to sell
    # Outputs:
    # orderNumber   The order number
    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})
 
    # Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
    # Inputs:
    # currencyPair  The curreny pair
    # orderNumber   The order number to cancel
    # Outputs:
    # succes        1 or 0
    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})
 
    # Immediately places a withdrawal for a given currency, with no email confirmation. In order to use this method, the withdrawal privilege must be enabled for your API key. Required POST parameters are "currency", "amount", and "address". Sample output: {"response":"Withdrew 2398 NXT."}
    # Inputs:
    # currency      The currency to withdraw
    # amount        The amount of this coin to withdraw
    # address       The withdrawal address
    # Outputs:
    # response      Text containing message about the withdrawal
    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})



def getAllPrice():
    ####### PAIR BTC and XMR #########
    global BTC_XMR_ASK
    #1 combination
    global XMR_BCN_ASK
    global BTC_BCN_BID
    #2 combination 
    global XMR_BLK_ASK
    global BTC_BLK_BID
    #3 combination
    global XMR_BTCD_ASK
    global BTC_BTCD_BID
    #4 combination
    global XMR_DASH_ASK
    global BTC_DASH_BID
    #5 combination
    global XMR_LTC_ASK
    global BTC_LTC_BID
    #6 combination
    global XMR_MAID_ASK
    global BTC_MAID_BID
    #7 combination
    global XMR_NXT_ASK
    global BTC_NXT_BID
    #8 combination
    global XMR_ZEC_ASK
    global BTC_ZEC_BID

    ####### PAIR USDT and BTC #########
    global USDT_BTC_ASK
    #1 combination
    global BTC_DASH_ASK
    global USDT_DASH_BID
    #2 combination 
    global BTC_LTC_ASK
    global USDT_LTC_BID
    #3 combination
    global BTC_NXT_ASK
    global USDT_NXT_BID
    #4 combination
    global BTC_STR_ASK
    global USDT_STR_BID
    #5 combination
    # BTC_XMR_ASK da dc define o cap tren roi
    global USDT_XMR_BID
    #6 combination
    global BTC_XRP_ASK
    global USDT_XRP_BID
    #7 combination
    global BTC_ETH_ASK
    global USDT_ETH_BID
    #8 combination
    global BTC_ETC_ASK
    global USDT_ETC_BID
    #9 combination
    global BTC_REP_ASK
    global USDT_REP_BID
    #10 combination
    global BTC_ZEC_ASK
    global USDT_ZEC_BID
    #11 combination
    global BTC_BCH_ASK
    global USDT_BCH_BID

     ####### PAIR USDT and ETH #########
    global USDT_ETH_ASK
    #1 combination
    global ETH_ETC_ASK
    #global USDT_ETC_BID
    #2 combination 
    global ETH_REP_ASK
    #global USDT_REP_BID
    #3 combination
    global ETH_ZEC_ASK
    #global USDT_ZEC_BID
    #4 combination
    global ETH_BCH_ASK
    #global USDT_BCH_BID

     ####### PAIR USDT and XMR #########
    global USDT_XMR_ASK
    #1 combination
    #global XMR_DASH_ASK 
    #global USDT_DASH_BID
    #2 combination 
    #global XMR_LTC_ASK
    #global USDT_LTC_BID
    #3 combination
    #global XMR_NXT_ASK
    #global USDT_NXT_BID
    #4 combination
    #global XMR_ZEC_ASK
    #global USDT_ZEC_BID

    #Request API
    url = "https://poloniex.com/public?command=returnTicker"
    response = requests.request("GET",url)
    status_code = response.status_code
    print ("Network Status: ", status_code)
    if status_code == 429:
        print ("rate limit, wait for 90 seconds")
        countdown(90)
        #time.sleep(90)
    elif status_code == 403:
        print ("need to open VPN")
    elif status_code == 200:
        jsontopython = json.loads(response.text)
        #print(jsontopython)
        ###### Pair BTC and XMR #########
        BTC_XMR_ASK = float(jsontopython["BTC_XMR"]["lowestAsk"])
        #1 combination
        XMR_BCN_ASK = float(jsontopython["XMR_BCN"]["lowestAsk"])
        BTC_BCN_BID = float(jsontopython["BTC_BCN"]["highestBid"])
        #2 combination 
        XMR_BLK_ASK = float(jsontopython["XMR_BLK"]["lowestAsk"])
        BTC_BLK_BID = float(jsontopython["BTC_BLK"]["highestBid"])
        #3 combination
        XMR_BTCD_ASK = float(jsontopython["XMR_BTCD"]["lowestAsk"])
        BTC_BTCD_BID = float(jsontopython["BTC_BTCD"]["highestBid"])
        #4 combination
        XMR_DASH_ASK = float(jsontopython["XMR_DASH"]["lowestAsk"])
        BTC_DASH_BID = float(jsontopython["BTC_DASH"]["highestBid"])
        #5 combination
        XMR_LTC_ASK = float(jsontopython["XMR_LTC"]["lowestAsk"])
        BTC_LTC_BID = float(jsontopython["BTC_LTC"]["highestBid"])
        #6 combination
        XMR_MAID_ASK = float(jsontopython["XMR_MAID"]["lowestAsk"])
        BTC_MAID_BID = float(jsontopython["BTC_MAID"]["highestBid"])
        #7 combination
        XMR_NXT_ASK = float(jsontopython["XMR_NXT"]["lowestAsk"])
        BTC_NXT_BID = float(jsontopython["BTC_NXT"]["highestBid"])
        #8 combination
        XMR_ZEC_ASK = float(jsontopython["XMR_ZEC"]["lowestAsk"])
        BTC_ZEC_BID = float(jsontopython["BTC_ZEC"]["highestBid"])

        ####### PAIR USDT and BTC #########
        USDT_BTC_ASK = float(jsontopython["USDT_BTC"]["lowestAsk"])
        #1 combination
        BTC_DASH_ASK = float(jsontopython["BTC_DASH"]["lowestAsk"])
        USDT_DASH_BID = float(jsontopython["USDT_DASH"]["highestBid"])
        #2 combination 
        BTC_LTC_ASK = float(jsontopython["BTC_LTC"]["lowestAsk"])
        USDT_LTC_BID = float(jsontopython["USDT_LTC"]["highestBid"])
        #3 combination
        BTC_NXT_ASK = float(jsontopython["BTC_NXT"]["lowestAsk"])
        USDT_NXT_BID = float(jsontopython["USDT_NXT"]["highestBid"])
        #4 combination
        BTC_STR_ASK = float(jsontopython["BTC_STR"]["lowestAsk"])
        USDT_STR_BID = float(jsontopython["USDT_STR"]["highestBid"])
        #5 combination
        BTC_XMR_ASK = float(jsontopython["BTC_XMR"]["lowestAsk"])
        USDT_XMR_BID = float(jsontopython["USDT_XMR"]["highestBid"])
        #6 combination
        BTC_XRP_ASK = float(jsontopython["BTC_XRP"]["lowestAsk"])
        USDT_XRP_BID = float(jsontopython["USDT_XRP"]["highestBid"])
        #7 combination
        BTC_ETH_ASK = float(jsontopython["BTC_ETH"]["lowestAsk"])
        USDT_ETH_BID = float(jsontopython["USDT_ETH"]["highestBid"])
        #8 combination
        BTC_ETC_ASK = float(jsontopython["BTC_ETC"]["lowestAsk"])
        USDT_ETC_BID = float(jsontopython["USDT_ETC"]["highestBid"])
        #9 combination
        BTC_REP_ASK = float(jsontopython["BTC_REP"]["lowestAsk"])
        USDT_REP_BID = float(jsontopython["USDT_REP"]["highestBid"])
        #10 combination
        BTC_ZEC_ASK = float(jsontopython["BTC_ZEC"]["lowestAsk"])
        USDT_ZEC_BID = float(jsontopython["USDT_ZEC"]["highestBid"])
        #11 combination
        BTC_BCH_ASK = float(jsontopython["BTC_BCH"]["lowestAsk"])
        USDT_BCH_BID = float(jsontopython["USDT_BCH"]["highestBid"])

         ####### PAIR USDT and ETH #########
        USDT_ETH_ASK = float(jsontopython["USDT_ETH"]["lowestAsk"])
        #1 combination
        ETH_ETC_ASK = float(jsontopython["ETH_ETC"]["lowestAsk"])
        USDT_ETC_BID = float(jsontopython["USDT_ETC"]["highestBid"])
        #2 combination 
        ETH_REP_ASK = float(jsontopython["ETH_REP"]["lowestAsk"])
        USDT_REP_BID = float(jsontopython["USDT_REP"]["highestBid"])
        #3 combination
        ETH_ZEC_ASK = float(jsontopython["ETH_ZEC"]["lowestAsk"])
        USDT_ZEC_BID = float(jsontopython["USDT_ZEC"]["highestBid"])
        #4 combination
        ETH_BCH_ASK = float(jsontopython["ETH_BCH"]["lowestAsk"])
        USDT_BCH_BID = float(jsontopython["USDT_BCH"]["highestBid"])

         ####### PAIR USDT and XMR #########
        USDT_XMR_ASK = float(jsontopython["USDT_XMR"]["lowestAsk"])
        #1 combination
        XMR_DASH_ASK = float(jsontopython["XMR_DASH"]["lowestAsk"])
        USDT_DASH_BID = float(jsontopython["USDT_DASH"]["highestBid"])
        #2 combination 
        XMR_LTC_ASK = float(jsontopython["XMR_LTC"]["lowestAsk"])
        USDT_LTC_BID = float(jsontopython["USDT_LTC"]["highestBid"])
        #3 combination
        XMR_NXT_ASK = float(jsontopython["XMR_NXT"]["lowestAsk"])
        USDT_NXT_BID = float(jsontopython["USDT_NXT"]["highestBid"])
        #4 combination
        XMR_ZEC_ASK = float(jsontopython["XMR_ZEC"]["lowestAsk"])
        USDT_ZEC_BID = float(jsontopython["USDT_ZEC"]["highestBid"])
        #----------------------
        #----------------------
    return status_code

def takeAction_BTC_XMR(coin): #chua sua phan order
    print ("checking ", coin, "....")
    firstPairAsk = BTC_XMR_ASK #luon luon
    global budgetOriginal_BTC
    if coin == "bcn":
        secondPairAsk = XMR_BCN_ASK
        thirdPairBid = BTC_BCN_BID
    elif coin == "blk":
        secondPairAsk = XMR_BLK_ASK
        thirdPairBid = BTC_BLK_BID
    elif coin == "btcd":
        secondPairAsk = XMR_BTCD_ASK
        thirdPairBid = BTC_BTCD_BID
    elif coin == "dash":
        secondPairAsk = XMR_DASH_ASK
        thirdPairBid = BTC_DASH_BID
    elif coin == "ltc":
        secondPairAsk = XMR_LTC_ASK
        thirdPairBid = BTC_LTC_BID
    elif coin == "maid":
        secondPairAsk = XMR_MAID_ASK
        thirdPairBid = BTC_MAID_BID
    elif coin == "nxt":
        secondPairAsk = XMR_NXT_ASK
        thirdPairBid = BTC_NXT_BID
    elif coin == "zec":
        secondPairAsk = XMR_ZEC_ASK
        thirdPairBid = BTC_ZEC_BID
    
    firstPair = "BTC_XMR" #luon luon
    secondPair = "XMR_" + coin.upper()
    thirdPair = "BTC_" + coin.upper()

    crossrate = firstPairAsk * secondPairAsk
    if crossrate < thirdPairBid:
        percent = (thirdPairBid - crossrate)*100/crossrate
        if percent > 0.8: #neu lech >0.8% thi moi take action
            #print(firstPairAsk, secondPairAsk, thirdPairBid)
            print ("GAP ",percent)
            print ("Prices lan luot la ",firstPairAsk, " ", secondPairAsk, " ", thirdPairBid)
            amount1 = float(budgetOriginal_BTC)/firstPairAsk
            polo.buy(firstPair,firstPairAsk,amount1)        

            while True:
                getBalance = polo.returnBalances()
                XMRAmount = float(getBalance["XMR"])
                print("XMR co ", XMRAmount)
                if float(XMRAmount) > 0.0001:
                    amount2 = float(XMRAmount)/secondPairAsk
                    print("So luong mua ", coin, " la ",amount2)
                    polo.buy(secondPair,secondPairAsk,amount2)
                    break
            while True:
                getBalance = polo.returnBalances()
                amount3 = getBalance[coin.upper()]
                print(coin, " co ", amount3)
                if float(amount3) > 0.0001:
                    polo.sell(thirdPair,thirdPairBid,amount3)
                    break
            while True:
                getBalance = polo.returnBalances()
                budgetAfter_BTC = getBalance["BTC"]
                print ("Kiem tra tai khoan sau khi trade ...")
                if float(budgetAfter_BTC) > 0.0001:
                    print("BTC sau khi trade la ", budgetAfter_BTC)
                    budgetOriginal_BTC = budgetAfter_BTC
                    break
            

def takeAction_USDT_BTC(coin):
    print ("checking ", coin, "....")
    firstPairAsk = USDT_BTC_ASK #luon luon
    global budgetOriginal_USDT
    if coin == "dash":
        secondPairAsk = BTC_DASH_ASK
        thirdPairBid = USDT_DASH_BID
    elif coin == "ltc":
        secondPairAsk = BTC_LTC_ASK
        thirdPairBid = USDT_LTC_BID
    elif coin == "nxt":
        secondPairAsk = BTC_NXT_ASK
        thirdPairBid = USDT_NXT_BID
    elif coin == "str":
        secondPairAsk = BTC_STR_ASK
        thirdPairBid = USDT_STR_BID
    elif coin == "xmr":
        secondPairAsk = BTC_XMR_ASK
        thirdPairBid = USDT_XMR_BID
    elif coin == "xrp":
        secondPairAsk = BTC_XRP_ASK
        thirdPairBid = USDT_XRP_BID
    elif coin == "eth":
        secondPairAsk = BTC_ETH_ASK
        thirdPairBid = USDT_ETH_BID
    elif coin == "etc":
        secondPairAsk = BTC_ETC_ASK
        thirdPairBid = USDT_ETC_BID
    elif coin == "rep":
        secondPairAsk = BTC_REP_ASK
        thirdPairBid = USDT_REP_BID
    elif coin == "zec":
        secondPairAsk = BTC_ZEC_ASK
        thirdPairBid = USDT_ZEC_BID
    elif coin == "bch":
        secondPairAsk = BTC_BCH_ASK
        thirdPairBid = USDT_BCH_BID

    firstPair = "USDT_BTC" #luon luon
    secondPair = "BTC_" + coin.upper()
    thirdPair = "USDT_" + coin.upper()
    crossrate = firstPairAsk * secondPairAsk
    if crossrate < thirdPairBid:
        percent = (thirdPairBid - crossrate)*100/crossrate
        if percent > 0.8: #neu lech >0.6% thi moi take action
            print ("GAP ",percent)
            print ("Prices lan luot la ",firstPairAsk, " ", secondPairAsk, " ", thirdPairBid)
            amount1 = float(budgetOriginal_USDT)/firstPairAsk
            polo.buy(firstPair,firstPairAsk,amount1)
            
            while True:
                getBalance = polo.returnBalances()
                BTCAmount = float(getBalance["BTC"]) - 0.00253540
                print("BTC co ", BTCAmount)
                if float(BTCAmount) > 0.0001:
                    amount2 = float(BTCAmount)/secondPairAsk
                    print("So luong mua ", coin, " la ",amount2)
                    polo.buy(secondPair,secondPairAsk,amount2)
                    break
            while True:
                getBalance = polo.returnBalances()
                amount3 = getBalance[coin.upper()]
                print(coin, " co ", amount3)
                if float(amount3) > 0.0001:
                    polo.sell(thirdPair,thirdPairBid,amount3)
                    break
            while True:
                getBalance = polo.returnBalances()
                budgetAfter_USDT = getBalance["USDT"]
                print ("Kiem tra tai khoan sau khi trade ...")
                if float(budgetAfter_USDT) > 0.0001:
                    print("USDT sau khi trade la ", budgetAfter_USDT)
                    budgetOriginal_USDT = budgetAfter_USDT
                    break
            

def takeAction_USDT_ETH(coin):
    print ("checking ", coin, "....")
    firstPairAsk = USDT_ETH_ASK #luon luon
    global budgetOriginal_USDT
    if coin == "etc":
        secondPairAsk = ETH_ETC_ASK
        thirdPairBid = USDT_ETC_BID
    elif coin == "rep":
        secondPairAsk = ETH_REP_ASK
        thirdPairBid = USDT_REP_BID
    elif coin == "zec":
        secondPairAsk = ETH_ZEC_ASK
        thirdPairBid = USDT_ZEC_BID
    elif coin == "bch":
        secondPairAsk = ETH_BCH_ASK
        thirdPairBid = USDT_BCH_BID

    firstPair = "USDT_ETH" #luon luon
    secondPair = "ETH_" + coin.upper()
    thirdPair = "USDT_" + coin.upper()
    crossrate = firstPairAsk * secondPairAsk
    if crossrate < thirdPairBid:
        percent = (thirdPairBid - crossrate)*100/crossrate
        if percent > 0.8: #neu lech >0.8% thi moi take action
            print ("GAP ",percent)      
            print ("Prices lan luot la ",firstPairAsk, " ", secondPairAsk, " ", thirdPairBid)
            amount1 = float(budgetOriginal_USDT)/firstPairAsk
            polo.buy(firstPair,firstPairAsk,amount1)
            
            while True:
                getBalance = polo.returnBalances()
                ETHAmount = float(getBalance["ETH"]) - 0.03609977
                print("ETH co ", ETHAmount)
                if float(ETHAmount) > 0.0001:
                    amount2 = float(ETHAmount)/secondPairAsk
                    print("So luong mua ", coin, " la ",amount2)
                    polo.buy(secondPair,secondPairAsk,amount2)
                    break
            while True:
                getBalance = polo.returnBalances()
                amount3 = getBalance[coin.upper()]
                print(coin, " co ", amount3)
                if float(amount3) > 0.0001:
                    polo.sell(thirdPair,thirdPairBid,amount3)
                    break
            while True:
                getBalance = polo.returnBalances()
                budgetAfter_USDT = getBalance["USDT"]
                print ("Kiem tra tai khoan sau khi trade ...")
                if float(budgetAfter_USDT) > 0.0001:
                    print("USDT sau khi trade la ", budgetAfter_USDT)
                    budgetOriginal_USDT = budgetAfter_USDT
                    break

def takeAction_USDT_XMR(coin):
    print ("checking ", coin, "....")
    firstPairAsk = USDT_XMR_ASK #luon luon
    global budgetOriginal_USDT
    if coin == "dash":
        secondPairAsk = XMR_DASH_ASK
        thirdPairBid = USDT_DASH_BID
    elif coin == "ltc": 
        secondPairAsk = XMR_LTC_ASK
        thirdPairBid = USDT_LTC_BID
    elif coin == "nxt":
        secondPairAsk = XMR_NXT_ASK
        thirdPairBid = USDT_NXT_BID
    elif coin == "zec":
        secondPairAsk = XMR_ZEC_ASK
        thirdPairBid = USDT_ZEC_BID
    
    firstPair = "USDT_XMR" #luon luon
    secondPair = "XMR_" + coin.upper()
    thirdPair = "USDT_" + coin.upper()
    crossrate = firstPairAsk * secondPairAsk
    if crossrate < thirdPairBid:
        percent = (thirdPairBid - crossrate)*100/crossrate
        if percent > 0.8: #neu lech >0.8% thi moi take action
            print ("GAP ",percent)
            print ("Prices lan luot la ",firstPairAsk, " ", secondPairAsk, " ", thirdPairBid)
            amount1 = float(budgetOriginal_USDT)/firstPairAsk
            polo.buy(firstPair,firstPairAsk,amount1)
            
            while True:
                getBalance = polo.returnBalances()
                XMRAmount = getBalance["XMR"]
                print("XMR co ", XMRAmount)
                if float(XMRAmount) > 0.0001:
                    amount2 = float(XMRAmount)/secondPairAsk
                    print("So luong mua ", coin, " la ",amount2)
                    polo.buy(secondPair,secondPairAsk,amount2)
                    break

            while True:
                getBalance = polo.returnBalances()
                amount3 = getBalance[coin.upper()]
                print(coin, " co ", amount3)
                if float(amount3) > 0.0001:
                    polo.sell(thirdPair,thirdPairBid,amount3)
                    break
            while True:
                getBalance = polo.returnBalances()
                budgetAfter_USDT = getBalance["USDT"]
                print ("Kiem tra tai khoan sau khi trade ...")
                if float(budgetAfter_USDT) > 0.0001:
                    print("USDT sau khi trade la ", budgetAfter_USDT)
                    budgetOriginal_USDT = budgetAfter_USDT
                    break
                     
            

def monitorAll(): 
    monitorTime = 1
    global budgetOriginal_USDT
    global budgetOriginal_BTC
    #kiem tra toan bo tai khoan
    getBalance = polo.returnBalances() 
    for key in getBalance:
        if float(getBalance[key]) > 0:
            print(key, " co ", getBalance[key])
    budgetOriginal_USDT = getBalance["USDT"]
    budgetOriginal_BTC = getBalance["BTC"]
    #print ("Tai khoan USD ban dau co ", budgetOriginal_USDT)
    #print ("Tai khoan BTC ban dau co ", budgetOriginal_BTC)
    while True:    
        status_code = getAllPrice()
        if status_code == 200: #neu lay dc all price Ok
            print ("###### START MONITORING EXCHANGE - NUMBER ", monitorTime, "##########")
            print ("####### BTC and XMR #######")
            takeAction_BTC_XMR("bcn")
            takeAction_BTC_XMR("blk")
            takeAction_BTC_XMR("btcd")
            takeAction_BTC_XMR("dash")
            takeAction_BTC_XMR("ltc") 
            takeAction_BTC_XMR("maid")
            takeAction_BTC_XMR("nxt")
            takeAction_BTC_XMR("zec")
            print ("####### USDT and BTC #######")
            takeAction_USDT_BTC("dash")
            takeAction_USDT_BTC("ltc") 
            takeAction_USDT_BTC("nxt")
            takeAction_USDT_BTC("str")
            takeAction_USDT_BTC("xmr")
            #takeAction_USDT_BTC("xrp") #Trung
            #takeAction_USDT_BTC("eth") #Trung
            takeAction_USDT_BTC("etc")
            takeAction_USDT_BTC("rep")
            takeAction_USDT_BTC("zec")
            takeAction_USDT_BTC("bch")
            print ("####### USDT and ETH #######") #Trung
            takeAction_USDT_ETH("etc")
            takeAction_USDT_ETH("rep")
            takeAction_USDT_ETH("zec")
            takeAction_USDT_ETH("bch")
            print ("####### USDT and XMR #######")
            takeAction_USDT_XMR("dash")
            #takeAction_USDT_XMR("ltc")
            takeAction_USDT_XMR("nxt")
            takeAction_USDT_XMR("zec")

            monitorTime = monitorTime + 1
            time.sleep(2)
##################################### CODE MOI #########################################
########################################################################################
def showAvailableBallance():
    getBalance = polo.returnBalances() 
    for key in getBalance:
        if float(getBalance[key]) > 0:
            print(key, " co ", getBalance[key])
 
def getItemFromOrderBook(pair, type, position): 
    #eg: pair = "USDT_BTC" | type is "asks" or "bids" | position = 1 is the first place
    orderbook = polo.returnOrderBook(pair)
    #print (orderbook)
    priceAndVolume = orderbook[type][int(position)-1] 
    #print (priceAndVolume)
    return priceAndVolume

def getAllFromOrderBook():
    orderbook = polo.returnOrderBook("all")
    #print (orderbook)
    return orderbook

def takeAction(mainCurrency1, mainCurrency2, currency, orderbook, budget):
    orderBudget = budget 
    #eg: mainCurrency1 is BTC, mainCurrency2 is XMR, currency is BCN
    #Step 1: tao ra ten cac pairs can kiem tra
    print ("Checking ", currency)
    firstPair = mainCurrency1 + "_" + mainCurrency2 #BTC_XMR
    #print(firstPair)
    secondPair = mainCurrency2 + "_" + currency #XMR_BCN
    #print(secondPair)
    thirdPair =  mainCurrency1 + "_" + currency #BTC_BCN
    #print(thirdPair)
    #Step 2: get price cho cac pairs o step 1
    priceAndVolume = getItemFromOrderBook(firstPair,"asks", 1, orderbook) #lay vi tri thu 1
    firstPairAsk = priceAndVolume[0] #lay gia ask
    firstPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", firstPair, " la ", firstPairAsk)
    #print ("Volume cap ", firstPair, " la ", firstPairVolume)
    priceAndVolume = getItemFromOrderBook(secondPair,"asks", 2, orderbook) #lay vi tri thu 2
    secondPairAsk = priceAndVolume[0] #lay gia ask
    secondPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", secondPair, " la ", secondPairAsk)
    #print ("Volume cap ", secondPair, " la ", secondPairVolume)
    priceAndVolume = getItemFromOrderBook(thirdPair,"bids", 3, orderbook) #lay vi tri thu 3
    thirdPairBid = priceAndVolume[0] #lay gia bid
    thirdPairVolume = priceAndVolume[1] #lay volume
    #print("Bid cap ", thirdPair, " la ", thirdPairBid)
    #print ("Volume cap ", thirdPair, " la ", thirdPairVolume)
    #Step 3: kiem tra dieu kien lech 
    crossrate = float(firstPairAsk) * float(secondPairAsk)
    #print ("crossrate la ", crossrate)
    if ((float(thirdPairBid)-crossrate)*100/crossrate) > 0.8 : #dieu kien lech xay ra > 0.8%
        gap = (float(thirdPairBid)-crossrate)*100/crossrate
        print ("Xuat Hien Lech ", gap, "%")
        #tinh ra luong amount can mua voi bo 3 price o tren, so sanh voi volume dang co tren san
        amount1 = budget/firstPairAsk     
        amount2 = amount1/secondPairAsk     
        amount3 = amount2
        #Kiem Tra Volume
        if ((amount1 <= firstPairVolume) and (amount2 <=secondPairVolume) and (amount3 <= thirdPairVolume)):
            print ("Volume Ok, Thuc Hien Cac Orders Sau:")
            print ("Cap ", firstPair," : Mua ", amount1, " ", mainCurrency2, " | Giá Ask ", firstPairAsk )
            #polo.buy(firstPair,firstPairAsk,amount1)
            print ("Cap ", secondPair," : Mua ", amount2, " ", currency, " | Giá Ask ", secondPairAsk )
            #polo.buy(secondPair,secondPairAsk,amount2)
            print ("Cap ", thirdPair," : Ban ", amount3, " ", currency, " | Giá Bid ", thirdPairBid )
            #polo.sell(thirdPair,thirdPairBid,amount3)        
            
        else:
            print ("Volume NOT Ok. Tiep Tuc Monitor")
    print ("-----------")

def USDT_XMR(orderbook, budget_USDT):
    mainCurrency1 = "USDT"
    mainCurrency2 = "XMR"
    currencyList = ["DASH", "LTC", "NXT", "ZEC"]
    print ("##### USDT and XMR #####")
    for currency in currencyList:
        takeAction(mainCurrency1, mainCurrency2, currency, orderbook, budget_USDT)

def USDT_ETH(orderbook, budget_USDT):
    mainCurrency1 = "USDT"
    mainCurrency2 = "ETH"
    currencyList = ["ETC", "REP", "ZEC", "BCH"]
    print ("##### USDT and ETH #####")
    for currency in currencyList:
        takeAction(mainCurrency1, mainCurrency2, currency, orderbook, budget_USDT)

def USDT_BTC(orderbook, budget_USDT):
    mainCurrency1 = "USDT"
    mainCurrency2 = "BTC"
    currencyList = ["DASH", "LTC", "NXT", "STR", "XMR", "XRP", "ETH", "ETC", "REP", "ZEC", "BCH"]
    print ("##### USDT and BTC #####")
    for currency in currencyList:
        takeAction(mainCurrency1, mainCurrency2, currency, orderbook, budget_USDT)

def BTC_XMR(orderbook, budget_BTC):
    mainCurrency1 = "BTC"
    mainCurrency2 = "XMR"
    currencyList = ["BCN", "BLK", "BTCD", "DASH", "LTC", "MAID", "NXT", "ZEC"] 
    print ("##### BTC and XMR #####")
    for currency in currencyList:
        takeAction(mainCurrency1, mainCurrency2, currency, orderbook, budget_BTC)

def newMain():
    monitorTime = 1
    #kiem tra toan bo tai khoan
    #getBalance = polo.returnBalances() 
    #for key in getBalance:
    #    if float(getBalance[key]) > 0:
    #        print(key, " co ", getBalance[key])
    #Set budget cho moi order
    budget_BTC = 0.002 
    budget_USDT = 10
    while True:    
        orderbook = getAllFromOrderBook()    
        currentDT = datetime.datetime.now()
        print ("###### START MONITORING EXCHANGE - NUMBER ", monitorTime, " - ", currentDT, " ##########")        
        USDT_BTC(orderbook, budget_USDT)
        USDT_ETH(orderbook, budget_USDT)
        USDT_XMR(orderbook, budget_USDT)
        BTC_XMR(orderbook, budget_BTC)
        monitorTime = monitorTime + 1
        #time.sleep(1)

def takeActionCurrency1(mainCurrency1, mainCurrency2, currency, orderbook, budget1,budget2,logfile,info):
    orderBudget = budget1
    #eg: mainCurrency1 is BTC, mainCurrency2 is XMR, currency is BCN
    #Step 1: tao ra ten cac pairs can kiem tra
    info= info+ currency+","
    firstPair = mainCurrency1 + "_" + mainCurrency2 #BTC_XMR
    #print(firstPair)
    secondPair = mainCurrency2 + "_" + currency #XMR_BCN
    #print(secondPair)
    thirdPair =  mainCurrency1 + "_" + currency #BTC_BCN
    #print(thirdPair)
    #Step 2: get price cho cac pairs o step 1
    priceAndVolume = getItemFromOrderBook(firstPair,"asks", 1) #lay vi tri thu 1
    firstPairAsk = priceAndVolume[0] #lay gia ask
    firstPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", firstPair, " la ", firstPairAsk)
    #print ("Volume cap ", firstPair, " la ", firstPairVolume)
    priceAndVolume = getItemFromOrderBook(secondPair,"asks", 1) #lay vi tri thu 2
    secondPairAsk = priceAndVolume[0] #lay gia ask
    secondPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", secondPair, " la ", secondPairAsk)
    #print ("Volume cap ", secondPair, " la ", secondPairVolume)
    priceAndVolume = getItemFromOrderBook(thirdPair,"bids", 1) #lay vi tri thu 3
    thirdPairBid = priceAndVolume[0] #lay gia bid
    thirdPairVolume = priceAndVolume[1] #lay volume
    print (str(orderbook),file=open(logfile, "a"))

def takeActionCurrency(mainCurrency1, mainCurrency2, currency, budget1,budget2,logfile,loginf):
    budget = budget1
    #eg: mainCurrency1 is BTC, mainCurrency2 is XMR, currency is BCN
    #Step 1: tao ra ten cac pairs can kiem tra    
    firstPair = mainCurrency1 + "_" + mainCurrency2 #BTC_XMR
    #print(firstPair)
    secondPair = mainCurrency2 + "_" + currency #XMR_BCN
    #print(secondPair)
    thirdPair =  mainCurrency1 + "_" + currency #BTC_BCN
    #print(thirdPair)
    #Step 2: get price cho cac pairs o step 1
    priceAndVolume = getItemFromOrderBook(firstPair,"asks", 1) #lay vi tri thu 1
    firstPairAsk = priceAndVolume[0] #lay gia ask
    firstPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", firstPair, " la ", firstPairAsk)
    #print ("Volume cap ", firstPair, " la ", firstPairVolume)
    priceAndVolume = getItemFromOrderBook(secondPair,"asks", 1) #lay vi tri thu 2
    secondPairAsk = priceAndVolume[0] #lay gia ask
    secondPairVolume = priceAndVolume[1] #lay volume
    #print("Ask cap ", secondPair, " la ", secondPairAsk)
    #print ("Volume cap ", secondPair, " la ", secondPairVolume)
    priceAndVolume = getItemFromOrderBook(thirdPair,"bids", 1) #lay vi tri thu 3
    thirdPairBid = priceAndVolume[0] #lay gia bid
    thirdPairVolume = priceAndVolume[1] #lay volume
    #print("Bid cap ", thirdPair, " la ", thirdPairBid)
    #print ("Volume cap ", thirdPair, " la ", thirdPairVolume)
    if mainCurrency1 == "BTC":
        budget = budget2
    #Step 3: kiem tra dieu kien lech 
    crossrate = float(firstPairAsk) * float(secondPairAsk)
    #tinh ra luong amount can mua voi bo 3 price o tren, so sanh voi volume dang co tren san
    amount1 = float(budget)/float(firstPairAsk)
    amountFee1 = amount1*0.0025
    amount2 = (amount1-amountFee1)/float(secondPairAsk)   
    amountFee2 = amount2*0.0025
    amount3 = amount2 - amountFee2
    amountFee3 = amount3*0.0015
    lastAmount = amount3 - amountFee3
    gap = (float(thirdPairBid)-crossrate)*100/crossrate
    loginf= (loginf+ "CrossRate':"+str(gap)+"','"+
             "LastAmount':"+str(lastAmount)+"',\n  '"+
            firstPair+"':{'Ask':'"+str(firstPairAsk)+"','Volume':'"+str(firstPairVolume)+"','Amount':'"+str(amount1)+"','AmountFee':'"+str(amountFee1)+"'},\n   '"+
            secondPair+"':{'Ask':'"+str(secondPairAsk)+"','Volume':'"+str(secondPairVolume)+"','Amount':'"+str(amount2)+"','AmountFee':'"+str(amountFee2)+"'},\n    '"+
            thirdPair+"':{'Bid':'"+str(thirdPairBid)+"','Volume':'"+str(thirdPairVolume)+"','Amount':'"+str(amount3)+"','AmountFee':'"+str(amountFee3)+"'},\n   ")
    #print ("crossrate la ", crossrate)
    if ((gap > 0.8) and (amount1 <= firstPairVolume) and (amount2 <=secondPairVolume) and (amount3 <= thirdPairVolume)):
        #Kiem Tra Volume
        response = polo.buy(firstPair,firstPairAsk,amount1)
        if 'error' in response:
            loginf = loginf+",'errorOrder1':'"+str(response)+"','Status':'NOT OK1'"
        else:
            if response["resultingTrades"] != []:
                response= polo.buy(secondPair,secondPairAsk,amount2)
                if 'error' in response:
                    loginf = loginf+",'errorOrder2':'"+str(response)+"','Status':'NOT OK2'"
                else:
                    if response["resultingTrades"] != []:                  
                        response= polo.sell(thirdPair,thirdPairBid,amount3)
                        if 'error' in response:
                            loginf = loginf+",'errorOrder3':'"+str(response)+"','Status':'NOT OK3'"
                        else:
                            if response["resultingTrades"] != []:
                                loginf = loginf+"'Status':'Excellent'"
                                print (loginf+"}",file=open("Excellent.txt", "a"))
                            else:
                                loginf = loginf+"'Status':'NOT OK3'"
                    else:
                        loginf = loginf+"'Status':'NOT OK2'"
            else:
                loginf = loginf+"'Status':'NOT OK1'"
    else:
        logfile = "logfile_notOK.txt"
        loginf = loginf+"'Status':'NOT OK'"
    return [loginf,logfile]
def runMain(arrls1,arrls2,arrls3):
    monitorTime = 1
    #kiem tra toan bo tai khoan
    #getBalance = polo.returnBalances() 
    #for key in getBalance:
    #    if float(getBalance[key]) > 0:
    #        print(key, " co ", getBalance[key])
    #Set budget cho moi order
    budget_BTC = 0.001 
    budget_USDT = 5
    #Set currency list
    currency = arrls1
    main1 = arrls2[0]
    main2 = arrls2[1]
    logfile= arrls3[0] + "_"+ currency+ ".txt";
    while True:           
        #print ("###### START MONITORING EXCHANGE - NUMBER ", monitorTime, " - ", currentDT, " ##########")
        currentDT = datetime.datetime.now()
        loginfo = "'"+ arrls3[0] + "_"+ currency+"':{\n 'Index':'"+str(monitorTime)+"','date':'"+str(currentDT)+"','"
        log= takeActionCurrency(main1, main2, currency, budget_USDT,budget_BTC,logfile,loginfo)
        monitorTime = monitorTime + 1
        print (log[0]+"},",file=open(log[1], "a"))
    

if __name__ == "__main__":
    #monitorAll()
    #APIKey =  "VU5GUAS6-RCPZC9TQ-N3A7QCLR-YNBAQ3CB"
    #Secret =  b"ce8a55fff14004bab10e3321065778c09a330fc45ac8cdfa25574007fc3e2cda1e8ce8bbc1ad928031df22b551d1d3116e22268b1b141b6c080890316b573fa5"
    

    polo= poloniex(APIKey,Secret)
    #allBalance = polo.returnBalances()
    #print(allBalance["USDT"])
    #monitorAll() 
    #polo.sell("BTC_XMR","0.02539991","0.09956982"
    #showAvailableBallance()
    #takeAction("BTC", "XMR", "BCN")
    #newMain()
    arrCurrencyls = [[["DASH", "LTC", "NXT", "ZEC"],["USDT","XMR"],["USDT_XMR"]], 
                  [["ETC", "REP", "ZEC", "BCH"],["USDT","ETH"],["USDT_ETH"]],
                  [["DASH", "LTC", "NXT", "STR", "XMR", "XRP", "ETH", "ETC", "REP", "ZEC", "BCH"],["USDT","BTC"],["USDT_BTC"]],
                  [["BCN", "BLK", "BTCD", "DASH", "LTC", "MAID", "NXT", "ZEC"],["BTC","XMR"],["BTC_XMR"]]]

    for u in arrCurrencyls:
        for a in u[0]:
            t = threading.Thread(target=runMain, args = (a,u[1],u[2]))
            t.daemon = True
            t.start()
    
    
    
    