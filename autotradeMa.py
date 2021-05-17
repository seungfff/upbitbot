import time
import pyupbit
import datetime
import requests

access = "LPBFmfkxrRHptrldCidIGfCGGtbFk0jXqv0xBvx4"
secret = "AlTtv1GKSFqmoDtqCK3S4aRdedNP5hjbpC1fCqE5"


def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
 
myToken = "xoxb-2054471993015-2093053772496-RaZjH0BBSpWx5GFcnRXaC1Vp"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        nowDate = now.strftime('%Y-%m-%d')
        moningHour = 9
        moningMinute = 0
        
        start_time = get_start_time("KRW-DOGE")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=60):
            target_price = get_target_price("KRW-DOGE", 0.3)
            ma15 = get_ma15("KRW-DOGE")
            current_price = get_current_price("KRW-DOGE")

            if moningHour == now.hour and moningMinute == now.minute: 
                post_message(myToken,"#event",str(nowDate)+"  매수 목표가 : "+str(target_price))
                post_message(myToken,"#event",str(nowDate)+"  매도 목표가 : "+str(ma15))

            if target_price < current_price and ma15 < current_price:
                post_message(myToken,"#event",str(now)+"  매수 신호포착 및 매수주문 : "+str(target_price))
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-DOGE", krw*0.9995)
        else:
            iq = get_balance("DOGE")
            if iq > 0.00008:
                post_message(myToken,"#event",str(now)+"  매도 신호포착 및 매수주문 : "+str(ma15))
                upbit.sell_market_order("KRW-DOGE", iq)
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#event",e)
        time.sleep(1)