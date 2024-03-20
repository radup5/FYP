from exchange import Exchange, OrderSide, Order
import orderbook_lists
import orderbook_heaps
import orderbook_benchmark
import datetime
import random
import time
import matplotlib.pyplot as plt


def setup_exchanges():
    exchange = [None, None, None]
    buy_side = orderbook_lists.OrderBookSide(OrderSide.BUY)
    sell_side = orderbook_lists.OrderBookSide(OrderSide.SELL)
    exchange[0] = Exchange(buy_side, sell_side)
    buy_side = orderbook_heaps.OrderBookSide(OrderSide.BUY)
    sell_side = orderbook_heaps.OrderBookSide(OrderSide.SELL)
    exchange[1] = Exchange(buy_side, sell_side)
    buy_side = orderbook_benchmark.OrderBookSide(OrderSide.BUY)
    sell_side = orderbook_benchmark.OrderBookSide(OrderSide.SELL)
    exchange[2] = Exchange(buy_side, sell_side)

    return exchange


def run_simulation(type, operations, traders, runs):
    exchange = setup_exchanges()

    avg_time = 0
    for _ in range(runs):

        start = time.time()

        for _ in range(operations):
            action_type = random.randint(1, 5)
            if action_type <= 4 or len(exchange[0].traders) == 0: # add order
                side = random.randint(0, 1)
                side = OrderSide.BUY if side == 0 else OrderSide.SELL
                price = random.randint(1, 1000)
                trader_id = random.randint(1, traders)
                order = Order(side=side, price=price, quantity=1, time=datetime.datetime.now(), trader_id=trader_id)
                exchange[type].add_order(order)
            else:                                                 # cancel order
                index = random.randint(0, len(exchange[0].traders) - 1)
                trader_id = list(exchange[0].traders)[index]
                order_id = exchange[0].traders[trader_id]
                exchange[type].cancel_order(order_id, trader_id)


        end = time.time()

        avg_time += (end - start)
        
    return avg_time / runs


def plot_simulations():

    operations = [1000, 10000, 50000, 100000]
    traders = 100
    runs = 3
    times = [[], [], []]

    for type in range(3):
        for op in operations:
            avg_time = run_simulation(type, op, traders, runs)
            times[type].append(avg_time)
    
    plt.scatter(operations, times[0], color='r', marker='.')
    plt.scatter(operations, times[1], color='g', marker='x')
    plt.scatter(operations, times[2], color='b', marker='s')
    plt.xlabel("actions")
    plt.ylabel("time(s)")
    plt.legend(["#1", "#2", "BSE"])
    plt.show()

plot_simulations()