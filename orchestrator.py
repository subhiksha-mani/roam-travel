from location import get_location_ip, get_nearest_landmarks, reverse_geocode, get_prominent_places
from search import search_location
from data_processing import clean_text
from speech import text_to_speech

if __name__ == "__main__":

    lat, lng, _, _, _ = get_location_ip()
    topics = ["history", "cultural significance", "architecture"]

    nearest_places = get_nearest_landmarks(lat, lng)
    prominent_places = get_prominent_places(nearest_places)
    top_place = prominent_places[0]

    name = top_place["name"]

    response = search_location(top_place, topics)
    cleaned_context = clean_text(response, topics)

    text_to_speech(cleaned_context)
