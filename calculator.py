from email import header
from statistics import multimode
from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity

from pathfinder import Route

import time
import sys
import pickle


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = "*" * filled_len + "-" * (bar_len - filled_len)

    sys.stdout.write("[%s] %s%s %s\r" % (bar, percents, "%", status))
    sys.stdout.flush()


# Create the ESI interface application and a client (currently a public client)
esi_app = EsiApp()
app = esi_app.get_latest_swagger

# Log into ESI for application perms
# security = EsiSecurity(
#     redirect_uri="http://localhost:65432/callback",
#     client_id="c6977cc398d94a4a966d2246e5c549e5",
#     secret_key="2GdfCPX8EjHJLkMLfikNoJ5Q1q6LlcP5jEh3qIQu",
#     header={
#         "User-Agent": "A simple calculator for my EVE trucker needs - simeonikh@gmail.com - https://github.com/KhanSimeoni/EVE-Trading-Tracker"
#     },
# )

# tokens = security.auth(
#     code="S9fAItDklM5CaUW3pcHgnAWDP3kodE8poZo_YgtVCmAF6g8tA3nyGh1G-CFXNGSA"
# )
# print(tokens)
# Load star system information from pickle file
print("pickling")

file = open("systems_data", "r+b")
systems_data = pickle.load(file)
file.close()

file = open("regions", "r+b")
all_regions = pickle.load(file)
file.close()

print("connecting to ESI")

client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={
        "User-Agent": "Something CCP can use to contact you and that define your app"
    },
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)

# Get market orders for a region


def getItemOrders(item_id, do_all_regions=True, regions=None):
    print("getting market orders")
    buy_information = []
    sell_information = []
    counter = 0
    total = len(all_regions)

    for region in all_regions:

        systems_request_buy = app.op["get_markets_region_id_orders"](
            region_id=region, order_type="buy", type_id=item_id
        )
        systems_request_sell = app.op["get_markets_region_id_orders"](
            region_id=region, order_type="sell", type_id=item_id
        )

        orders_buy = client.request(systems_request_buy)
        orders_sell = client.request(systems_request_sell)

        for order in orders_buy.data:
            buy_information.append(
                (
                    order.get("price"),
                    order.get("volume_remain"),
                    order.get("system_id"),
                    order.get("location_id"),
                )
            )

        for order in orders_sell.data:
            sell_information.append(
                (
                    order.get("price"),
                    order.get("volume_remain"),
                    order.get("system_id"),
                    order.get("location_id"),
                )
            )

        counter += 1

        buy_information.sort(None, True)
        sell_information.sort()
        buy_information = buy_information[0:19]
        sell_information = sell_information[0:19]

        progress(counter, total)

    print()
    return buy_information, sell_information


