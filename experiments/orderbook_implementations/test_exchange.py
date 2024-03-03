from exchange import Exchange, OrderBook, OrderSide, Order
import orderbook_lists
import orderbook_heaps
import orderbook_benchmark
import datetime
import random
import time
import pytest


@pytest.fixture
def empty_Exchanges():
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



def test_exchange(empty_Exchanges):
    exchange = empty_Exchanges

    for i in range(1000000):
        action_type = random.randint(0, 5)
        if action_type <= 4 or len(exchange[0].traders) == 0: # add order
            side = random.randint(0, 1)
            side = OrderSide.BUY if side == 0 else OrderSide.SELL
            price = random.randint(1, 1000)
            trader_id = random.randint(1, 1000)
            order = Order(side=side, price=price, quantity=1, time=datetime.datetime.now(), trader_id=trader_id)
            exchange[0].add_order(order)
            exchange[1].add_order(order)
            exchange[2].add_order(order)
        else:                                                 # cancel order
            index = random.randint(0, len(exchange[0].traders) - 1)
            trader_id = list(exchange[0].traders)[index]
            order_id = exchange[0].traders[trader_id]
            exchange[0].cancel_order(order_id, trader_id)
            exchange[1].cancel_order(order_id, trader_id)
            exchange[2].cancel_order(order_id, trader_id)
        
        assert exchange[0].get_best_price(OrderSide.BUY) == exchange[1].get_best_price(OrderSide.BUY)
        assert exchange[0].get_best_price(OrderSide.BUY) == exchange[2].get_best_price(OrderSide.BUY)
        assert exchange[1].get_best_price(OrderSide.BUY) == exchange[2].get_best_price(OrderSide.BUY)

        assert exchange[0].get_best_price(OrderSide.SELL) == exchange[1].get_best_price(OrderSide.SELL)
        assert exchange[0].get_best_price(OrderSide.SELL) == exchange[2].get_best_price(OrderSide.SELL)
        assert exchange[1].get_best_price(OrderSide.SELL) == exchange[2].get_best_price(OrderSide.SELL)