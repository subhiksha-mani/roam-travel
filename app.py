import os
import streamlit as st
import pandas as pd

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
from streamlit.components.v1 import html

# ----------------------
# Fetch user location (browser geolocation)
# ----------------------
if st.session_state.lat is None or st.session_state.lng is None:
    # Embed JS to get browser location
    html("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            document.querySelector('#coords').value = lat + ',' + lng;
        }
    );
    </script>
    <input type="text" id="coords" style="display:none;">
    """, height=0)

    coords_input = st.text_input("Coordinates (lat,lng):", key="coords")

    if coords_input:
        try:
            lat, lng = map(float, coords_input.split(","))
            st.session_state.lat = lat
            st.session_state.lng = lng
        except:
            st.warning("Waiting for browser location… please allow access in your browser.")

    if st.session_state.lat and st.session_state.lng:
        # Optional: reverse geocode to get city name
        city = get_location_ip()[2]  # keep your current IP-based city fallback
        st.session_state.city = city

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


