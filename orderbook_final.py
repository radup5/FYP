from exchange_extended import Order, OrderSide, OrderBookSideInterface
from config import *



# OrderNode objects used to create the Double-Linked List
class OrderNode:

    def __init__(self, order: Order) -> None:
        self.order = order
        
        self.prev = None
        self.next = None



class PriceLevel:

    def __init__(self, price: int) -> None:
        self.price = price
        self.quantity = 0

        self.head_order_node = None
        self.tail_order_node = None



class OrderBookSide(OrderBookSideInterface):

    def __init__(self, side: OrderSide) -> None:

        self.side = side
        # each index in the limit_order_book list corresponds to a price level
        self.limit_order_book = [None] * ((EXCHANGE_MAX_PRICE - EXCHANGE_MIN_PRICE) // TICKSIZE + 1)
        self.best_price = None

        # id -> OrderNode
        self.order_nodes = {}

    def __price_to_index(self, price: int) -> int:
        return (price - EXCHANGE_MIN_PRICE) // TICKSIZE

    def add_order(self, order: Order) -> None:
        # get index in limit_order_book
        index = self.__price_to_index(order.price)

        # if there is no order at this price
        if self.limit_order_book[index] is None:

            # create a new PriceLevel
            newPriceLevel = PriceLevel(order.price)
            newPriceLevel.quantity += order.quantity
            self.limit_order_book[index] = newPriceLevel

            # create an OrderNode and add it to the double-linked list (empty)
            newOrderNode = OrderNode(order)
            self.order_nodes[order.id] = newOrderNode
            newPriceLevel.head_order_node = newOrderNode
            newPriceLevel.tail_order_node = newOrderNode

            # update best price
            if self.side == OrderSide.BUY:
                if self.best_price is None or self.best_price < order.price:
                    self.best_price = order.price
            elif self.side == OrderSide.SELL:
                if self.best_price is None or self.best_price > order.price:
                    self.best_price = order.price

        else:
            # create an OrderNode and add it to the double-linked list
            newOrderNode = OrderNode(order)
            self.order_nodes[order.id] = newOrderNode
            
            priceLevel = self.limit_order_book[index]
            priceLevel.quantity += order.quantity
            priceLevel.tail_order_node.next = newOrderNode
            newOrderNode.prev = priceLevel.tail_order_node
            priceLevel.tail_order_node = newOrderNode
    
    def __next_best_price(self, index: int) -> int | None:
        if self.side == OrderSide.BUY:
            while index >= 0:
                if self.limit_order_book[index] is not None:
                    return self.limit_order_book[index].price
                index -= 1
        elif self.side == OrderSide.SELL:
            while index < len(self.limit_order_book):
                if self.limit_order_book[index] is not None:
                    return self.limit_order_book[index].price
                index += 1
        return None

    def cancel_order(self, order_id: int, trader_id: int) -> None:
        # get the corresponding OrderNode
        orderNode = self.order_nodes[order_id]
        order = orderNode.order

        index = self.__price_to_index(order.price)
        priceLevel = self.limit_order_book[index]
        priceLevel.quantity -= order.quantity
        # if the order is the only one at this price level
        if priceLevel.quantity == 0:

            if priceLevel.head_order_node is not priceLevel.tail_order_node:
                raise RuntimeError("Wrong priceLevel linked list (cancel order)")
            
            self.limit_order_book[index] = None
            if self.best_price == order.price:
                self.best_price = self.__next_best_price(index)
            del priceLevel
        else:
            if priceLevel.head_order_node is orderNode:

                if orderNode.prev is not None:
                    raise RuntimeError("Wrong head node in priceLevel linked list (cancel order)")
                
                # remove the first node (head)
                priceLevel.head_order_node = orderNode.next
                orderNode.next.prev = None
            elif priceLevel.tail_order_node is orderNode:
                
                if orderNode.next is not None:
                    raise RuntimeError("Wrong tail node in priceLevel linked list (cancel order)")
                
                # remove the last node (tail)
                priceLevel.tail_order_node = orderNode.prev
                orderNode.prev.next = None
            else:

                if orderNode.prev is None or orderNode.next is None:
                    raise RuntimeError("Wrong node in priceLevel linked list (cancel order)")

                # remove node
                orderNode.prev.next = orderNode.next
                orderNode.next.prev = orderNode.prev

        self.order_nodes.pop(order_id)
        del orderNode
        del order

    def match_order(self) -> tuple[int, int]:
        price = self.best_price
        index = self.__price_to_index(price)
        matchingPriceLevel = self.limit_order_book[index]
        matchingOrderNode = matchingPriceLevel.head_order_node
        matchingOrder = matchingOrderNode.order
        counterparty_id = matchingOrder.trader_id
        order_id = matchingOrder.id
        quantity = 1
        matchingPriceLevel.quantity -= quantity

        if matchingPriceLevel.quantity == 0:

            if matchingPriceLevel.head_order_node is not matchingPriceLevel.tail_order_node:
                raise RuntimeError("Wrong priceLevel linked list (match order)")

            self.limit_order_book[index] = None
            self.best_price = self.__next_best_price(index)
            del matchingPriceLevel
        else:

            if matchingOrderNode.prev is not None:
                raise RuntimeError("Wrong head node in priceLevel linked list (match order)")
            
            # remove the first node (head)
            matchingPriceLevel.head_order_node = matchingOrderNode.next
            matchingOrderNode.next.prev = None

        self.order_nodes.pop(matchingOrder.id)
        del matchingOrderNode
        del matchingOrder
        return counterparty_id, order_id