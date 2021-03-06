# This code never runs under normal operation of the tool
# Its use was to get get every system in EVE and get information about it,
# This was used to create the map seen in the GUI, the information is now
# Stored in a pickle file. If the EVE map ever changes, delete that pickle
# File and run this code.

from esipy import EsiApp
from esipy import EsiClient

import pickle


# Create the ESI interface application and a client (currently a public client)
esi_app = EsiApp()
app = esi_app.get_latest_swagger

client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={
        "User-Agent": "Something CCP can use to contact you and that define your app"
    },
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)

# Get market orders for a region
systems_request = app.op["get_universe_systems"]()
systems = client.request(systems_request)

systems_num = len(systems.data)
systems_data = []

counter = 0

for system in systems.data:
    request_operation = app.op["get_universe_systems_system_id"](
        system_id=system,
    )

    # Print the found market orders
    request = client.request(request_operation)
    sys_name = request.data.get("name")
    sys_id = request.data.get("system_id")
    sys_pos = request.data.get("position")
    print(
        sys_name,
        sys_id,
        "X: ",
        sys_pos.get("x"),
        "Y: ",
        sys_pos.get("y"),
    )

    systems_data.append((sys_name, sys_id, (sys_pos.get("x"), sys_pos.get("y"))))

    counter += 1
    print(round((counter / systems_num) * 100), "%")

file = open("systems_data", "w+b")
pickle.dump(systems_data, file)
file.close()
