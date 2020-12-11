#!/usr/bin/env python3
#

import os.path
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.locks
import tornado.options
import tornado.web
import threading
import requests
import math
import json
import time


from tornado.options import define, options

define("port", default=8081, help="run on the given port", type=int)

etherscan_apikey = 'Y4FWA2X96S3MVSGE48BBF6T8MXEMMMNC3V'
etfx_address = '0x9c5e7329f4Fb3c9e4ea567987151aa09D8212BB3'
total_etfx = 100000000000000
uniswap_address = '0x05E318D47454BdcCbF390C8531d334C36c934C26'

# POOLs
lp_contractaddress = ''
lp_rewardSpeedDaily = 166600000000




class Application(tornado.web.Application):
    coins = {}
    
    def __init__(self):
        self.db = {}
        self.session = requests.session()
        self.wathcher()
        #self.testAll()
        handlers = [
            (r'/api/v1/apy', APRsHandler),
            (r'/.*', NotFoundHandler)
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            cookie_secret="v6ffsdkSmGidP9FTLLWFDfDd8bezffM3dJ",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

    def wathcher(self):
        
        newcache = self.db.copy()
        for key, value in newcache.items():
          try:
            if value['time'] < int(round(time.time()))-61:
                
                if key == 'Locked_LPToken':
                  temp = self.getLockedLPToken()
                elif key == 'ETFXETH':
                  temp = self.getETFXETH()
                elif key == 'UNItETH':
                  temp = self.getUNItETH()
                elif key == 'ETHUSD':
                  temp = self.getETHUSD()
                elif key == 'ETHBTC':
                  temp = self.getETHBTC()

                print(int(round(time.time())))
                del self.db[key]
                time.sleep(1)
          except Exception as e: print(e)
        threading.Timer(30.0, self.wathcher).start()

    def testAll(self):
        print(self.getLockedLPToken())
        print(self.getETFXETH())
        print(self.getUNItETH())
        print(self.getETHUSD())
        print(self.getETHBTC())

    def getTotalETFX(self):
        return total_etfx
          
    def getLockedLPToken(self):
        key = 'Locked_LPToken'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress="+uniswap_address+"&address="+lp_contractaddress+"&tag=latest&apikey="+etherscan_apikey).json()
            #print(etherscan['result'])
            jblock = {'time':int(round(time.time())), 'data':etherscan['result']}
            self.db[key] = jblock
            return jblock['data']

    def getETFXETH(self):
        key = 'ETFXETH'
        if key in self.db:
            return self.db[key]['data']
        else:
            etfx_clean = etfx_address.split('x')
            etherscan = self.session.get("https://api.etherscan.io/api?module=proxy&action=eth_call&to=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D&data=0xd06ca61f00000000000000000000000000000000000000000000000000000000000186a000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000"+etfx_clean[1]+"&tag=latest&apikey="+etherscan_apikey).json()
            #print(etherscan['result'])
            pricehex = etherscan['result'][-32:]
            priceint = int(pricehex, 16)
            reprice = 0
            if priceint > 0:
              reprice = float(100000/priceint)
            jblock = {'time':int(round(time.time())), 'data':reprice}
            self.db[key] = jblock
            return jblock['data']

    def getUNItETH(self):
        key = 'UNItETH'
        if key in self.db:
            return self.db[key]['data']
        else:
            totalUNI = self.session.get("https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress="+uniswap_address+"&apikey="+etherscan_apikey).json()
            time.sleep(0.5)
            weth = self.session.get("https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress=0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2&address="+uniswap_address+"&tag=latest&apikey="+etherscan_apikey).json()
            priceUNIFFYIETH = 0
            if int(totalUNI['result']) > 0:
              priceUNIFFYIETH = int(weth['result'])/int(totalUNI['result'])
            jblock = {'time':int(round(time.time())+630), 'data':float(priceUNIFFYIETH)}
            self.db[key] = jblock
            return jblock['data']

    def getETHUSD(self):
        key = 'ETHUSD'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey="+etherscan_apikey).json()
            #print(etherscan['result']['ethusd'])
            
            jblock = {'time':int(round(time.time())), 'data':float(etherscan['result']['ethusd'])}
            self.db[key] = jblock
            self.db['ETHBTC'] = {'time':int(round(time.time())+600), 'data':float(etherscan['result']['ethbtc'])}
            return jblock['data']

    def getETHBTC(self):
        key = 'ETHBTC'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=stats&action=ethprice&apikey="+etherscan_apikey).json()
            #print(etherscan['result']['ethusd'])

            self.db['ETHUSD'] = {'time':int(round(time.time())+610), 'data':float(etherscan['result']['ethusd'])}
            self.db['ETHBTC'] = {'time':int(round(time.time())+650), 'data':float(etherscan['result']['ethbtc'])}
            return float(etherscan['result']['ethbtc'])

    
class BaseHandler(tornado.web.RequestHandler):
    def getLockedLPToken(self):
        return self.application.getLockedLPToken()

    def getETFXETH(self):
        return self.application.getETFXETH()

    def getUNItETH(self):
        return self.application.getUNItETH()


class NotFoundHandler(BaseHandler):
    def get(self):  # for all methods
        self.write({"code": 404,"msg": "Invalid API resource path."})
    def post(self):  # for all methods
        self.write({"code": 404,"msg": "Invalid API resource path."})
        
class APRsHandler(BaseHandler):
    def get(self):
        wraped = self.getLockedLPToken()
        rewardPerToken = lp_rewardSpeedDaily/int(wraped)
        rewardPerTokenPerYear = rewardPerToken * 365
        rewardPerTokenPerYearinETH = rewardPerTokenPerYear * self.getETFXETH()
        APY = "0.00"
        if self.getUNItETH() > 0:
          APY = "%.2f" % ((rewardPerTokenPerYearinETH/self.getUNItETH())*100)
        self.write({"APY": APY })
        
    def post(self):  # for all methods
        self.write({"code": 404,"msg": "Invalid API resource path."})
        

def main():
    tornado.options.parse_command_line()
    # Create the global connection pool.
    app = Application()
    app.listen(options.port, address='0.0.0.0')
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
