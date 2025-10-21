import math

import requests
from haversine import haversine

GOOGLE_API_KEY = "AIzaSyAIBIZP4_tSOwP5CFbqOsexq_gtajbhr0A"

def get_location_ip():
    try:
        data = requests.get("https://ipinfo.io/json").json()
        lat, lng = map(float, data["loc"].split(","))
        city = data.get("city", "")
        region = data.get("region", "")
        country = data.get("country", "")
        return lat, lng, city, region, country
    except Exception:
        return None, None, None, None, None


def reverse_geocode(lat, lng):
    """
    Convert lat/lng to human-readable location using Google Maps API
    """
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={GOOGLE_API_KEY}"
    data = requests.get(url).json()
    if data:
        return [
            {
                "name": loc["formatted_address"],
                "place_id": loc["place_id"],
                "types": loc["types"],
                "latitude": loc["geometry"]["location"]["lat"],
                "longitude": loc["geometry"]["location"]["lng"]
            }
            for loc in data.get("results", [])
        ]
    else:
        return "Invalid longitude/latitude."


def get_nearest_landmarks(lat: float | int, lng: float | int, k=5):
    rich_types = [
        "museum",  # art, history, science museums
        "shrine",  # religious sites
        "temple",  # Buddhist/Hindu/other temples
        "church",  # Christian churches
        "monument",  # statues, historic landmarks
        "park",  # major parks and gardens
        "garden",  # botanical gardens, iris gardens, etc.
        "historical_building",  # castles, old houses, heritage buildings
        "natural_feature",  # mountains, rivers, waterfalls
        "tourist_attraction",  # famous sights
        "landmark",  # well-known structures
        "art_gallery",  # significant galleries
        "stadium",  # architecturally notable or historic
        "zoo",  # major zoos
        "aquarium",  # large aquariums
        "cultural_center",  # cultural halls, centers, exhibition spaces
        "palace",  # historic palaces
        "fort",  # forts or citadels
        "castle",  # castles
        "observatory"  # major observatories
    ]
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    all_results = []
    for type in rich_types:
        params = {
            "location": f"{lat},{lng}",
            "radius": 1000,
            "type": type,
            "key": GOOGLE_API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()
        all_results.extend(data.get("results", []))

    all_results = [
        place for place in all_results
        if any(t in rich_types for t in place.get("types", []))
    ]

    unique_places = {}
    for place in all_results:
        place_id = place["place_id"]
        if place_id not in unique_places:
            unique_places[place_id] = place

    for place in unique_places.values():
        place["score"] = compute_distance_rating_weighted_score(place, lat, lng)

    top_grouped_places = group_top_places_fuzzy(unique_places.values(), threshold=0.5)

    top_places = top_grouped_places[:k]

    return top_places

def get_prominent_places(top_places):
    city = top_places[0].get("plus_code", {}).get("compound_code", "")

    if top_places:
        max_score = max(p['score'] for p in top_places)
        prominent_places = [p for p in top_places if p['score'] >= 0.3 * max_score]
        if prominent_places[0]['score'] <=40:
            print("Defaulting to city name as prominent place due to low scores below threshold.")
            prominent_places = [{"name": city, "score": 0}]

        if not prominent_places:
            print("No prominent places found. Defaulting to city name.")
            prominent_places = [{"name": city, "score": 0}]
    else:
        prominent_places = [{"name": city, "score": 0}]
        print("Prominent places generated: ", prominent_places)

    return prominent_places

def compute_distance_rating_weighted_score(place, curr_lat, curr_lng, alpha=0.5):
    place_coords = (place["geometry"]["location"]["lat"],  place["geometry"]["location"]["lng"])
    curr_coords = (curr_lat, curr_lng)

    # Returns in kilometers
    haversine_dst = haversine(place_coords, curr_coords)
    num_ratings = place.get("user_ratings_total", 0)

    score = place.get("rating", 0) * math.log(1 + num_ratings) - alpha * haversine_dst
    return score


from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def group_top_places_fuzzy(places, threshold=0.5):
    groups = []

    for place in places:
        name = place["name"]
        found_group = False

        for group in groups:
            if similar(name, group[0]["name"]) >= threshold:
                group.append(place)
                found_group = True
                break

        if not found_group:
            groups.append([place])

    top_grouped_places = [max(group, key=lambda x: x["score"]) for group in groups]
    top_grouped_places_sorted = sorted(top_grouped_places, key=lambda x: x["score"], reverse=True)

    return top_grouped_places_sorted


