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

etherscan_apikey  = 'Y4FWA2X96S3MVSGE48BBF6T8MXEMMMNC3V'
etfx_address      = '0x9c5e7329f4Fb3c9e4ea567987151aa09D8212BB3'
total_etfx        = 100000000000000
uniswap_address   = '0x05E318D47454BdcCbF390C8531d334C36c934C26'

# POOLs
lp_contractaddress    = ''
lp_rewardSpeedDaily   = 166600000000

etfx_contractaddress  = ''
etfx_rewardSpeedDaily = 55500000000

dai_contractaddress   = ''
dai_rewardSpeedDaily  = 55500000000

usdt_contractaddress  = ''
usdt_rewardSpeedDaily = 55500000000




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
                elif key == 'Locked_DAIToken':
                  temp = self.getLockedDAIToken()
                elif key == 'Locked_USDTToken':
                  temp = self.getLockedUSDTToken()
                elif key == 'Locked_ETFXToken':
                  temp = self.getLockedETFXToken()
                elif key == 'ETFXETH':
                  temp = self.getETFXETH()
                elif key == 'UNItETH':
                  temp = self.getUNItETH()
                elif key == 'ETHUSD':
                  temp = self.getETHUSD()
                elif key == 'ETHBTC':
                  temp = self.getETHBTC()
                elif key == 'DAIETH':
                  temp = self.getDAIETH()
                elif key == 'USDTETH':
                  temp = self.getUSDTETH()

                print(int(round(time.time())))
                del self.db[key]
                time.sleep(1)
          except Exception as e: print(e)
        threading.Timer(30.0, self.wathcher).start()

    def testAll(self):
        print(self.getLockedLPToken())
        time.sleep(1)
        print(self.getLockedDAIToken())
        time.sleep(1)
        print(self.getLockedUSDTToken())
        time.sleep(1)
        print(self.getLockedETFXToken())
        time.sleep(1)
        print(self.getETFXETH())
        time.sleep(1)
        print(self.getUNItETH())
        time.sleep(1)
        print(self.getETHUSD())
        time.sleep(1)
        print(self.getETHBTC())
        time.sleep(1)
        print(self.getDAIETH())
        time.sleep(1)
        print(self.getUSDTETH())

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
          
    def getLockedDAIToken(self):
        key = 'Locked_DAIToken'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress="+dai_contractaddress+"&apikey="+etherscan_apikey).json()
            #print(etherscan['result'])
            jblock = {'time':int(round(time.time())), 'data':etherscan['result']}
            self.db[key] = jblock
            return jblock['data']
          
    def getLockedUSDTToken(self):
        key = 'Locked_USDTToken'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress="+usdt_contractaddress+"&apikey="+etherscan_apikey).json()
            #print(etherscan['result'])
            jblock = {'time':int(round(time.time())), 'data':etherscan['result']}
            self.db[key] = jblock
            return jblock['data']
          
    def getLockedETFXToken(self):
        key = 'Locked_ETFXToken'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress="+etfx_contractaddress+"&apikey="+etherscan_apikey).json()
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

    def getDAIETH(self):
        key = 'DAIETH'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=proxy&action=eth_call&to=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D&data=0xd06ca61f00000000000000000000000000000000000000000000000000000000000186a000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000006b175474e89094c44da98b954eedeac495271d0f&tag=latest&apikey="+etherscan_apikey).json()
            
            pricehex = etherscan['result'][-32:]
            priceint = int(pricehex, 16)
            jblock = {'time':int(round(time.time())+630), 'data':float(100000/priceint)}
            self.db[key] = jblock
            return jblock['data']

    def getUSDTETH(self):
        key = 'USDTETH'
        if key in self.db:
            return self.db[key]['data']
        else:
            etherscan = self.session.get("https://api.etherscan.io/api?module=proxy&action=eth_call&to=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D&data=0xd06ca61f00000000000000000000000000000000000000000000000000000000000186a000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000006b175474e89094c44da98b954eedeac495271d0f&tag=latest&apikey="+etherscan_apikey).json()
            
            pricehex = etherscan['result'][-32:]
            priceint = int(pricehex, 16)
            
            jblock = {'time':int(round(time.time())+630), 'data':float(100000/priceint)}
            self.db[key] = jblock
            return jblock['data']

    
class BaseHandler(tornado.web.RequestHandler):
    def getLockedLPToken(self):
        return self.application.getLockedLPToken()

    def getLockedETFXToken(self):
        return self.application.getLockedETFXToken()

    def getLockedDAIToken(self):
        return self.application.getLockedDAIToken()

    def getLockedUSDTToken(self):
        return self.application.getLockedUSDTToken()

    def getETFXETH(self):
        return self.application.getETFXETH()

    def getUNItETH(self):
        return self.application.getUNItETH()

    def getDAIETH(self):
        return self.application.getDAIETH()

    def getUSDTETH(self):
        return self.application.getUSDTETH()




class NotFoundHandler(BaseHandler):
    def get(self):  # for all methods
        self.write({"code": 404,"msg": "Invalid API resource path."})
    def post(self):  # for all methods
        self.write({"code": 404,"msg": "Invalid API resource path."})
        
class APRsHandler(BaseHandler):
    def get(self):
        lp_wraped = self.getLockedLPToken()
        lp_rewardPerToken = lp_rewardSpeedDaily/int(lp_wraped)
        lp_rewardPerTokenPerYear = lp_rewardPerToken * 365
        lp_rewardPerTokenPerYearinETH = lp_rewardPerTokenPerYear * self.getETFXETH()
        uniAPY = "0.00"
        if self.getUNItETH() > 0:
          uniAPY = "%.2f" % ((lp_rewardPerTokenPerYearinETH/self.getUNItETH())*100)

        etfx_wraped = self.getLockedETFXToken()
        etfx_rewardPerToken = etfx_rewardSpeedDaily/int(etfx_wraped)
        etfx_rewardPerTokenPerYear = etfx_rewardPerToken * 365
        etfx_rewardPerTokenPerYearinETH = etfx_rewardPerTokenPerYear
        etfxAPY = "%.2f" % ((etfx_rewardPerTokenPerYearinETH)*100)

        dai_wraped = self.getLockedDAIToken()
        dai_rewardPerToken = dai_rewardSpeedDaily/int(dai_wraped)
        dai_rewardPerTokenPerYear = dai_rewardPerToken * 365
        dai_rewardPerTokenPerYearinETH = dai_rewardPerTokenPerYear * self.getETFXETH()
        daiAPY = "0.00"
        if self.getDAIETH() > 0:
          daiAPY = "%.2f" % ((dai_rewardPerTokenPerYearinETH/self.getDAIETH())*100)

        usdt_wraped = self.getLockedUSDTToken()
        usdt_rewardPerToken = usdt_rewardSpeedDaily/int(usdt_wraped)
        usdt_rewardPerTokenPerYear = usdt_rewardPerToken * 365
        usdt_rewardPerTokenPerYearinETH = usdt_rewardPerTokenPerYear * self.getETFXETH()
        usdtAPY = "0.00"
        if self.getUSDTETH() > 0:
          usdtAPY = "%.2f" % ((usdt_rewardPerTokenPerYearinETH/self.getUSDTETH())*100)
        
        self.write({"ETFXUniV2Pool":{"APY": uniAPY},"ETFXPool":{"APY": etfxAPY},"ETFXDAIPool":{"APY": daiAPY},"ETFXUSDTPool":{"APY": usdtAPY}})
        
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
