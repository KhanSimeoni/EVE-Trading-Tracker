from esipy import EsiApp
from esipy import EsiClient


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
systems = [30002187, 30002186, 30002185]
for system in systems:
    request_operation = app.op["get_universe_systems_system_id"](
        system_id=system,
    )

    # Print the found market orders
    request = client.request(request_operation)
    print(request.data.get("name"), request.data.get("position"))
