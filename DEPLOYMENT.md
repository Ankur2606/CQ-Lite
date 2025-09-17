# Deployment Guide

## Backend Deployment on Render

1. **Create a Render Account**
   - Go to [render.com](https://render.com) and sign up
   - Connect your GitHub repository

2. **Deploy from GitHub**
   - Click "New Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration

3. **Environment Variables**
   Set the following environment variables in Render dashboard:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `NEBIUS_API_KEY`: Your Nebius API key (if using)

4. **Deployment Configuration**
   The `render.yaml` file contains all necessary configuration:
   - Python 3.12 runtime
   - Automatic dependency installation from `requirements.txt`
   - Health check endpoint at `/api/health`
   - Service will be available at: `https://cq-lite-backend.onrender.com`

## Frontend Deployment on Netlify

1. **Create a Netlify Account**
   - Go to [netlify.com](https://netlify.com) and sign up
   - Connect your GitHub repository

2. **Deploy from GitHub**
   - Click "New site from Git"
   - Select your repository
   - Netlify will automatically use the `netlify.toml` configuration

3. **Build Settings**
   The `netlify.toml` file contains:
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/out`
   - Environment variable: `NEXT_PUBLIC_API_URL=https://cq-lite-backend.onrender.com`

4. **Custom Domain (Optional)**
   - In Netlify dashboard, go to Domain settings
   - Add your custom domain if you have one

## Environment Variables

### Backend (Render)
- `GOOGLE_API_KEY`: Required for Gemini AI service
- `NEBIUS_API_KEY`: Optional for Nebius AI service

### Frontend (Netlify)
- `NEXT_PUBLIC_API_URL`: Backend API URL (set in netlify.toml)

## Post-Deployment Steps

1. **Update API URL** (if different)
   - If your Render service gets a different URL, update `NEXT_PUBLIC_API_URL` in netlify.toml
   - Redeploy the frontend

2. **Test the Application**
   - Visit your Netlify frontend URL
   - Test file upload functionality
   - Test chat functionality
   - Verify all API calls work correctly

3. **Monitor Logs**
   - Check Render logs for backend issues
   - Check Netlify build logs for frontend issues

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Ensure environment variables are set correctly
- Verify Python dependencies in requirements.txt

### Frontend Issues
- Check Netlify build logs
- Ensure API URL is correct
- Verify CORS configuration in backend

### API Connection Issues
- Check network requests in browser DevTools
- Verify backend health endpoint: `https://cq-lite-backend.onrender.com/api/health`
- Ensure CORS allows your frontend domain

## File Structure for Deployment

```
├── requirements.txt          # Python dependencies (generated)
├── render.yaml              # Render deployment config
├── netlify.toml             # Netlify deployment config
├── api/
│   ├── main.py              # FastAPI application
│   └── ...                  # Other API files
└── frontend/
    ├── package.json         # Node.js dependencies
    ├── next.config.js       # Next.js config with static export
    └── ...                  # Other frontend files
```