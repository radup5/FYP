from exchange import Order, OrderSide, OrderBook, OrderBookSideInterface
from heapq import heappush, heappop, heapify
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
        # heap including all the prices
        self.price_heap = []
        # first element from heap
        self.best_price = None
        
        # id -> OrderNode
        self.order_nodes = {}

        # price -> PriceLevel
        self.price_levels = {}

    def add_order(self, order: Order) -> None:
        # if there is no order at this price
        if order.price not in self.price_levels:

            # create a new PriceLevel
            newPriceLevel = PriceLevel(order.price)
            newPriceLevel.quantity += order.quantity
            self.price_levels[order.price] = newPriceLevel
            if self.side == OrderSide.BUY:
                heappush(self.price_heap, -order.price)
            else:
                heappush(self.price_heap, order.price)

            # create an OrderNode and add it to the double-linked list (empty)
            newOrderNode = OrderNode(order)
            self.order_nodes[order.id] = newOrderNode
            newPriceLevel.head_order_node = newOrderNode
            newPriceLevel.tail_order_node = newOrderNode

            # update best price
            if len(self.price_heap) > 0:
                self.best_price = abs(self.price_heap[0])

        else:
            # create an OrderNode and add it to the double-linked list
            newOrderNode = OrderNode(order)
            self.order_nodes[order.id] = newOrderNode
            
            priceLevel = self.price_levels[order.price]
            priceLevel.quantity += order.quantity
            priceLevel.tail_order_node.next = newOrderNode
            newOrderNode.prev = priceLevel.tail_order_node
            priceLevel.tail_order_node = newOrderNode
    
    def cancel_order(self, order_id: int, trader_id: int) -> None:
        # get the corresponding OrderNode
        orderNode = self.order_nodes[order_id]
        order = orderNode.order
        priceLevel = self.price_levels[order.price]
        priceLevel.quantity -= order.quantity

        # if the order is the only one at this price level
        if priceLevel.quantity == 0:

            if priceLevel.head_order_node is not priceLevel.tail_order_node:
                raise RuntimeError("Wrong priceLevel linked list (cancel order)")
            
            if abs(self.price_heap[0]) == order.price:
                heappop(self.price_heap)
                if len(self.price_heap) > 0:
                    self.best_price = abs(self.price_heap[0])
                else:
                    self.best_price = None
            else:
                # TODO: implement heap class for O(log n) instead of O(n)
                sign = -1 if self.side == OrderSide.BUY else 1
                self.price_heap.remove(sign * order.price)
                heapify(self.price_heap)

            self.price_levels.pop(order.price)
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

                orderNode.prev.next = orderNode.next
                orderNode.next.prev = orderNode.prev

        self.order_nodes.pop(order_id)
        del orderNode
        del order

    def match_order(self) -> tuple[int, int]:
        price = self.best_price
        matchingPriceLevel = self.price_levels[price]
        matchingOrderNode = matchingPriceLevel.head_order_node
        matchingOrder = matchingOrderNode.order
        counterparty_id = matchingOrder.trader_id
        order_id = matchingOrder.id
        quantity = 1
        matchingPriceLevel.quantity -= quantity

        if matchingPriceLevel.quantity == 0:

            if matchingPriceLevel.head_order_node is not matchingPriceLevel.tail_order_node:
                raise RuntimeError("Wrong priceLevel linked list (match order)")

            heappop(self.price_heap)
            if len(self.price_heap) > 0:
                self.best_price = abs(self.price_heap[0])
            else:
                self.best_price = None

            self.price_levels.pop(price)
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