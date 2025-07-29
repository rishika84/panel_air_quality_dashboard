# Deploy to Render.com Without GitHub - Direct Upload Guide

## Method 1: Direct File Upload to Render

### Step 1: Prepare Your Files
Make sure you have these files in your project folder:
- `panel_air_quality_dashboard.py`
- `air_quality.sqlite`
- `requirements.txt`
- `render.yaml`

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with a new email account (different from your GitHub)
3. Verify your email

### Step 3: Deploy Using Direct Upload

#### Option A: Manual Upload
1. **Login to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Choose "Build and deploy from a Git repository"**
4. **Click "Connect account" → Choose "GitHub"**
5. **Create a new repository:**
   - Click "Create a new repository"
   - Name it: `air-quality-dashboard`
   - Make it Private (recommended)
   - Click "Create repository"

#### Option B: Use Render's Direct Deploy
1. **In Render Dashboard, click "New +" → "Web Service"**
2. **Choose "Deploy from existing repository"**
3. **Select your newly created repository**
4. **Configure the service:**
   - **Name:** `air-quality-dashboard`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT --allow-websocket-origin=*`
   - **Plan:** Free (or choose paid if needed)

### Step 4: Upload Your Files
1. **Clone the new repository locally:**
   ```bash
   git clone https://github.com/YOUR_NEW_ACCOUNT/air-quality-dashboard.git
   cd air-quality-dashboard
   ```

2. **Copy your files:**
   ```bash
   # Copy your dashboard files to this directory
   cp ../panel_air_quality_dashboard.py .
   cp ../air_quality.sqlite .
   cp ../requirements.txt .
   cp ../render.yaml .
   ```

3. **Push to the new repository:**
   ```bash
   git add .
   git commit -m "Initial dashboard deployment"
   git push origin main
   ```

## Method 2: Using Render CLI (Alternative)

### Step 1: Install Render CLI
```bash
# Install Render CLI
npm install -g @render/cli

# Or using curl
curl -s https://api.render.com/download/cli/linux | bash
```

### Step 2: Login and Deploy
```bash
# Login to Render
render login

# Deploy from current directory
render deploy
```

## Method 3: Using Render's Blueprint (Easiest)

### Step 1: Create Blueprint File
Create a file called `render.yaml` (already created for you):

```yaml
services:
  - type: web
    name: air-quality-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT --allow-websocket-origin=*
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
```

### Step 2: Deploy Using Blueprint
1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Upload your `render.yaml` file
4. Render will automatically create the service

## Method 4: Manual Service Creation

### Step 1: Create Web Service Manually
1. **Login to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Choose "Build and deploy from a Git repository"**
4. **Create new repository or use existing one**

### Step 2: Configure Service Settings
- **Name:** `air-quality-dashboard`
- **Environment:** `Python 3`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** Leave empty (if files are in root)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `panel serve panel_air_quality_dashboard.py --address 0.0.0.0 --port $PORT --allow-websocket-origin=*`

### Step 3: Environment Variables (if needed)
Add these if required:
- `PYTHON_VERSION`: `3.9`
- `PORT`: `10000` (Render will set this automatically)

## Quick Commands for New Repository

```bash
# Create new repository and push files
git init
git add .
git commit -m "Initial dashboard deployment"
git branch -M main
git remote add origin https://github.com/YOUR_NEW_ACCOUNT/air-quality-dashboard.git
git push -u origin main
```

## Important Notes

1. **Database File:** Make sure `air_quality.sqlite` is included in your repository
2. **File Size:** Render has limits on file sizes, but SQLite should be fine
3. **Free Tier:** Free tier has limitations but should work for your dashboard
4. **Custom Domain:** You can add a custom domain later if needed

## Troubleshooting

### Common Issues:
1. **Build fails:** Check `requirements.txt` has all dependencies
2. **Database not found:** Ensure SQLite file is in repository
3. **Port issues:** Render sets `$PORT` automatically
4. **Memory limits:** Free tier has memory restrictions

### Testing Locally First:
```bash
# Test before deploying
panel serve panel_air_quality_dashboard.py --port 10000
```

## Success Indicators

After deployment, you should see:
- ✅ Build completed successfully
- ✅ Service is running
- ✅ URL provided (like `https://your-app.onrender.com`)
- ✅ Dashboard loads in browser

Your dashboard will be accessible at the provided URL and can be shared with anyone! 