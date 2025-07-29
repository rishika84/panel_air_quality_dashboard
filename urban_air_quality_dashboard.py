        .block-container {padding-top: 0rem !important;}
        .main .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important;}
        .stApp {padding-top: 0rem !important;}
        
        /* Remove gaps and spacing */
        .stMarkdown {margin-bottom: 0rem !important;}
        .element-container {margin-bottom: 0rem !important;}
        .stSelectbox {margin-bottom: 0rem !important;}
        .stTextInput {margin-bottom: 0rem !important;}
        
        /* Compact header */
        .header-container {margin-bottom: 0rem !important; padding-bottom: 0rem !important;}
        .block-container {padding-top: 0rem !important;}
        /* Ensure proper card positioning */
        .aqi-card-container {position: relative; z-index: 10; margin-top: -200px;}
        .main .block-container {padding-top: 0rem !important; padding-bottom: 0rem !important;}
        .stApp {padding-top: 0rem !important;}
        
        /* Remove any remaining gaps */
        .stApp > div > div > div > div {padding: 0 !important;}
        .main .block-container {padding-bottom: 0rem !important;}
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MAP SECTION ---
# Full-bleed map container
st.markdown("""
    <style>
    .full-bleed-map-container {
        width: 100vw; 
        margin-left: calc(-50vw + 50%); 
        margin-right: calc(-50vw + 50%); 
        padding: 0;
        
        /* Remove gaps and spacing */
        .stMarkdown {margin-bottom: 0rem !important;}
        .element-container {margin-bottom: 0rem !important;}
        .stSelectbox {margin-bottom: 0rem !important;}
        .stTextInput {margin-bottom: 0rem !important;}
        
        /* Compact header */
        .header-container {margin-bottom: 0rem !important; padding-bottom: 0rem !important;}
        
        /* Ensure proper card positioning */
        .aqi-card-container {position: relative; z-index: 10; margin-top: -200px;}
        
        /* Remove any remaining gaps */
        .stApp > div > div > div > div {padding: 0 !important;}
        .main .block-container {padding-bottom: 0rem !important;}
        margin-top: -1rem;
        margin-bottom: -2rem;
        position: relative;
        z-index: 1;
    }
    </style>
    <div class='full-bleed-map-container'>
""", unsafe_allow_html=True)
st_folium(m, width=3000, height=450)
st.markdown("</div>", unsafe_allow_html=True)
# --- AQI CARD DATA ---
city_data = latest[latest["site"] == selected_city].iloc[0]
city_name = selected_city
region = city_coords[selected_city].get('region', '') if selected_city in city_coords else ''
last_updated = city_data["datetime"].strftime("%d-%b %H:%M")
def calc_aqi(pm25):
    # US EPA breakpoints for PM2.5 (µg/m³)
    if pm25 <= 12:
        return int(pm25 / 12 * 50)
    elif pm25 <= 35.4:
        return int(50 + (pm25-12)/(35.4-12)*50)
    elif pm25 <= 55.4:
        return int(100 + (pm25-35.4)/(55.4-35.4)*50)
    elif pm25 <= 150.4:
        return int(150 + (pm25-55.4)/(150.4-55.4)*100)
    elif pm25 <= 250.4:
        return int(200 + (pm25-150.4)/(250.4-150.4)*100)
    elif pm25 <= 350.4:
        return int(300 + (pm25-250.4)/(350.4-250.4)*100)
    elif pm25 <= 500.4:
st.markdown('<div class="header-container">', unsafe_allow_html=True)
        return int(400 + (pm25-350.4)/(500.4-350.4)*100)
    else:
        return 500
aqi = calc_aqi(city_data["pm25"])
status, emoji, color = get_aqi_status(aqi)
        margin: -200px auto 0.5rem auto;
    <div class='aqi-card-container'>
        <div class='aqi-card-main'>
                    </div>
                </div>
            </div>
        </div>
    </div>
st.markdown('</div>', unsafe_allow_html=True)

# --- MAP SECTION ---
# Full-bleed map container
st.markdown("""
    <style>
    .full-bleed-map-container {
        width: 100vw; 
        margin-left: calc(-50vw + 50%); 
        margin-right: calc(-50vw + 50%); 
        padding: 0;
        margin-top: -1rem;
        margin-bottom: -2rem;
        position: relative;
        z-index: 1;
    }
    </style>
    <div class='full-bleed-map-container'>
""", unsafe_allow_html=True)
st_folium(m, width=3000, height=450)
st.markdown("</div>", unsafe_allow_html=True)
# --- AQI CARD DATA ---
city_data = latest[latest["site"] == selected_city].iloc[0]
city_name = selected_city
region = city_coords[selected_city].get('region', '') if selected_city in city_coords else ''
last_updated = city_data["datetime"].strftime("%d-%b %H:%M")
def calc_aqi(pm25):
    # US EPA breakpoints for PM2.5 (µg/m³)
    if pm25 <= 12:
        return int(pm25 / 12 * 50)
    elif pm25 <= 35.4:
        return int(50 + (pm25-12)/(35.4-12)*50)
    elif pm25 <= 55.4:
        return int(100 + (pm25-35.4)/(55.4-35.4)*50)
    elif pm25 <= 150.4:
        return int(150 + (pm25-55.4)/(150.4-55.4)*100)
    elif pm25 <= 250.4:
        return int(200 + (pm25-150.4)/(250.4-150.4)*100)
    elif pm25 <= 350.4:
        return int(300 + (pm25-250.4)/(350.4-250.4)*100)
    elif pm25 <= 500.4:
        return int(400 + (pm25-350.4)/(500.4-350.4)*100)
    else:
        return 500
aqi = calc_aqi(city_data["pm25"])
status, emoji, color = get_aqi_status(aqi)
        margin: -200px auto 0.5rem auto;
    <div class='aqi-card-container'>
        <div class='aqi-card-main'>
                    </div>
                </div>
            </div>
        </div>
    </div>