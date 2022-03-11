# This code never runs under normal operation of the tool
# Its use was to get get every system's connections in EVE to bypass the ESI
# Route request, as the request was used too often and slowed down the program
# This was also used to create the map seen in the GUI, the information is now
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
connections_data = []

counter = 0

for system in systems.data:
    system_request_operation = app.op["get_universe_systems_system_id"](
        system_id=system,
    )

    # Print the found market orders
    request = client.request(system_request_operation)

    sys_name = request.data.get("name")
    sys_id = request.data.get("system_id")
    sys_stargates = request.data.get("stargates")

    sys_connections = []

    if sys_stargates:
        for gate in sys_stargates:
            stargate_request_operation = app.op["get_universe_stargates_stargate_id"](
                stargate_id=gate
            )

            stargate_request = client.request(stargate_request_operation)
            connection = stargate_request.data.get("destination").get("system_id")
            sys_connections.append(connection)

    print(sys_name, sys_id, sys_connections)
    connections_data.append((sys_name, sys_id, sys_connections))

    counter += 1
    print(round((counter / systems_num) * 100), "%")

file = open("connections_data", "w+b")
pickle.dump(connections_data, file)
file.close()
