from enum import Enum
import datetime



exchange_min_price = 0
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

    # TODO: update return for match_order (for order generator)
    def add_order(self, order: Order) -> str | int:
        
        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"
        
        order.id = self.next_order_id
        self.next_order_id += 1

        if order.side == OrderSide.BUY:
            if self.sell_side.best_price != None and order.price >= self.sell_side.best_price: # market order
                order.price = self.sell_side.best_price
                counterparty_id, order_id = self.sell_side.match_order()

                self.traders[counterparty_id].remove(order_id)
                self.traders_side[(counterparty_id, OrderSide.SELL)].remove(order_id)

                return "trade matched"
                # notify couterparty about a matched trade
            else:                                                                              # limit order
                self.buy_side.add_order(order)
        elif order.side == OrderSide.SELL:
            if self.buy_side.best_price != None and order.price <= self.buy_side.best_price:   # market order
                order.price = self.buy_side.best_price
                counterparty_id, order_id = self.buy_side.match_order()

                self.traders[counterparty_id].remove(order_id)
                self.traders_side[(counterparty_id, OrderSide.BUY)].remove(order_id)

                return "trade matched"
                # notify couterparty about a matched trade
            else:                                                                              # limit order
                self.sell_side.add_order(order)
        
        if order.trader_id in self.traders:
            self.traders[order.trader_id].append(order.id)
        else:
            self.traders[order.trader_id] = [order.id]
        if (order.trader_id, order.side) in self.traders_side:
            self.traders_side[(order.trader_id, order.side)].append(order.id)
        else:
            self.traders_side[(order.trader_id, order.side)] = [order.id]

        return order.id
                

    def add_market_order(self, order: Order) -> str | int:

        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"

        order.id = self.next_order_id
        self.next_order_id += 1

        if order.side == OrderSide.BUY:
            order.price = self.sell_side.best_price
            counterparty_id, order_id = self.sell_side.match_order()

            self.traders[counterparty_id].remove(order_id)
            self.traders_side[(counterparty_id, OrderSide.SELL)].remove(order_id)

            # if trader is the order generator trader, return counterparty_id
            if order.trader_id == 0:
                return counterparty_id, order_id
            return "trade matched"
            # notify couterparty about a matched trade
        else:
            order.price = self.buy_side.best_price
            counterparty_id, order_id = self.buy_side.match_order()

            self.traders[counterparty_id].remove(order_id)
            self.traders_side[(counterparty_id, OrderSide.BUY)].remove(order_id)

            # if trader is the order generator trader, return counterparty_id
            if order.trader_id == 0:
                return counterparty_id, order_id
            return "trade matched"
            # notify couterparty about a matched trade


    def add_limit_order(self, order: Order) -> str | int:

        if order.price % ticksize != 0:
            return "price not divisible by the ticksize"
        if order.price < exchange_min_price or order.price > exchange_max_price:
            return "price out of bound"
        
        order.id = self.next_order_id
        self.next_order_id += 1

        # TODO: elif instead of else
        if order.side == OrderSide.BUY:
            self.buy_side.add_order(order)
        else:
            self.sell_side.add_order(order)
        
        if order.trader_id in self.traders:
            self.traders[order.trader_id].append(order.id)
        else:
            self.traders[order.trader_id] = [order.id]
        if (order.trader_id, order.side) in self.traders_side:
            self.traders_side[(order.trader_id, order.side)].append(order.id)
        else:
            self.traders_side[(order.trader_id, order.side)] = [order.id]

        return order.id


    def cancel_order(self, order_id: int, trader_id: int) -> str | None:

        if trader_id not in self.traders:
            return "trader does not exist"

        if order_id not in self.traders[trader_id]:
            return "trader id does not match order id"

        if (trader_id, OrderSide.BUY) in self.traders_side and order_id in self.traders_side[(trader_id, OrderSide.BUY)]:
            self.buy_side.cancel_order(order_id, trader_id)
            self.traders_side[(trader_id, OrderSide.BUY)].remove(order_id)
        elif (trader_id, OrderSide.SELL) in self.traders_side and order_id in self.traders_side[(trader_id, OrderSide.SELL)]:
            self.sell_side.cancel_order(order_id, trader_id)
            self.traders_side[(trader_id, OrderSide.SELL)].remove(order_id)
        # else:
        #     return "order does not exist"

        self.traders[trader_id].remove(order_id)


    def get_best_price(self, side: OrderSide) -> int:
        if side == OrderSide.BUY:
            return self.buy_side.best_price
        else:
            return self.sell_side.best_price