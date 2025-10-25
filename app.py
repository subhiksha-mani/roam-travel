import os
import streamlit as st
import pandas as pd

from streamlit_javascript import st_javascript
from geopy.geocoders import Nominatim

from location import get_location_ip, get_nearest_landmarks, get_prominent_places
from search import search_location
from data_processing import clean_text
from speech import text_to_speech

# Ensure audio directory exists
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ----------------------
# Streamlit page styling
# ----------------------
st.markdown("""
<style>
.main .block-container {
    max-width: 700px;
    margin: 0 auto;
    padding-top: 2rem;
}
h1, h2, h3, .tagline { 
    text-align: center; 
}
.tagline {
    font-size: 20px;
    color: #444;
    font-style: italic;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Roam")
st.markdown('<div class="tagline">Your AI-assisted travel companion.</div>', unsafe_allow_html=True)

# ----------------------
# Initialize session state
# ----------------------
for key in ["lat", "lng", "prominent_places", "selected_name", "summary", "city"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["lat", "lng", "city"] else []

# ----------------------
# Fetch user location
# ----------------------
# Only fetch if lat/lng not already in session_state
if st.session_state.get("lat") is None or st.session_state.get("lng") is None:
    coords = st_javascript(
        "navigator.geolocation.getCurrentPosition(pos => [pos.coords.latitude, pos.coords.longitude]);"
    )
    if coords:
        st.session_state.lat, st.session_state.lng = coords

# Fallback to IP-based location if browser location not available
if st.session_state.get("lat") is None or st.session_state.get("lng") is None:
    lat, lng, city, region, country = get_location_ip()
    st.session_state.lat = lat
    st.session_state.lng = lng
    st.session_state.city = city

# ----------------------
# Reverse geocode to get city name if missing
# ----------------------
if st.session_state.get("lat") and st.session_state.get("lng") and not st.session_state.get("city"):
    try:
        geolocator = Nominatim(user_agent="roam_app")
        location = geolocator.reverse((st.session_state.lat, st.session_state.lng), exactly_one=True)
        city = location.raw.get("address", {}).get("city") or \
               location.raw.get("address", {}).get("town") or \
               location.raw.get("address", {}).get("village")
        st.session_state.city = city
    except:
        st.session_state.city = None

if st.session_state.city:
    st.markdown(
        f"<p style='text-align:center; font-size:20px; font-weight:500;'>Looks like you're in {st.session_state.city}! Learn more about these spots nearby.</p>",
        unsafe_allow_html=True
    )

# ----------------------
# Get nearby landmarks
# ----------------------
if st.session_state.lat and st.session_state.lng:
    nearest_places = get_nearest_landmarks(st.session_state.lat, st.session_state.lng)
    st.session_state.prominent_places = get_prominent_places(nearest_places)
    print(st.session_state.prominent_places)

# ----------------------
# Display map and controls
# ----------------------
if st.session_state.prominent_places:
    map_data = pd.DataFrame([{
        "lat": p["geometry"]["location"]["lat"],
        "lon": p["geometry"]["location"]["lng"],
        "name": p["name"]
    } for p in st.session_state.prominent_places])
    st.map(map_data)

    landmark_names = [p["name"] for p in st.session_state.prominent_places]
    selected_index = 0 if not st.session_state.selected_name else landmark_names.index(st.session_state.selected_name)
    st.session_state.selected_name = st.selectbox(
        "Select a nearby landmark:",
        landmark_names,
        index=selected_index
    )

    topics_options = ["History", "Cultural Significance", "Architecture", "Food", "Nature", "Shopping", "Photography Spots"]
    default_topics = ["History", "Cultural Significance", "Architecture"]
    topics = st.multiselect("Select topics for summary:", topics_options, default=default_topics)

    # ----------------------
    # Generate summary & audio
    # ----------------------
    generate = st.button("Generate Summary and Audio") or (
        st.session_state.summary and isinstance(st.session_state.summary, str)
    )

    if generate:
        top_place = next(p for p in st.session_state.prominent_places if p["name"] == st.session_state.selected_name)

        # Generate summary if not already present
        if not st.session_state.summary or isinstance(st.session_state.summary, list):
            with st.spinner("Generating summary..."):
                response = search_location(top_place, topics)
                st.session_state.summary = clean_text(response, topics)

        # Ensure summary is a string
        summary_text = (
            " ".join(st.session_state.summary) if isinstance(st.session_state.summary, list) else st.session_state.summary
        )

        if not summary_text.strip():
            st.warning("Summary is empty. Cannot generate audio.")
        else:
            st.markdown(f"### {top_place['name']}")
            st.write(summary_text)

            # Generate TTS
            with st.spinner("Generating audio..."):
                audio_path = text_to_speech(summary_text)
                if audio_path:
                    st.audio(audio_path, format="audio/mp3")


