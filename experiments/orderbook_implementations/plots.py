import matplotlib.pyplot as plt

# 10 traders

# 1k, 10k, 50k, 100k
orders = [1000, 10000, 50000, 100000]

exchange1 = [0.008, 0.068, 0.29, 0.55]
exchange2 = [0.004, 0.035, 0.14, 0.27]
exchange3 = [0.005, 0.044, 0.17, 0.33]

# plt.scatter(orders, exchange1, color='r', marker='.')
# plt.scatter(orders, exchange2, color='g', marker='x')
# plt.scatter(orders, exchange3, color='b', marker='s')
# plt.xlabel("orders")
# plt.ylabel("time(s)")
# plt.legend(["#1", "#2", "BSE"])
# plt.show()


# 100 traders

exchange1 = [0.005, 0.051, 0.20, 0.39]
exchange2 = [0.004, 0.034, 0.14, 0.26]
exchange3 = [0.008, 0.070, 0.29, 0.57]

# plt.scatter(orders, exchange1, color='r', marker='.')
# plt.scatter(orders, exchange2, color='g', marker='x')
# plt.scatter(orders, exchange3, color='b', marker='s')
# plt.xlabel("orders")
# plt.ylabel("time(s)")
# plt.legend(["#1", "#2", "BSE"])
# plt.show()

# 1000 traders

exchange1 = [0.005, 0.041, 0.17, 0.33]
exchange2 = [0.004, 0.036, 0.15, 0.28]
exchange3 = [0.017, 0.30, 1.58, 3.21]

plt.scatter(orders, exchange1, color='r', marker='.')
plt.scatter(orders, exchange2, color='g', marker='x')
plt.scatter(orders, exchange3, color='b', marker='s')
plt.xlabel("orders")
plt.ylabel("time(s)")
plt.legend(["#1", "#2", "BSE"])
plt.show()