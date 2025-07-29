import panel as pn
import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure Panel
pn.extension('plotly', sizing_mode='stretch_width')

# --- DATA LOADING FUNCTIONS ---
@pn.cache
def load_latest_data():
    """Load latest air quality data from SQLite database"""
    conn = sqlite3.connect("air_quality.sqlite")
    df = pd.read_sql_query("SELECT * FROM defra_uk_air_quality", conn)
    conn.close()
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Get latest for each site
    latest = df.sort_values("datetime").groupby("site").tail(1)
    return latest

@pn.cache
def load_historical_data():
    """Load historical data for trends"""
    conn = sqlite3.connect("air_quality.sqlite")
    df = pd.read_sql_query("SELECT * FROM defra_uk_air_quality", conn)
    conn.close()
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df

# Load data
latest_data = load_latest_data()
historical_data = load_historical_data()
cities = sorted(latest_data["site"].unique())

# --- AQI CALCULATION FUNCTIONS ---
def calc_aqi(pm25):
    """Calculate AQI based on PM2.5 using US EPA standards"""
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

def get_aqi_status(aqi):
    """Get AQI status, emoji, and color"""
    if aqi <= 50:
        return ("Good", "😊", "#00e400", "#e8f5e8")
    elif aqi <= 100:
        return ("Moderate", "😐", "#ffff00", "#fffde7")
    elif aqi <= 150:
        return ("Unhealthy for Sensitive Groups", "😷", "#ff7e00", "#fff3e0")
    elif aqi <= 200:
        return ("Unhealthy", "😷", "#ff0000", "#ffebee")
    elif aqi <= 300:
        return ("Very Unhealthy", "🤢", "#8f3f97", "#f3e5f5")
    else:
        return ("Hazardous", "☠️", "#7e0023", "#fce4ec")

# --- INTERACTIVE COMPONENTS ---
city_selector = pn.widgets.Select(
    name='Select City', 
    options=cities, 
    value=cities[0] if cities else None,
    width=300
)

