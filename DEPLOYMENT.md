# Render Deployment Guide for Schedule Notifier

## Backend Deployment (Render.com)

### Step 1: Create GitHub Repository (Optional but Recommended)

1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `schedule-notifier`
3. Make it private (recommended since it contains school data)
4. In your project folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/schedule-notifier.git
   git push -u origin main
   ```

### Step 2: Deploy Backend to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended) or email

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use "Public Git repository" if not using GitHub)
   - If using GitHub: Select `schedule-notifier` repository

3. **Configure Service**
   - **Name:** `schedule-notifier-backend`
   - **Region:** Choose closest to Israel (e.g., Frankfurt)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python api.py`
   - **Instance Type:** Free

4. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add:
   
   ```
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   DATABASE_PATH=/opt/render/project/src/schedule_notifier.db
   CHECK_INTERVAL_MINUTES=20
   HOST=0.0.0.0
   PORT=10000
   DEBUG=False
   ```

5. **Upload Firebase Credentials**
   - After creating the service, go to "Environment" tab
   - Click "Secret Files"
   - Add new secret file:
     - **Filename:** `firebase-credentials.json`
     - **Contents:** Paste your Firebase service account JSON

6. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - You'll get a URL like: `https://schedule-notifier-backend.onrender.com`

### Step 3: Deploy Frontend (Vercel - Recommended)

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select `schedule-notifier`

3. **Configure Project**
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`

4. **Add Environment Variables**
   Add all variables from `frontend/.env`:
   ```
   VITE_FIREBASE_API_KEY=AIzaSyCCkZZv14rlRsOPxzZbTdorUL5_WE6GRc0
   VITE_FIREBASE_AUTH_DOMAIN=schedule-notifier-7dd0e.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=schedule-notifier-7dd0e
   VITE_FIREBASE_STORAGE_BUCKET=schedule-notifier-7dd0e.firebasestorage.app
   VITE_FIREBASE_MESSAGING_SENDER_ID=576852404893
   VITE_FIREBASE_APP_ID=1:576852404893:web:294255bfd64fe495174274
   VITE_FIREBASE_VAPID_KEY=BFlSPrx0ZtWtCJhOXXS7TkCcklYFU9VTnBlLrYpOMmNzWe2UIJgdfgd_HNsxVecuGJ8B7YoycfjPpIPugenUpEQ
   VITE_API_URL=https://schedule-notifier-backend.onrender.com/api
   ```
   
   **IMPORTANT:** Update `VITE_API_URL` with your actual Render backend URL!

5. **Deploy**
   - Click "Deploy"
   - You'll get a URL like: `https://schedule-notifier.vercel.app`

### Step 4: Update Firebase Service Worker

After deployment, update the service worker with your backend URL:

1. Edit `frontend/public/firebase-messaging-sw.js`
2. No changes needed - it uses the same Firebase config

### Step 5: Test

1. Visit your Vercel URL
2. Complete onboarding
3. Check if changes load
4. Test notifications (you may need to wait for the 20-minute check cycle)

## Alternative: Deploy Frontend to Render (If you prefer one platform)

1. Create another Web Service on Render
2. **Name:** `schedule-notifier-frontend`
3. **Root Directory:** `frontend`
4. **Build Command:** `npm install && npm run build`
5. **Start Command:** `npx vite preview --host 0.0.0.0 --port $PORT`
6. Add same environment variables as above

## Troubleshooting

### Backend Issues:
- **500 errors:** Check Render logs for Python errors
- **Database errors:** Make sure DATABASE_PATH is correct
- **Firebase errors:** Verify secret file was uploaded correctly

### Frontend Issues:
- **Can't connect to backend:** Check VITE_API_URL is correct
- **Notifications not working:** Verify VAPID key is correct
- **Build fails:** Check all environment variables are set

### Common Issues:
- **CORS errors:** Backend already has CORS enabled, should work
- **Slow loading:** First request on free tier may take 30-60 seconds (cold start)
- **Database resets:** Free tier may reset database periodically - upgrade to paid if needed

## Costs

- **Render Free Tier:** 
  - 750 hours/month free
  - Sleeps after 15 minutes of inactivity
  - Wakes up on request (30-60 second delay)

- **Vercel Free Tier:**
  - Unlimited bandwidth
  - 100 GB-hours/month
  - Always on

**Total Cost: $0/month** (with limitations)

For always-on service, upgrade Render backend to $7/month.
