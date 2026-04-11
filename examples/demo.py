import os
from ndamaps import NDAMapsClient, ClientOptions

def main():
    api_key = os.environ.get("NDAMAPS_API_KEY")
    if not api_key:
        print("Please set NDAMAPS_API_KEY environment variable")
        return

    client = NDAMapsClient(ClientOptions(api_key=api_key))

    print("--- 1. Forward Geocoding ---")
    geocode_res = client.geocoding.forward_google(address="Hồ Hoàn Kiếm, Hà Nội")
    if "results" in geocode_res and len(geocode_res["results"]) > 0:
        location = geocode_res["results"][0].get("geometry", {}).get("location", {})
        print(f"Result: {location}")

    print("\n--- 2. Optimized Route (Travelling Salesperson) ---")
    locations = [
        {"lat": 21.03624, "lon": 105.77142}, # Home base
        {"lat": 21.03326, "lon": 105.78743}, # Delivery 1
        {"lat": 21.00329, "lon": 105.81834}, # Delivery 2
        {"lat": 21.03624, "lon": 105.77142}  # Return home
    ]
    
    route_res = client.navigation.optimized_route(locations=locations, costing="auto")
    
    trip = route_res.get("trip", {})
    if "summary" in trip:
        print(f"Total Distance: {trip['summary'].get('length')} meters")
        print(f"Total ETA: {trip['summary'].get('time')} seconds")

    order = [loc.get("original_index") for loc in trip.get("locations", [])]
    print(f"Optimized stops order (original indices): {order}")

if __name__ == "__main__":
    main()