# Create a JavaScript callback to sync HTML dropdown with Panel widget
dropdown_js = pn.pane.HTML("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const cityDropdown = document.getElementById('city-dropdown');
    if (cityDropdown) {
        cityDropdown.addEventListener('change', function() {
            const selectedCity = this.value;
            // This will trigger the Panel widget update
            window.parent.postMessage({
                type: 'city_change',
                city: selectedCity
            }, '*');
        });
    }
});
</script>
""")

time_range = pn.widgets.Select(
    name='Time Range',
    options=['Last 24 Hours', 'Last 7 Days', 'Last 30 Days'],
    value='Last 24 Hours',
    width=200
)

# --- MAP CREATION ---
def create_map(city=None):
    """Create interactive map with air quality data"""
    if city and city in latest_data['site'].values:
        # Filter data for selected city
        city_data = latest_data[latest_data['site'] == city].iloc[0]
        center_lat = city_data['latitude']
        center_lon = city_data['longitude']
        zoom = 11  # Closer zoom for selected city
    else:
        # Default UK view
        center_lat, center_lon, zoom = 54.5, -3, 5.5
    
    # Create map with all cities
    fig = px.scatter_map(
        latest_data,
        lat='latitude',
        lon='longitude',
        hover_name='site',
        hover_data=['pm25', 'pm10', 'no2', 'o3'],
        color='pm25',
        color_continuous_scale='RdYlGn_r',
        size='pm25',
        zoom=zoom,
        center={'lat': center_lat, 'lon': center_lon}
    )
    
    # Highlight selected city with larger, prominent marker
    if city and city in latest_data['site'].values:
        city_data = latest_data[latest_data['site'] == city].iloc[0]
        fig.add_trace(go.Scattermap(
            lat=[city_data['latitude']],
            lon=[city_data['longitude']],
            mode='markers',
            marker=dict(
                size=30,
                color='#ff0000',
                symbol='circle'
            ),
            name=city,
            showlegend=False,
            hovertemplate=f'<b>{city}</b><br>Selected City<br>PM2.5: {city_data["pm25"]:.1f} µg/m³<extra></extra>'
        ))
    
    fig.update_layout(
        map_style='carto-positron',
        height=450,
        margin={'l': 0, 'r': 0, 't': 30, 'b': 0},
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig

# --- AQI CARD CREATION ---
def create_aqi_card(city):
    """Create AQI status card"""
    if city not in latest_data['site'].values:
        return "City data not available"
    
    city_data = latest_data[latest_data['site'] == city].iloc[0]
    aqi = calc_aqi(city_data['pm25'])
    status, emoji, color, bg_color = get_aqi_status(aqi)
    
    # Format last updated time
    last_updated = city_data['datetime'].strftime("%d %b %H:%M")
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 50%, #e9ecef 100%);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        margin: -80px 0 20px 0;
        position: relative;
        z-index: 10;
        width: 100%;
        color: #333;
        min-height: 120px;
    ">
        <!-- Header - Left aligned -->
        <div style="text-align: left; margin-bottom: 15px;">
            <h2 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Real-time Air Quality Data</h2>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">{city}, United Kingdom • Last Updated: {last_updated}</p>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <!-- Left side - AQI and PM values -->
            <div style="flex: 3; display: flex; gap: 40px; align-items: center;">
                <!-- AQI Section -->
                <div style="text-align: left;">
                    <div style="font-size: 0.9rem; color: #666; margin-bottom: 3px;">Live AQI</div>
                    <div style="font-size: 3.5rem; font-weight: bold; color: {color}; margin-bottom: 3px;">{aqi}</div>
                    <div style="font-size: 1rem; font-weight: 600; color: #333; margin-bottom: 3px;">Air Quality is</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: {color};">{status}</div>
                </div>
                
                <!-- PM Values -->
                <div style="text-align: left; display: flex; gap: 30px;">
                    <div>
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 2px;">PM10</div>
                        <div style="font-size: 1.1rem; font-weight: bold; color: #333;">{city_data['pm10']:.1f} µg/m³</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 2px;">PM2.5</div>
                        <div style="font-size: 1.1rem; font-weight: bold; color: #333;">{city_data['pm25']:.1f} µg/m³</div>
                    </div>
                </div>
            </div>
            
            <!-- Right side - Weather card -->
            <div style="flex: 1; background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 15px; border: 1px solid #e0e0e0;">
                <div style="text-align: center;">
                    <div style="font-size: 1.3rem; margin-bottom: 3px;">☁️</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #333; margin-bottom: 3px;">{city_data['temperature']:.1f}°C</div>
                    <div style="font-size: 0.8rem; color: #666; margin-bottom: 2px;">Humidity: {city_data['humidity']:.1f}%</div>
                    <div style="font-size: 0.8rem; color: #666;">Wind: 14 km/h</div>
                </div>
            </div>
        </div>
        
        <!-- Compact AQI Scale Bar -->
        <div style="margin-top: 15px;">
            <div style="display: flex; height: 4px; border-radius: 2px; overflow: hidden; margin-bottom: 6px;">
                <div style="flex: 1; background: #00e400;"></div>
                <div style="flex: 1; background: #ffff00;"></div>
                <div style="flex: 1; background: #ff7e00;"></div>
                <div style="flex: 1; background: #ff0000;"></div>
                <div style="flex: 1; background: #8f3f97;"></div>
                <div style="flex: 1; background: #7e0023;"></div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-size: 0.65rem; color: #666;">Good</span>
                <span style="font-size: 0.65rem; color: #666;">Moderate</span>
                <span style="font-size: 0.65rem; color: #666;">Poor</span>
                <span style="font-size: 0.65rem; color: #666;">Unhealthy</span>
                <span style="font-size: 0.65rem; color: #666;">Severe</span>
                <span style="font-size: 0.65rem; color: #666;">Hazardous</span>
            </div>
        </div>
    </div>
    """
    
    return card_html

