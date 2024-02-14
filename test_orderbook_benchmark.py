import datetime
import pytest
import orderbook_benchmark as e
from unittest.mock import Mock



# @pytest.fixture
# def global_var():
#     pytest.exchange_min_price = 0
#     pytest.exchange_max_price = 100
#     pytest.ticksize = 1

@pytest.fixture
def empty_OrderBookSide():
    return e.OrderBookSide(e.OrderSide.BUY)

@pytest.fixture
def empty_OrderBook():
    return e.OrderBook()



def test_Order_initialization():
    # tests that Order initialisation works as expected
    side = e.OrderSide.BUY
    price = 50
    quantity = 1
    time = datetime.datetime.now()
    trader_id = 1

    order = e.Order(side, price, quantity, time, trader_id)

    assert order.side == side
    assert order.price == price
    assert order.quantity == quantity
    assert order.time == time
    assert order.trader_id == trader_id



def test_add_single_order_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    assert order_book_side.best_price == None

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    assert order_book_side.best_price == 50



def test_add_single_order_lob(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    assert order_book_side.lob[50][0] == 1



def test_add_multiple_orders_same_price_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    assert order_book_side.best_price == None

    prices = [50, 50, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        assert order_book_side.best_price == 50



def test_add_multiple_orders_same_price_lob(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 50, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        assert order_book_side.lob[50][0] == i + 1



def test_add_multiple_orders_different_price_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    assert order_book_side.best_price == None

    prices = [50, 52, 51, 52]
    best_price = [50, 52, 52, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        assert order_book_side.best_price == best_price[i]



def test_add_multiple_orders_different_price_lob(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    quantity = [1, 1, 2]
    for i, price in enumerate([50, 51, 52]):
        assert order_book_side.lob[price][0] == quantity[i]



def test_cancel_single_order_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    order_book_side.cancel_order(order_id=0, trader_id=1)

    assert order_book_side.best_price == None



def test_cancel_single_order_lob(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    order_book_side.cancel_order(order_id=0, trader_id=1)

    assert order.price not in order_book_side.lob



def test_cancel_multiple_orders_best_price1(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52, 51]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    best_price = [52, 51, 51]
    cancelled_orders = [1, 3, 2]
    for i, order_id in enumerate(cancelled_orders):
        order_book_side.cancel_order(order_id=order_id, trader_id=order_id+1)

        assert order_book_side.best_price == best_price[i]



def test_cancel_multiple_orders_best_price2(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52, 51, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    best_price = [52, 52, 52]
    cancelled_orders = [0, 3, 4]
    for i, order_id in enumerate(cancelled_orders):
        order_book_side.cancel_order(order_id=order_id, trader_id=order_id+1)

        assert order_book_side.best_price == best_price[i]



def test_cancel_multiple_orders_lob(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52, 51, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    cancelled_orders = [0, 3, 4]
    for order_id in cancelled_orders:
        order_book_side.cancel_order(order_id=order_id, trader_id=order_id+1)

    quantity = [1, 2]
    for i, price in enumerate([51, 52]):
        order_book_side.lob[price][0] == quantity[i]
    assert 50 not in order_book_side.lob



def test_match_single_order_best_price(empty_OrderBook):
    order_book = empty_OrderBook

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book.buy_side.add_order(order)

    assert order_book.buy_side.best_price == 50

    order_book.buy_side.match_order()

    assert order_book.buy_side.best_price == None



def test_match_single_order_limit_order_book(empty_OrderBook):
    order_book = empty_OrderBook

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book.buy_side.add_order(order)

    order_book.buy_side.match_order()

    assert order.price not in order_book.buy_side.lob



def test_match_multiple_orders_best_price(empty_OrderBook):
    order_book = empty_OrderBook

    prices = [51, 50, 51, 51, 52, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book.buy_side.add_order(order)
    
    best_price = [51, 51, 51]
    for i in range(3):
        order_book.buy_side.match_order()

        assert order_book.buy_side.best_price == best_price[i]



def test_match_multiple_orders_limit_order_book(empty_OrderBook):
    order_book = empty_OrderBook

    prices = [51, 50, 51, 51, 52, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book.buy_side.add_order(order)
    
    for i in range(3):
        order_book.buy_side.match_order()

    quantity = [2, 1]
    for i, price in enumerate([50, 51]):
        assert order_book.buy_side.lob[price][0] == quantity[i]
    assert 52 not in order_book.buy_side.lob