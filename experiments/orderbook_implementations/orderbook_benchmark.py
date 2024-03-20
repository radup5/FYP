from exchange import Order, OrderSide, OrderBook, OrderBookSideInterface



class OrderBookSide(OrderBookSideInterface):

    def __init__(self, side: OrderSide) -> None:
        self.side = side
        self.orders = {}
        self.lob = {}
        self.lob_anonymized = []
        self.best_price = None

    def anonymize_lob(self) -> None:
        self.lob_anonymized = []
        for price in sorted(self.lob):
            quantity = self.lob[price][0]
            self.lob_anonymized.append([price, quantity])

    def build_lob(self) -> None:
        self.lob = {}
        for trader_id in self.orders:
            order = self.orders[trader_id]
            price = order.price
            if price in self.lob:
                quantity = self.lob[price][0]
                orders = self.lob[price][1]
                orders.append([order.time, order.quantity, order.trader_id, order.id])
                self.lob[price] = [quantity + order.quantity, orders]
            else:
                self.lob[price] = [order.quantity, [[order.time, order.quantity, order.trader_id, order.id]]]
        
        self.anonymize_lob()

        if len(self.lob) > 0:
            if self.side == OrderSide.BUY:
                self.best_price = self.lob_anonymized[-1][0]
            else:
                self.best_price = self.lob_anonymized[0][0]
        else:
            self.best_price = None

    def add_order(self, order: Order) -> None:
        self.orders[order.trader_id] = order
        self.build_lob()
    
    def cancel_order(self, order_id: int, trader_id: int) -> None:
        if trader_id in self.orders:
            self.orders.pop(trader_id)
            self.build_lob()

    def match_order(self) -> tuple[int, int]:
        best_price_orders = self.lob[self.best_price]
        best_price_quantity = best_price_orders[0]
        counterparty_id = best_price_orders[1][0][2]
        order_id = best_price_orders[1][0][3]

        if best_price_quantity == 1:
            self.lob.pop(self.best_price)
            self.orders.pop(counterparty_id)

            if len(self.orders) > 0:
                if OrderSide.BUY:
                    self.best_price = max(self.lob.keys())
                else:
                    self.best_price = min(self.lob.keys())
            else:
                self.best_price = None
        else:
            self.lob[self.best_price] = [best_price_quantity - 1, best_price_orders[1][1:]]
            self.orders.pop(counterparty_id)
        
        self.build_lob()
        
        return counterparty_id, order_id