# --- TREND CHARTS ---
def create_trend_chart(city, time_range):
    """Create AQI trend chart"""
    if city not in historical_data['site'].values:
        return go.Figure()
    
    # Filter data for selected city and time range
    city_data = historical_data[historical_data['site'] == city].copy()
    
    if time_range == 'Last 24 Hours':
        cutoff = datetime.now() - timedelta(hours=24)
    elif time_range == 'Last 7 Days':
        cutoff = datetime.now() - timedelta(days=7)
    else:  # Last 30 Days
        cutoff = datetime.now() - timedelta(days=30)
    
    city_data = city_data[city_data['datetime'] >= cutoff].sort_values('datetime')
    
    if city_data.empty:
        return go.Figure()
    
    # Calculate AQI for each data point
    city_data['aqi'] = city_data['pm25'].apply(calc_aqi)
    
    fig = go.Figure()
    
    # Add AQI line
    fig.add_trace(go.Scatter(
        x=city_data['datetime'],
        y=city_data['aqi'],
        mode='lines+markers',
        name='AQI',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6)
    ))
    
    # Add PM2.5 line
    fig.add_trace(go.Scatter(
        x=city_data['datetime'],
        y=city_data['pm25'],
        mode='lines+markers',
        name='PM2.5 (µg/m³)',
        line=dict(color='#ff6b6b', width=2),
        marker=dict(size=4),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f'AQI Trend - {city}',
        height=300,
        xaxis_title='Time',
        yaxis_title='AQI',
        yaxis2=dict(title='PM2.5 (µg/m³)', overlaying='y', side='right'),
        hovermode='x unified',
        showlegend=True,
        legend=dict(x=0.02, y=0.98)
    )
    
    return fig

def create_pollutants_chart(city):
    """Create pollutants comparison chart"""
    if city not in latest_data['site'].values:
        return go.Figure()
    
    city_data = latest_data[latest_data['site'] == city].iloc[0]
    
    pollutants = ['PM2.5', 'PM10', 'NO₂', 'O₃']
    values = [city_data['pm25'], city_data['pm10'], city_data['no2'], city_data['o3']]
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
    
    fig = go.Figure(data=[
        go.Bar(
            x=pollutants,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}' for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f'Current Pollutant Levels - {city}',
        height=300,
        yaxis_title='Concentration (µg/m³)',
        showlegend=False
    )
    
    return fig

# --- DASHBOARD LAYOUT ---
# Create a header with Panel widgets properly embedded
header = pn.Row(
    pn.pane.HTML("""
        <div style="
            background: white;
            color: #333;
            padding: 8px 0;
            margin: 0;
            border-bottom: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; justify-content: flex-start; max-width: 1200px; margin: 0 auto; gap: 30px;">
                <div style="display: flex; align-items: center;">
                    <h1 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #333;">UK AIR QUALITY DASHBOARD</h1>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="position: relative;">
                        <input type="text" placeholder="Search any Location, City..." 
                               style="padding: 8px 12px 8px 35px; border: 1px solid #d0d7de; border-radius: 6px; font-size: 14px; width: 250px; background-image: url('data:image/svg+xml;utf8,<svg fill=&quot;%2399a1b3&quot; height=&quot;16&quot; viewBox=&quot;0 0 24 24&quot; width=&quot;16&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;><path d=&quot;M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99a1 1 0 001.41-1.41l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z&quot;></path></svg>'); background-repeat: no-repeat; background-position: 10px center;"
                        />
                    </div>
                </div>
            </div>
        </div>
    """),
    city_selector,
    time_range,
    align='center'
)

# Controls row is no longer needed since dropdowns are in header
controls = pn.Row(align='center')

# Map section
map_pane = pn.pane.Plotly(create_map(cities[0] if cities else None), height=450)

# AQI Card (will be updated dynamically) - centered like AQI.in
aqi_card = pn.pane.HTML(create_aqi_card(cities[0] if cities else None))

# Create pollutant cards function
def create_historical_aqi_graph(city):
    """Create historical AQI graph for a city - synchronized with original data"""
    if not city:
        return None
    
    # Get historical data for the city
    df = load_historical_data()
    city_data = df[df['site'] == city].copy()
    
    if city_data.empty:
        # If no data for this city, create a placeholder graph
        fig = go.Figure()
        fig.add_annotation(
            text=f"No historical data available for {city}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=200,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Convert datetime to datetime
    city_data['datetime'] = pd.to_datetime(city_data['datetime'])
    
    # Sort by datetime
    city_data = city_data.sort_values('datetime')
    
    # Get the last 24 hours of data for better synchronization
    latest_time = city_data['datetime'].max()
    cutoff_time = latest_time - timedelta(hours=24)
    recent_data = city_data[city_data['datetime'] >= cutoff_time].copy()
    
    # If we don't have 24 hours of data, get the last 20 data points
    if len(recent_data) < 5:
        recent_data = city_data.tail(20).copy()
    
    if recent_data.empty:
        # Still no data, create placeholder
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {city}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=200,
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Calculate AQI for each row
    recent_data['aqi'] = recent_data['pm25'].apply(calc_aqi)
    
    # Create the graph
    fig = go.Figure()
    
    # Add bar chart with dark green styling
    fig.add_trace(go.Bar(
        x=recent_data['datetime'],
        y=recent_data['aqi'],
        marker_color='#2e7d32',
        name='AQI',
        hovertemplate='<b>Time:</b> %{x}<br><b>AQI:</b> %{y}<extra></extra>',
        marker_line_width=0,
        opacity=0.9
    ))
    
    # Update layout - centered and properly formatted
    fig.update_layout(
        title=None,
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10),
        margin=dict(l=40, r=20, t=20, b=40),
        height=200,
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor='#f0f0f0',
            tickformat='%m-%d %H:%M',
            tickmode='auto',
            nticks=6,
            tickfont=dict(size=9),
            tickangle=0
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f0f0f0',
            range=[0, max(recent_data['aqi']) * 1.1 if max(recent_data['aqi']) > 0 else 50],
            tickfont=dict(size=9),
            tickmode='linear',
            dtick=20
        )
    )
    
    return fig

def create_aqi_index():
    """Create AQI index scale component"""
    return f"""
    <div style="
        margin: 30px auto;
        max-width: 1200px;
        width: 100%;
        padding: 30px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    ">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="margin: 0; color: #333; font-size: 1.8rem; font-weight: 600;">Air Quality Index (AQI) Scale</h2>
            <p style="margin: 8px 0 0 0; color: #666; font-size: 1rem;">Know about the category of air quality index (AQI) your ambient air falls in and what it implies.</p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
            <!-- Good -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #00e400;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #00e400;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">😊</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Good</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(0 to 50)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">The air is fresh and free from toxins. Enjoy outdoor activities without any health concerns.</p>
                </div>
            </div>
            
            <!-- Moderate -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #ffff00;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #ffff00;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #333;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">😐</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Moderate</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(51 to 100)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">Air quality is acceptable for most, but sensitive individuals might experience mild discomfort.</p>
                </div>
            </div>
            
            <!-- Poor -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #ff7e00;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #ff7e00;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">😷</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Poor</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(101 to 150)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">Breathing may become slightly uncomfortable, especially for those with respiratory issues.</p>
                </div>
            </div>
            
            <!-- Unhealthy -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #ff0000;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #ff0000;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">😷</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Unhealthy</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(151 to 200)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">This air quality is particularly risky for children, pregnant women, and the elderly. Limit outdoor activities.</p>
                </div>
            </div>
            
            <!-- Severe -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #8f3f97;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #8f3f97;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">🤢</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Severe</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(201 to 300)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">Prolonged exposure can cause chronic health issues or organ damage. Avoid outdoor activities.</p>
                </div>
            </div>
            
            <!-- Hazardous -->
            <div style="
                background: #f8f9fa;
                border-left: 5px solid #7e0023;
                border-radius: 8px;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 15px;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: #7e0023;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                ">☠️</div>
                <div>
                    <h3 style="margin: 0 0 5px 0; color: #333; font-size: 1.2rem; font-weight: 600;">Hazardous</h3>
                    <p style="margin: 0 0 3px 0; color: #666; font-size: 0.9rem; font-weight: 500;">(301+)</p>
                    <p style="margin: 0; color: #333; font-size: 0.9rem; line-height: 1.4;">Dangerously high pollution levels. Life-threatening health risks with prolonged exposure. Stay indoors and take precautions.</p>
                </div>
            </div>
        </div>
    </div>
    """

def create_pollutant_cards(city):
    """Create pollutant cards like AQI.in - improved layout"""
    if city not in latest_data['site'].values:
        return "City data not available"
    
    city_data = latest_data[latest_data['site'] == city].iloc[0]
    
    cards_html = f"""
    <div style="
        background: white;
        padding: 40px 60px;
        margin: 30px auto;
        max-width: 1400px;
        width: 100%;
    ">
        <div style="margin-bottom: 30px; text-align: center;">
            <h2 style="margin: 0; color: #333; font-size: 1.8rem; font-weight: 600;">Major Air Pollutants</h2>
            <p style="margin: 8px 0 0 0; color: #0066cc; font-size: 1.2rem; font-weight: 500;">{city}</p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; max-width: 1200px; margin: 0 auto;">
            <!-- PM2.5 Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                 cursor: pointer;
                 transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Particulate Matter</div>
                    <div style="font-size: 0.9rem; color: #666;">(PM2.5)</div>
                 </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data['pm25']:.1f} µg/m³</div>
                    <div style="font-size: 1.2rem; color: #666;">→</div>
                </div>
            </div>
            
            <!-- PM10 Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                 cursor: pointer;
                 transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Particulate Matter</div>
                    <div style="font-size: 0.9rem; color: #666;">(PM10)</div>
                 </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data['pm10']:.1f} µg/m³</div>
                    <div style="font-size: 1.2rem; color: #ff0000;">⚠️</div>
                </div>
            </div>
            
            <!-- CO Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Carbon Monoxide</div>
                    <div style="font-size: 0.9rem; color: #666;">(CO)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data.get('co', 95):.0f} ppb</div>
                    <div style="font-size: 1.2rem; color: #666;">→</div>
                </div>
            </div>
            
            <!-- SO2 Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Sulfur Dioxide</div>
                    <div style="font-size: 0.9rem; color: #666;">(SO2)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data.get('so2', 0):.0f} ppb</div>
                    <div style="font-size: 1.2rem; color: #666;">↓</div>
                </div>
            </div>
            
            <!-- NO2 Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Nitrogen Dioxide</div>
                    <div style="font-size: 0.9rem; color: #666;">(NO2)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data['no2']:.0f} ppb</div>
                    <div style="font-size: 1.2rem; color: #666;">↓</div>
                </div>
            </div>
            
            <!-- O3 Card -->
            <div style="
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-left: 5px solid #00e400;
                border-radius: 12px;
                padding: 25px 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                cursor: pointer;
                transition: all 0.3s ease;
                min-height: 120px;
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: center;
            " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <div style="font-size: 1.1rem; color: #333; font-weight: 500;">Ozone</div>
                    <div style="font-size: 0.9rem; color: #666;">(O3)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="font-size: 1.8rem; font-weight: bold; color: #333;">{city_data['o3']:.0f} ppb</div>
                    <div style="font-size: 1.2rem; color: #666;">→</div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return cards_html

# Create pollutant cards
pollutant_cards = pn.pane.HTML(create_pollutant_cards(cities[0] if cities else None))

# Create historical AQI graph with width control - centered
aqi_graph = pn.pane.Plotly(
    create_historical_aqi_graph(cities[0] if cities else None),
    width=1200,
    height=250,
    align='center'
)

# Create graph header
def create_graph_header(city):
    return f"""
    <div style="
        margin: 20px auto 0 auto;
        max-width: 1200px;
        width: 100%;
        padding: 20px 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="text-align: left;">
                <p style="margin: 0; color: #666; font-size: 0.9rem; font-weight: 500;">AQI Graph</p>
                <h3 style="margin: 5px 0 0 0; color: #333; font-size: 1.4rem; font-weight: 600;">Historical Air Quality Data</h3>
                <p style="margin: 5px 0 0 0; color: #0066cc; font-size: 1rem; font-weight: 500;">{city}</p>
        </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="display: flex; background: #f5f5f5; border-radius: 6px; padding: 2px;">
                <button style="
                        background: #007bff;
                        color: white;
                    border: none;
                        padding: 8px 12px;
                        border-radius: 4px;
                    cursor: pointer;
                        font-size: 0.8rem;
                        font-weight: 500;
                ">📊</button>
                <button style="
                        background: #e0e0e0;
                        color: #333;
                    border: none;
                        padding: 8px 12px;
                        border-radius: 4px;
                    cursor: pointer;
                        font-size: 0.8rem;
                ">📈</button>
            </div>
            <select style="
                    padding: 8px 12px;
                border: 1px solid #ddd;
                    border-radius: 6px;
                    font-size: 0.9rem;
                background: white;
                    cursor: pointer;
            ">
                <option>24 Hours</option>
                <option>7 Days</option>
                <option>30 Days</option>
            </select>
            <select style="
                    padding: 8px 12px;
                border: 1px solid #ddd;
                    border-radius: 6px;
                    font-size: 0.9rem;
                background: white;
                    cursor: pointer;
            ">
                <option>AQI</option>
                <option>PM2.5</option>
                <option>PM10</option>
            </select>
            </div>
        </div>
    </div>
    """

graph_header = pn.pane.HTML(create_graph_header(cities[0] if cities else None))

# Charts section with pollutant cards and graph as separate sections - properly centered
charts_row = pn.Column(
    pollutant_cards,
    graph_header,
    pn.Column(aqi_graph, align='center', width=1200),
    align='center',
    sizing_mode='stretch_width'
)

# Create AQI index component
aqi_index = pn.pane.HTML(create_aqi_index())

# Main dashboard layout - properly centered
dashboard = pn.Column(
    header,
    map_pane,
    pn.Column(aqi_card, align='center', width=800),
    charts_row,
    aqi_index,
    align='center',
    sizing_mode='stretch_width'
)

# --- INTERACTIVITY ---
@pn.depends(city_selector.param.value, watch=True)
def update_map(city):
    """Update map when city changes"""
    map_pane.object = create_map(city)

@pn.depends(city_selector.param.value, watch=True)
def update_aqi_card(city):
    """Update AQI card when city changes"""
    aqi_card.object = create_aqi_card(city)

@pn.depends(city_selector.param.value, watch=True)
def update_pollutant_cards(city):
    """Update pollutant cards when city changes"""
    pollutant_cards.object = create_pollutant_cards(city)

@pn.depends(city_selector.param.value, watch=True)
def update_aqi_graph(city):
    """Update AQI graph when city changes"""
    aqi_graph.object = create_historical_aqi_graph(city)

@pn.depends(city_selector.param.value, watch=True)
def update_graph_header(city):
    """Update graph header when city changes"""
    graph_header.object = create_graph_header(city)

# --- RUN DASHBOARD ---
if __name__ == '__main__':
    dashboard.show()
else:
    # For running in notebook or other environments
    dashboard 