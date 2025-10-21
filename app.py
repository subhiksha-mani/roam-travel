import os

import streamlit as st
import pandas as pd

from location import get_location_ip, get_nearest_landmarks, get_prominent_places
from search import search_location
from data_processing import clean_text
from speech import text_to_speech

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

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

for key in ["lat", "lng", "prominent_places", "selected_name", "summary", "city"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["lat", "lng", "city"] else []

if st.session_state.lat is None or st.session_state.lng is None:
    with st.spinner("Fetching your location and nearby prominent spots..."):
        lat, lng, city, region, country = get_location_ip()
        if lat and lng:
            st.session_state.lat = lat
            st.session_state.lng = lng
            st.session_state.city = city

if st.session_state.city:
    st.markdown(
        f"<p style='text-align:center; font-size:20px; font-weight:500;'>Looks like you're in {st.session_state.city}! Learn more about these spots nearby.</p>",
        unsafe_allow_html=True
    )
if st.session_state.lat and st.session_state.lng:
    nearest_places = get_nearest_landmarks(st.session_state.lat, st.session_state.lng)
    st.session_state.prominent_places = get_prominent_places(nearest_places)

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

    if st.button("Generate Summary") or st.session_state.summary:
        top_place = next(p for p in st.session_state.prominent_places if p["name"] == st.session_state.selected_name)

        if st.session_state.summary is None:
            response = search_location(top_place, topics)
            st.session_state.summary = clean_text(response, topics)

        st.markdown(f"### {top_place['name']}")
        st.write(st.session_state.summary)

        audio_path = text_to_speech(st.session_state.summary, top_place["name"])
        st.audio(audio_path, format="audio/mp3")


