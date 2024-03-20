import numpy as np
import datetime

from exchange_extended import Exchange, OrderSide, Order
import orderbook_final



# TODO: limit position, limit cash (calculate money needed for all limit orders)


class Trader:

    def __init__(self, trader_id: int, cash: int, exchange: Exchange) -> None:
        self.trader_id = trader_id
        self.cash = cash
        self.initial_cash = cash
        self.exchange = exchange

        self.position = 0
        self.value = cash
        self.active_orders = {}
    

    def get_profit(self) -> int:
        mid_price = (self.exchange.buy_side.get_best_price() + self.exchange.sell_side.get_best_price()) // 2
        profit = self.cash + self.position * mid_price - self.initial_cash
        # TODO: self.value - self.initial_cash ?
        return profit
    

    def update_value(self) -> None:
        mid_price = (self.exchange.buy_side.get_best_price() + self.exchange.sell_side.get_best_price()) // 2
        self.value = self.cash + self.position * mid_price


    def __send_limit_order(self, side: OrderSide, price: int, time: datetime.datetime) -> None:
        order = Order(side, price, 1, time, self.trader_id)
        order_id = self.exchange.add_limit_order(order)
        self.active_orders[order_id] = order


    def __sent_market_order(self, side: OrderSide, time: datetime.datetime) -> None:
        if side == OrderSide.BUY:
            price = self.exchange.sell_side.get_best_price()
        else:
            price = self.exchange.buy_side.get_best_price()

        order = Order(side, price, 1, time, self.trader_id)
        self.exchange.add_market_order(order)

        if order.side == OrderSide.BUY:
            self.position += 1
            self.cash -= order.price
        else:
            self.position -= 1
            self.cash += order.price


    def __sent_cancel_order(self, order_id: int, time: datetime.datetime) -> None:
        if order_id in self.active_orders:
            self.exchange.cancel_order(order_id, self.trader_id)
            self.active_orders.pop(order_id)


    def matched_order_notification(self, order_id: int) -> None:
        order = self.active_orders[order_id]
        self.active_orders.pop(order_id)

        if order.side == OrderSide.BUY:
            self.position += 1
            self.cash -= order.price
        else:
            self.position -= 1
            self.cash += order.price

    
    def strategy(self, lob_state: np.ndarray, time: datetime.datetime) -> None:
        pass