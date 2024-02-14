from enum import Enum
import datetime



exchange_min_price = 1
exchange_max_price = 1000
# to avoid floting point error, it is suggested 
# to use int values for the ticksize
ticksize = 1



class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"



class Order:
    def __init__(self, side: OrderSide, price: int, quantity: int, time: datetime.datetime, trader_id: int) -> None:
        self.id = None
        self.side = side
        self.price = price
        self.quantity = quantity
        self.time = time
        self.trader_id = trader_id



class OrderBookSideI:

    def add_order(self, order: Order) -> None:
        pass

    def cancel_order(self, order_id: int, trader_id: int) -> None:
        pass

    def match_order(self) -> tuple[int, int]:
        pass



class OrderBook:

    def __init__(self, buy_side: OrderBookSideI, sell_side: OrderBookSideI) -> None:
        self.buy_side = buy_side
        self.sell_side = sell_side
        self.next_order_id = 0



class Exchange(OrderBook):

    def __init__(self, buy_side: OrderBookSideI, sell_side: OrderBookSideI):
        super().__init__(buy_side, sell_side)
        self.traders = {}
        self.traders_side = {}

    def add_order(self, order: Order) -> str | int:
        
        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"
        
        # only one active order for each trader
        if order.trader_id in self.traders:
            # cancel old order before adding the new one
            self.cancel_order(self.traders[order.trader_id], order.trader_id)
            # self.traders.pop(order.trader_id)
            # self.traders_side.pop((order.trader_id, OrderSide.BUY), None)
            # self.traders_side.pop((order.trader_id, OrderSide.SELL), None)

        order.id = self.next_order_id
        self.next_order_id += 1

        if order.side == OrderSide.BUY:
            if self.sell_side.best_price != None and order.price >= self.sell_side.best_price: # market order
                order.price = self.sell_side.best_price
                counterparty_id, order_id = self.sell_side.match_order()

                self.traders.pop(counterparty_id)
                self.traders_side.pop((counterparty_id, OrderSide.SELL))

                return "trade matched"
                # notify couterparty about a matched trade
            else:                                                                              # limit order
                self.buy_side.add_order(order)
        elif order.side == OrderSide.SELL:
            if self.buy_side.best_price != None and order.price <= self.buy_side.best_price:   # market order
                order.price = self.buy_side.best_price
                counterparty_id, order_id = self.buy_side.match_order()

                self.traders.pop(counterparty_id)
                self.traders_side.pop((counterparty_id, OrderSide.BUY))

                return "trade matched"
                # notify couterparty about a matched trade
            else:                                                                              # limit order
                self.sell_side.add_order(order)
        
        self.traders[order.trader_id] = order.id
        self.traders_side[(order.trader_id, order.side)] = order.id
        return order.id
                

    def add_market_order(self, order: Order) -> str:

        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"

        # only one active order for each trader
        if order.trader_id in self.traders:
            # cancel old order before adding the new one
            self.cancel_order(self.traders[order.trader_id], order.trader_id)
            # self.traders.pop(order.trader_id)
            # self.traders_side.pop((order.trader_id, OrderSide.BUY), None)
            # self.traders_side.pop((order.trader_id, OrderSide.SELL), None)

        order.id = self.next_order_id
        self.next_order_id += 1

        if order.side == OrderSide.BUY:
            order.price = self.sell_side.best_price
            counterparty_id, order_id = self.sell_side.match_order()

            self.traders.pop(counterparty_id)
            self.traders_side.pop((counterparty_id, OrderSide.SELL))

            return "trade matched"
            # notify couterparty about a matched trade
        else:
            order.price = self.buy_side.best_price
            counterparty_id, order_id = self.buy_side.match_order()

            self.traders.pop(counterparty_id)
            self.traders_side.pop((counterparty_id, OrderSide.BUY))

            return "trade matched"
            # notify couterparty about a matched trade


    def add_limit_order(self, order: Order) -> str | int:

        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"
        
        # only one active order for each trader
        if order.trader_id in self.traders:
            # cancel old order before adding the new one
            self.cancel_order(self.traders[order.trader_id], order.trader_id)
            # self.traders.pop(order.trader_id)
            # self.traders_side.pop((order.trader_id, OrderSide.BUY), None)
            # self.traders_side.pop((order.trader_id, OrderSide.SELL), None)

        order.id = self.next_order_id
        self.next_order_id += 1

        if order.side == OrderSide.BUY:
            self.buy_side.add_order(order)
        else:
            self.sell_side.add_order(order)
        
        self.traders[order.trader_id] = order.id
        self.traders_side[(order.trader_id, order.side)] = order.id
        return order.id


    def cancel_order(self, order_id: int, trader_id: int) -> str | None:

        # TODO: add dict of orders (trader_id -> list of order_ids)
        # TODO: check trader id when cancelling order
        # if trader_id != self.trader_orders[order_id]: sau not in pt mai multe trade-uri
        #     raise Exception("Trader id does not match order id") # notify trader invalid action
        
        if trader_id not in self.traders:
            return "trader does not exist"

        if order_id != self.traders[trader_id]:
            return "trader id does not match order id"

        if (trader_id, OrderSide.BUY) in self.traders_side:
            self.buy_side.cancel_order(order_id, trader_id)
            self.traders_side.pop((trader_id, OrderSide.BUY))
        elif (trader_id, OrderSide.SELL) in self.traders_side:
            self.sell_side.cancel_order(order_id, trader_id)
            self.traders_side.pop((trader_id, OrderSide.SELL))
        # else:
        #     return "order does not exist"

        self.traders.pop(trader_id)


    def get_best_price(self, side: OrderSide) -> int:
        if side == OrderSide.BUY:
            return self.buy_side.best_price
        else:
            return self.sell_side.best_price