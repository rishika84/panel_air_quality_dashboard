# Panel Air Quality Dashboard - Deployment Guide

## Overview
Your Panel dashboard can be deployed and shared with others through several methods. Here are the best options for sharing your air quality dashboard:

## Option 1: Local Network Sharing (Easiest)

### For sharing within your local network (same WiFi/office):

```bash
# Run the dashboard on your local network
panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port 5006 --allow-websocket-origin=*
```

**How to share:**
- Find your computer's IP address: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Share the URL: `http://YOUR_IP_ADDRESS:5006/panel_air_quality_dashboard`
- Others on the same network can access it

## Option 2: Cloud Deployment (Recommended for wider sharing)

### A. Render.com (Free tier available)

1. **Create a `requirements.txt` file:**
```txt
panel
pandas
sqlite3
numpy
plotly
```

2. **Create a `render.yaml` file:**
```yaml
services:
  - type: web
    name: air-quality-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
```

3. **Deploy:**
- Go to [render.com](https://render.com)
- Connect your GitHub repository
- Deploy automatically

### B. Heroku (Free tier discontinued, but still popular)

1. **Create `Procfile`:**
```
web: panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT
```

2. **Create `runtime.txt`:**
```
python-3.9.18
```

3. **Deploy:**
```bash
heroku create your-dashboard-name
git add .
git commit -m "Deploy dashboard"
git push heroku main
```

### C. Railway.app (Free tier available)

1. **Create `railway.json`:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

2. **Deploy:**
- Go to [railway.app](https://railway.app)
- Connect your GitHub repository
- Deploy automatically

## Option 3: GitHub Pages + Panel (Advanced)

### For static deployment:

1. **Create a static version:**
```python
# Add this to your dashboard file
if __name__ == '__main__':
    # For static export
    dashboard.save('dashboard.html')
```

2. **Deploy to GitHub Pages:**
- Push the HTML file to your repository
- Enable GitHub Pages in repository settings

## Option 4: Docker Deployment

### Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5006

CMD ["panel", "serve", "panel_air_quality_dashboard.py", "--address", "0.0.0.0", "--port", "5006"]
```

### Deploy with Docker:
```bash
docker build -t air-quality-dashboard .
docker run -p 5006:5006 air-quality-dashboard
```

## Option 5: Streamlit Cloud (Alternative)

If you want to convert to Streamlit for easier deployment:

1. **Convert your dashboard to Streamlit format**
2. **Deploy to [share.streamlit.io](https://share.streamlit.io)**

## Quick Start Commands

### For immediate local sharing:
```bash
# Install dependencies
pip install panel pandas plotly

# Run and share on network
panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port 5006 --allow-websocket-origin=*
```

### For cloud deployment preparation:
```bash
# Create requirements file
pip freeze > requirements.txt

# Test locally first
panel serve panel_air_quality_dashboard.py
```

## Important Notes

1. **Database Access**: Make sure your `air_quality.sqlite` file is included in the deployment
2. **Port Configuration**: Most cloud platforms use `$PORT` environment variable
3. **Dependencies**: Ensure all required packages are in `requirements.txt`
4. **Security**: For public deployment, consider adding authentication

## Recommended Approach

**For quick sharing with colleagues:**
- Use Option 1 (Local Network)

**For wider public access:**
- Use Option 2A (Render.com) - easiest and free

**For professional deployment:**
- Use Option 4 (Docker) - most reliable and scalable

## Troubleshooting

### Common Issues:
1. **Port already in use**: Change port number in command
2. **Database not found**: Ensure SQLite file is in same directory
3. **Dependencies missing**: Check `requirements.txt` is complete

### Testing before deployment:
```bash
# Test locally
panel serve panel_air_quality_dashboard.py

# Test with specific port
panel serve panel_air_quality_dashboard.py --port 8080
```

## Next Steps

1. Choose your preferred deployment method
2. Create the necessary configuration files
3. Test locally first
4. Deploy to your chosen platform
5. Share the URL with others

Your dashboard will be accessible via a web browser and can be shared with anyone who has the URL! 