def multiRoute(order_info):
    end_system_request = app.op["get_universe_systems_system_id"](
        system_id=order_info[4][0]
    )
    start_system_request = app.op["get_universe_systems_system_id"](
        system_id=order_info[4][1]
    )
    start_system = client.request(start_system_request)
    end_system = client.request(end_system_request)

    end_constillation_request = app.op[
        "get_universe_constellations_constellation_id",
    ](constellation_id=end_system.data.get("constellation_id"))
    start_constillation_request = app.op[
        "get_universe_constellations_constellation_id",
    ](constellation_id=start_system.data.get("constellation_id"))
    start_constillation = client.request(start_constillation_request)
    end_constillation = client.request(end_constillation_request)

    page_num = 1
    end_orders = []
    start_orders = []
    error = False
    while not error:
        end_orders_request = app.op["get_markets_region_id_orders"](
            region_id=end_constillation.data.get("region_id"),
            order_type="sell",
            page=page_num,
        )
        start_orders_request = app.op["get_markets_region_id_orders"](
            region_id=start_constillation.data.get("region_id"),
            order_type="buy",
            page=page_num,
        )
        end_orders_temp = client.request(end_orders_request)
        start_orders_temp = client.request(start_orders_request)

        try:
            if end_orders_temp.data.get("error"):
                error = True
        except:
            pass

        for order in end_orders_temp.data:
            end_orders.append(order)
        for order in start_orders_temp.data:
            start_orders.append(order)

        page_num += 1

    region_end_orders = []
    region_start_orders = []
    for order in end_orders:

        try:
            if order.get("system_id") == order_info[4][0]:
                region_end_orders.append(order)
        except:
            pass

    for order in start_orders:

        try:
            if order.get("system_id") == order_info[4][1]:
                region_start_orders.append(order)
        except:
            pass

    end_orders_info = []
    start_orders_info = []

    for order in region_end_orders:
        end_orders_info.append(
            (order.get("price"), order.get("volume_remain"), order.get("type_id"))
        )
    for order in region_start_orders:
        start_orders_info.append(
            (order.get("price"), order.get("volume_remain"), order.get("type_id"))
        )

    end_orders_info = sorted(end_orders_info, key=lambda order: order[0] * order[1])
    end_orders_info = sorted(end_orders_info, key=lambda order: order[2])

    start_orders_info = sorted(
        start_orders_info, key=lambda order: order[0] * order[1], reverse=True
    )
    start_orders_info = sorted(start_orders_info, key=lambda order: order[2])

    new_orders = []
    while len(end_orders_info) > 0:
        st_order = end_orders_info[0]
        ed_order = start_orders_info[0]

        if st_order[2] == ed_order[2]:
            moveable_volume = min(st_order[1], st_order[1])
            profit = round(
                (ed_order[0] - st_order[0]) * moveable_volume,
            )

            new_orders.append((profit, st_order[2], st_order[1]))
            start_orders_info.pop(0)
            # print("same")

        else:
            if st_order[2] > ed_order[2]:
                start_orders_info.pop(0)
                # print("spop")

            elif st_order[2] < ed_order[2]:
                end_orders_info.pop(0)
                # print("epop")

            else:
                # print("what?")
                return

    new_orders.sort(key=lambda order: order[0], reverse=True)

    return new_orders


# Calculate the profit and other info from the found buy and sell orders
def profitCalculation(buy_info, sell_info):
    print("procesing")

    counter = 0
    percentage = 0
    total_counts = len(buy_info) * len(sell_info)

    progress(counter, total_counts)

    profits = []
    for buy_order in buy_info:
        for sell_order in sell_info:

            route_map = Route()
            route = route_map.findRoute(buy_order[2], sell_order[2])
            start_and_end = (sell_order[2], buy_order[2])

            if route:
                route_length = len(route)
            else:
                route_length = 0

            moveable_volume = min(buy_order[1], sell_order[1])
            profit = round(
                (buy_order[0] - sell_order[0]) * moveable_volume,
            )

            profits.append(
                (
                    profit,
                    route_length,
                    round(profit / route_length),
                    moveable_volume,
                    start_and_end,
                )
            )

            counter += 1
            progress(counter, total_counts)

        profits.sort(key=lambda order: order[0], reverse=True)

    return profits


def calculate(item_id):
    buy_info, sell_info = getItemOrders(item_id)
    profit = profitCalculation(buy_info, sell_info)
    profit.sort(None, True)
    # other_sales = multiRoute(profit[0][4][0], profit[0][4][0])
    top_ten = profit[0:9]
    return top_ten


# Manual scan
standup_light_guided_bomb = 47816
gleam_medium_frequency_crystal = 12826

# slgb_top_ten = calculate(standup_light_guided_bomb)

# print()
# print("standup_light_guided_bomb")
# print(slgb_top_ten)

gmfc_top_ten = calculate(gleam_medium_frequency_crystal)

print()
print("gleam_medium_frequency_crystal")
print(gmfc_top_ten)

print("multi-routing: order 1, route 1")
slgb_multi = multiRoute(gmfc_top_ten[0])
print(slgb_multi[0:9])

print("multi-routing: order 1, route 2")
slgb_multi = multiRoute(gmfc_top_ten[1])
print(slgb_multi[0:9])

print("multi-routing: order 1, route 3")
slgb_multi = multiRoute(gmfc_top_ten[2])
print(slgb_multi[0:9])

# print("Profit: ", "0$ ", "Distance: ", "0 jumps ", "Profit Per Jump: ", "0$")
