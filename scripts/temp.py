from foodbridge.modules.location import Location
from foodbridge.modules.pantryLoop import PantryLoop
from foodbridge.search.search import searchDDG

location_module = Location()
location = location_module.forward()
print(f"Location found: {location}")

links = []
if location["city"] and location["area"]:
    links = searchDDG(f"Food Pantry near {location["area"]} {location["city"]}")
else:
    links = searchDDG(f"Food Pantry near {location["city"]}")

PantryLoop = PantryLoop(links)
PantryLoop.forward()