import datetime
import pytest
import orderbook_lists as e
from unittest.mock import Mock
from config import *


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
    buy_side = e.OrderBookSide(e.OrderSide.BUY)
    sell_side = e.OrderBookSide(e.OrderSide.SELL)
    return e.OrderBook(buy_side, sell_side)



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



def test_add_single_order_limit_order_book(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    assert order_book_side.limit_order_book[50].price == 50
    assert order_book_side.limit_order_book[50].quantity == 1



def test_add_single_order_linked_list(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    order_node = order_book_side.order_nodes[0]

    assert order_node.order is order
    assert order_node.prev is None
    assert order_node.next is None

    assert order_book_side.limit_order_book[50].head_order_node is order_node
    assert order_book_side.limit_order_book[50].tail_order_node is order_node



def test_add_multiple_orders_same_price_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    assert order_book_side.best_price == None

    prices = [50, 50, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        assert order_book_side.best_price == 50



def test_add_multiple_orders_same_price_limit_order_book(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 50, 50]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        assert order_book_side.limit_order_book[50].price == 50
        assert order_book_side.limit_order_book[50].quantity == i + 1



def test_add_multiple_orders_same_price_linked_list(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 50, 50]
    order_nodes = [None, None, None, None]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
        order_nodes[i] = order_book_side.order_nodes[i]

        assert order_nodes[i].order is order
    
    # check double-linked list
    assert order_nodes[0].prev is None
    assert order_nodes[0].next is order_nodes[1]
    assert order_nodes[1].prev is order_nodes[0]
    assert order_nodes[1].next is order_nodes[2]
    assert order_nodes[2].prev is order_nodes[1]
    assert order_nodes[2].next is None

    assert order_book_side.limit_order_book[50].head_order_node is order_nodes[0]
    assert order_book_side.limit_order_book[50].tail_order_node is order_nodes[2]



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



def test_add_multiple_orders_different_price_limit_order_book(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    quantity = [1, 1, 2]
    for i, price in enumerate([50, 51, 52]):
        assert order_book_side.limit_order_book[price].price == price
        assert order_book_side.limit_order_book[price].quantity == quantity[i]



def test_add_multiple_orders_different_price_linked_list(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52]
    order_nodes = [None, None, None, None]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)

        order_nodes[i] = order_book_side.order_nodes[i]

        assert order_nodes[i].order is order
    
    # check double-linked lists
    assert order_nodes[0].prev is None
    assert order_nodes[0].next is None
    assert order_nodes[1].prev is None
    assert order_nodes[1].next is order_nodes[3]
    assert order_nodes[2].prev is None
    assert order_nodes[2].next is None
    assert order_nodes[3].prev is order_nodes[1]
    assert order_nodes[3].next is None

    assert order_book_side.limit_order_book[50].head_order_node is order_nodes[0]
    assert order_book_side.limit_order_book[50].tail_order_node is order_nodes[0]
    assert order_book_side.limit_order_book[51].head_order_node is order_nodes[2]
    assert order_book_side.limit_order_book[51].tail_order_node is order_nodes[2]
    assert order_book_side.limit_order_book[52].head_order_node is order_nodes[1]
    assert order_book_side.limit_order_book[52].tail_order_node is order_nodes[3]



def test_add_multiple_orders_different_price_ticksize(mocker, empty_OrderBookSide):
    mocker.patch("config.TICKSIZE", new=2)
    order_book_side = empty_OrderBookSide

    prices = [48, 52, 50, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    quantity = [1, 1, 2]
    for i, price in enumerate([48, 50, 52]):
        assert order_book_side.limit_order_book[price // TICKSIZE].price == price
        assert order_book_side.limit_order_book[price // TICKSIZE].quantity == quantity[i]



def test_cancel_single_order_best_price(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    order_book_side.cancel_order(order_id=0, trader_id=1)

    assert order_book_side.best_price == None



def test_cancel_single_order_limit_order_book(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    order = e.Order(side=e.OrderSide.BUY, price=50, quantity=1, time=datetime.datetime.now(), trader_id=1)
    order.id = 0
    order_book_side.add_order(order)

    order_book_side.cancel_order(order_id=0, trader_id=1)

    assert order_book_side.limit_order_book[50] is None
    assert order.id not in order_book_side.order_nodes



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



def test_cancel_multiple_orders_limit_order_book(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52, 51, 52]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)
    
    cancelled_orders = [0, 3, 4]
    for order_id in cancelled_orders:
        order_book_side.cancel_order(order_id=order_id, trader_id=order_id+1)

        assert order_id not in order_book_side.order_nodes

    quantity = [1, 2]
    for i, price in enumerate([51, 52]):
        assert order_book_side.limit_order_book[price].price == price
        assert order_book_side.limit_order_book[price].quantity == quantity[i]
    assert order_book_side.limit_order_book[50] is None



def test_cancel_multiple_orders_linked_lists(empty_OrderBookSide):
    order_book_side = empty_OrderBookSide

    prices = [50, 52, 51, 52, 51, 52]
    order_nodes = [None, None, None, None, None, None]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book_side.add_order(order)

        order_nodes[i] = order_book_side.order_nodes[i]
    
    cancelled_orders = [0, 3, 4]
    for order_id in cancelled_orders:
        order_book_side.cancel_order(order_id=order_id, trader_id=order_id+1)
    
    # check double-linked lists
    assert order_nodes[2].prev is None
    assert order_nodes[2].next is None
    assert order_nodes[1].prev is None
    assert order_nodes[1].next is order_nodes[5]
    assert order_nodes[5].prev is order_nodes[1]
    assert order_nodes[5].next is None

    assert order_book_side.limit_order_book[51].head_order_node is order_nodes[2]
    assert order_book_side.limit_order_book[51].tail_order_node is order_nodes[2]
    assert order_book_side.limit_order_book[52].head_order_node is order_nodes[1]
    assert order_book_side.limit_order_book[52].tail_order_node is order_nodes[5]



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

    assert order_book.buy_side.limit_order_book[50] is None
    assert order.id not in order_book.buy_side.order_nodes



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

    matched_orders = [0, 2, 4]
    for order_id in matched_orders:
        assert order_id not in order_book.buy_side.order_nodes

    quantity = [2, 1]
    for i, price in enumerate([50, 51]):
        assert order_book.buy_side.limit_order_book[price].price == price
        assert order_book.buy_side.limit_order_book[price].quantity == quantity[i]
    assert order_book.buy_side.limit_order_book[52] is None



def test_match_multiple_orders_linked_lists(empty_OrderBook):
    order_book = empty_OrderBook

    prices = [51, 50, 51, 51, 52, 50]
    order_nodes = [None, None, None, None, None, None]
    for i in range(len(prices)):
        order = e.Order(side=e.OrderSide.BUY, price=prices[i], quantity=1, time=datetime.datetime.now(), trader_id=i+1)
        order.id = i
        order_book.buy_side.add_order(order)

        order_nodes[i] = order_book.buy_side.order_nodes[i]
    
    for i in range(3):
        order_book.buy_side.match_order()
    
    # check double-linked lists
    assert order_nodes[3].prev is None
    assert order_nodes[3].next is None
    assert order_nodes[1].prev is None
    assert order_nodes[1].next is order_nodes[5]
    assert order_nodes[5].prev is order_nodes[1]
    assert order_nodes[5].next is None

    assert order_book.buy_side.limit_order_book[50].head_order_node is order_nodes[1]
    assert order_book.buy_side.limit_order_book[50].tail_order_node is order_nodes[5]
    assert order_book.buy_side.limit_order_book[51].head_order_node is order_nodes[3]
    assert order_book.buy_side.limit_order_book[51].tail_order_node is order_nodes[3]