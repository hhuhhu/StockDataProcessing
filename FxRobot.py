import oandapy
import matplotlib.pyplot as plt
from Config import Config
from os import path
import datetime
import numpy

config = Config()
oanda = oandapy.API(environment="practice", access_token = config.token)
asks = list()
bids = list()
price_change = list()
f_back_log = open(path.relpath(config.back_log_path + '/' + config.insName + '_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))+'.log', 'a');
time = 0
times = list()
last_result = 'hold'
deals = list()
deal_price = 0
max_spread = 0
min_spread = 1
plusDeals = 0
minusDeals = 0
meanDeals = 0

if config.write_back_log:
    print 'Backlog file name:', f_back_log.name
    f_back_log.write('DateTime,Instrument,ASK,BID,Price change,Status, Spread, Result \n')

def get_real_prices():
    response = oanda.get_prices(instruments=config.insName)
    prices = response.get('prices')
    ask = prices[0].get('ask')
    bid = prices[0].get('bid')
    status = prices[0].get('status')
    if status == 'halted':
        print config.insName, 'is halted.'
        return
    asks.append(ask)
    bids.append(bid)
    lastPrice = (ask+bid)/2
    if (len(asks) > 1) and (len(bids) > 1):
        lastPrice = (asks[len(asks)-2] + bids[len(bids)-2]) / 2
    pChange = (ask+bid)/2 - lastPrice
    price_change.append(pChange)
    result = process_data(price_change, ask, bid)
    global last_result
    global deal_price
    global plusDeals
    global minusDeals
    global meanDeals
    if result != 'hold':
        diff = 0
        if last_result == 'buy':
                diff = pChange - deal_price
        if last_result == 'sell':
                diff = deal_price - pChange
        if diff != 0:
            deals.append(diff)
            if diff >= max_spread:
                plusDeals = plusDeals + 1
            if diff <= min_spread:
                minusDeals = minusDeals + 1
            if diff > min_spread and diff < max_spread :
                meanDeals = meanDeals + 1
        last_result = result
        deal_price = pChange
    if config.write_back_log:
        f_back_log.write('%s,%s,%s,%s,%s,%s,%s,%s \n' % (datetime.datetime.now(), config.insName, prices[0].get('ask'), prices[0].get('bid'), pChange, prices[0].get('status'), ask-bid, result))
    print time, "s : ", result, ' spread size: ', ask - bid

def process_data(price_change, ask, bid):
    result = 'hold'
    global last_result
    global  max_spread
    global  min_spread
    plt.clf()
    times.append(time)
    hmin = 0
    hmax = 0
    plt.subplot(2,1,1)
    if len(price_change) > 3:
        hmaxs = list()
        for i in range(1, len(price_change) - 2):
            if price_change[i] > price_change[i-1] and price_change[i] > price_change[i+1]:
                hmaxs.append(price_change[i])
        if len(hmaxs) > 0:
            hmax = numpy.mean(hmaxs)
            plt.axhline(y=hmax, label='MAX', color='red', linestyle=':')
        hmins = list()
        for i in range(1, len(price_change) - 2):
            if price_change[i] < price_change[i-1] and price_change[i] < price_change[i+1]:
                hmins.append(price_change[i])
        if len(hmins) > 0:
            hmin = numpy.mean(hmins)
            plt.axhline(y=hmin, label='MIN', color='green', linestyle=':')
    if hmin != 0 and hmax != 0:
        if price_change[len(price_change)-1] >= hmax:
            if last_result != 'sell':
                result = 'sell'
        if price_change[len(price_change)-1] <= hmin:
            if last_result != 'buy':
                result = 'buy'
        if price_change[len(price_change) - 1] > hmin and price_change[len(price_change)-1] < hmax:
            if last_result != 'close' and last_result!='hold':
                result = 'close'
    plt.plot(times, price_change, label='Price change', color='blue',  marker='')
    plt.title(config.insName)
    plt.xlabel('Time, s')
    plt.legend(loc='upper left')

    plt.subplot(2,2,3)
    plt.hist(deals,color='blue')
    spread = ask - bid
    if max_spread < spread :
        max_spread = spread
    if min_spread > spread:
        min_spread = spread
    plt.axvline(x = spread, color='red')
    plt.axvline(x = max_spread, color='gray', linestyle=":")
    plt.axvline(x = min_spread, color='gray', linestyle=":")
    plt.ylabel('Count of deals')
    plt.legend(loc='upper left')
    plt.xticks([])

    plt.subplot(2, 2, 4)
    plt.legend(loc='upper left')
    totalDeals = minusDeals + meanDeals + plusDeals
    if totalDeals!=0:
        plt.bar(0, 100 * float(minusDeals)/float(totalDeals), color='red')
        plt.bar(1, 100 * float(meanDeals)/float(totalDeals), color='blue')
        plt.bar(2, 100 * float(plusDeals)/float(totalDeals), color='green')
    plt.xticks([0.5,1.5,2.5], ['Minus', 'Mean', 'Plus'])
    plt.ylabel('% of deals')
    plt.margins(0.1)

    if len(asks) > config.maxLength:
        asks.pop(0)
    if len(bids) > config.maxLength:
        bids.pop(0)
    if len(price_change) > config.maxLength:
        price_change.pop(0)
    if len(times) > config.maxLength:
        times.pop(0)

    plt.tight_layout()
    return result


plt.ion()
plt.grid(True)

while True:
    get_real_prices()
    plt.pause(config.period)
    time = time + config.period


