import numpy as np
import datetime

from exchange_extended import Exchange, OrderSide, Order
import orderbook_lists

import matplotlib.pyplot as plt


# all orders generated by trader_id=0 
# are created by this generator
ORDER_GENERATOR_TRADER = 0



last_p_b = None
last_p_a = None


def get_lambda(i: int) -> float:
    if i == 1:
        return 1.85
    elif i == 2:
        return 1.51
    elif i == 3:
        return 1.09
    elif i == 4:
        return 0.88
    elif i == 5:
        return 0.77
    else:
        return 0


def get_theta(i: int) -> float:
    if i == 1:
        return 0.71
    elif i == 2:
        return 0.81
    elif i == 3:
        return 0.68
    elif i == 4:
        return 0.56
    elif i == 5:
        return 0.47
    else:
        return 0


def get_mu() -> float:
    return 0.94


def get_bid_price(X: np.ndarray) -> int:
    bids = np.where(X<0)[0]
    if len(bids) > 0:
        return bids[-1]
    # if the Limit Order Book is empty on the buy side
    return None


def get_ask_price(X: np.ndarray) -> int:
    asks = np.where(X>0)[0]
    if len(asks) > 0:
        return asks[0]
    # if the Limit Order Book is empty on the sell side
    return None


def get_rates(X: np.ndarray, p_b: int, p_a: int) -> list:

    global last_p_b, last_p_a
    if p_b == None:
        p_b = last_p_b
    if p_a == None:
        p_a = last_p_a

    # constants:
    MAX_i = 5

    rates = []

    # limit buy orders
    for i in range(1, MAX_i + 1):
        price = p_a - i
        rate = get_lambda(i)
        rates.append(('limit_buy_order', price, rate))
    
    # limit sell orders
    for i in range(1, MAX_i + 1):
        price = p_b + i
        rate = get_lambda(i)
        rates.append(('limit_sell_order', price, rate))
    
    rate = get_mu()
    # market buy order
    rates.append(('market_buy_order', p_a, rate))

    # market sell order
    rates.append(('market_sell_order', p_b, rate))

    # cancel buy orders
    for i in range(1, MAX_i + 1):
        price = p_a - i
        rate = get_theta(i) * abs(X[price])
        rates.append(('cancel_buy_order', price, rate))
    
    # cancel sell orders
    for i in range(1, MAX_i + 1):
        price = p_b + i
        rate = get_theta(i) * abs(X[price])
        rates.append(('cancel_sell_order', price, rate))
    
    return rates


def get_rates_sum(rates: list) -> float:
    # constants:
    RATE = 2

    rates_sum = sum(map(lambda x: x[RATE], rates))
    return rates_sum


def get_random_event(rates: list, sum_rates: float) -> tuple[str, int]:
    # constants:
    EVENT, PRICE, RATE = 0, 1, 2

    random_choice = np.random.uniform(0, sum_rates)
    i = 0
    current_sum = rates[i][RATE]
    while current_sum <= random_choice:
        i += 1
        current_sum += rates[i][RATE]
    event, price = rates[i][EVENT], rates[i][PRICE]
    return event, price


def simulate_n_events():
    pass


# TODO: convert price (pos) to real price
# TODO: X has only orders generated or include the other orders as well?
def simulate_n_seconds(X: np.ndarray, orders: dict, prices: dict, exchange: Exchange, time: datetime.datetime, n: float) -> tuple[list, dict, dict]:
    # TODO: check p_a - 5 > 0 and p_b + 5 < n otherwise raise exception

    # orders:   order_id -> Order
    # prices:   price -> [order_id, ...]

    p_b = get_bid_price(X)
    p_a = get_ask_price(X)
    rates = get_rates(X, p_b, p_a)
    global last_p_b, last_p_a
    last_p_b = p_b
    last_p_a = p_a
    sum_rates = get_rates_sum(rates)

    simulation_time = 0
    delta_t = np.random.exponential(1.0 / sum_rates)
    simulation_time += delta_t
    
    mid_prices = []
    i = 0
    events = 0
    while simulation_time <= n: # n seconds

        event, price = get_random_event(rates, sum_rates)

        if event == 'limit_buy_order':
            X[price] -= 1

            order = Order(OrderSide.BUY, price, 1, time + datetime.timedelta(seconds=simulation_time), ORDER_GENERATOR_TRADER)
            order_id = exchange.add_limit_order(order)
            
            orders[order_id] = order
            if price in prices:
                prices[price].append(order_id)
            else:
                prices[price] = [order_id]
        elif event == 'limit_sell_order':
            X[price] += 1

            order = Order(OrderSide.SELL, price, 1, time + datetime.timedelta(seconds=simulation_time), ORDER_GENERATOR_TRADER)
            order_id = exchange.add_limit_order(order)
            orders[order_id] = order
            if price in prices:
                prices[price].append(order_id)
            else:
                prices[price] = [order_id]
        elif event == 'market_buy_order' and p_a != None:
            X[p_a] -= 1

            order = Order(OrderSide.BUY, p_a, 1, time + datetime.timedelta(seconds=simulation_time), ORDER_GENERATOR_TRADER)
            counterparty_id, order_id = exchange.add_market_order(order)

            if counterparty_id == ORDER_GENERATOR_TRADER:
                order = orders[order_id]
                price = order.price
                orders.pop(order_id)
                prices[price].remove(order_id)
        elif event == 'market_sell_order' and p_b != None:
            X[p_b] += 1

            order = Order(OrderSide.SELL, p_b, 1, time + datetime.timedelta(seconds=simulation_time), ORDER_GENERATOR_TRADER)
            counterparty_id, order_id = exchange.add_market_order(order)

            if counterparty_id == ORDER_GENERATOR_TRADER:
                order = orders[order_id]
                price = order.price
                orders.pop(order_id)
                prices[price].remove(order_id)
        elif event == 'cancel_buy_order':
            if p_b == None:
                raise Exception("There are no buy orders: invalid cancel order!")
            # TODO: check price < p_a
            if len(prices[price]) != 0:
                X[price] += 1

                # TODO: check random order is buy
                random_order_id = prices[price][np.random.randint(len(prices[price]))]
                order_id = random_order_id
                trader_id = ORDER_GENERATOR_TRADER

                exchange.cancel_order(order_id, trader_id)
                orders.pop(order_id)
                prices[price].remove(order_id)
        elif event == 'cancel_sell_order':
            if p_a == None:
                raise Exception("There are no sell orders: invalid cancel order!")
            # TODO: check price > p_b
            if len(prices[price]) != 0:
                X[price] -= 1

                # TODO: check random order is sell
                random_order_id = prices[price][np.random.randint(len(prices[price]))]
                order_id = random_order_id
                trader_id = ORDER_GENERATOR_TRADER

                exchange.cancel_order(order_id, trader_id)
                orders.pop(order_id)
                prices[price].remove(order_id)
        
        if p_b != None and p_a != None:
            mid_prices.append((p_b + p_a) / 2)
        
        # events += 1
        # if i < simulation_time:
        #     i += 100
        #     print(events)
        #     print(list(X)[:500])
        #     print("\n")

        p_b = get_bid_price(X)
        p_a = get_ask_price(X)
        rates = get_rates(X, p_b, p_a)
        if p_b != None:
            last_p_b = p_b
        if p_a != None:
            last_p_a = p_a
        sum_rates = get_rates_sum(rates)

        delta_t = np.random.exponential(1 / sum_rates)
        simulation_time += delta_t
    
    return X, orders, prices, mid_prices



if __name__ == '__main__':
    X = np.zeros(1001)
    orders = {}
    prices = {}
    buy_side = orderbook_lists.OrderBookSide(OrderSide.BUY)
    sell_side = orderbook_lists.OrderBookSide(OrderSide.SELL)
    exchange = Exchange(buy_side, sell_side)
    time = datetime.datetime.now()
    n = 1000

    # init #1
    X[95] = -1
    price = 95
    order = Order(OrderSide.BUY, price, 1, datetime.datetime.now(), ORDER_GENERATOR_TRADER)
    order_id = exchange.add_limit_order(order)
    orders[order_id] = order
    prices[price] = [order_id]


    X[105] = 1
    price = 105
    order = Order(OrderSide.SELL, price, 1, datetime.datetime.now(), ORDER_GENERATOR_TRADER)
    order_id = exchange.add_limit_order(order)
    orders[order_id] = order
    prices[price] = [order_id]

    # # init #2
    # #2244500	200	2241100	287	2244900	100	2241000	77	2245000	5	2240900	100	2247500	10	2240000	10	2248000	250	2236500	2
    # buy_prices = [223, 222, 221, 220, 219]
    # sell_prices = [224, 225, 226, 227, 228]
    # buy_volumes = [200, 100, 5, 10, 250]
    # sell_volumes = [287, 77, 100, 10, 2]
    # for i in range(5):
    #     prices[buy_prices[i]] = []
    #     for j in range(buy_volumes[i]):
    #         price = buy_prices[i]
    #         X[price] -= 1
    #         order = Order(OrderSide.BUY, price, 1, datetime.datetime.now(), ORDER_GENERATOR_TRADER)
    #         order_id = exchange.add_limit_order(order)
    #         orders[order_id] = order
    #         prices[price].append(order_id)

    #     prices[sell_prices[i]] = []
    #     for j in range(sell_volumes[i]):
    #         price = sell_prices[i]
    #         X[price] += 1
    #         order = Order(OrderSide.SELL, price, 1, datetime.datetime.now(), ORDER_GENERATOR_TRADER)
    #         order_id = exchange.add_limit_order(order)
    #         orders[order_id] = order
    #         prices[price].append(order_id)


    X, orders, prices, mid_prices = simulate_n_seconds(X, orders, prices, exchange, time, n)
    print(list(X)[:500])


    plt.plot(mid_prices)
    plt.show()