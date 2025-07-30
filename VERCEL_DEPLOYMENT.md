# Vercel Deployment Guide

This guide explains how to properly deploy DevDocs AI to Vercel, avoiding the common configuration conflicts.

## 🚨 Important: Deployment Strategy

Due to Vercel's limitations with monorepo deployments, we recommend deploying the **frontend and backend separately**:

1. **Frontend**: Deploy to Vercel (Next.js)
2. **Backend**: Deploy to Railway, Render, or Vercel Functions

## 🚀 Option 1: Frontend Only on Vercel (Recommended)

### Step 1: Deploy Frontend to Vercel

1. **Connect Repository to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

3. **Environment Variables**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

### Step 2: Deploy Backend Separately

#### Option A: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy backend
cd backend
railway init
railway up
```

#### Option B: Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

#### Option C: Vercel Functions (Limited)
If you want to use Vercel Functions for the backend, you'll need to restructure the project.

## 🚀 Option 2: Vercel Functions (Advanced)

If you want to deploy both frontend and backend on Vercel, you need to restructure the project:

### Project Structure for Vercel Functions
```
your-project/
├── frontend/          # Next.js frontend
├── api/              # Vercel Functions
│   ├── ask.py        # /api/ask endpoint
│   ├── upload.py     # /api/upload endpoint
│   └── requirements.txt
└── vercel.json
```

### Updated vercel.json for Functions
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

## 🔧 Environment Configuration

### Frontend Environment Variables
```bash
# .env.local in frontend directory
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend Environment Variables
```bash
# Set in your backend deployment platform
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
```

## 🐛 Troubleshooting

### Common Vercel Errors

1. **"functions" and "builds" conflict**:
   - ✅ **Solution**: Remove the `functions` property from vercel.json
   - Use only `builds` for deployment configuration

2. **Python runtime issues**:
   - ✅ **Solution**: Ensure requirements.txt is in the correct location
   - Use `@vercel/python` builder

3. **Environment variables not found**:
   - ✅ **Solution**: Set environment variables in Vercel dashboard
   - Use `NEXT_PUBLIC_` prefix for client-side variables

4. **Build failures**:
   - ✅ **Solution**: Check build logs in Vercel dashboard
   - Ensure all dependencies are in requirements.txt

### Debug Commands
```bash
# Test build locally
cd frontend && npm run build

# Check Vercel configuration
vercel --debug

# View deployment logs
vercel logs
```

## 📋 Deployment Checklist

### Frontend (Vercel)
- [ ] Repository connected to Vercel
- [ ] Root directory set to `frontend`
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Domain configured

### Backend (Railway/Render)
- [ ] Backend deployed and accessible
- [ ] Environment variables set
- [ ] API endpoints responding
- [ ] CORS configured for frontend domain

### Integration
- [ ] Frontend can communicate with backend
- [ ] Supabase connection working
- [ ] File uploads functional
- [ ] Chat interface operational

## 🎯 Recommended Approach

For the best performance and reliability:

1. **Deploy frontend to Vercel** (Next.js optimized)
2. **Deploy backend to Railway** (Python optimized)
3. **Use Supabase** for database and auth
4. **Configure CORS** between frontend and backend

This approach gives you:
- ✅ Optimal performance for each platform
- ✅ Better scalability
- ✅ Easier debugging
- ✅ Cost-effective deployment

## 📞 Support

If you encounter issues:
1. Check the [Vercel Documentation](https://vercel.com/docs)
2. Review deployment logs in Vercel dashboard
3. Test locally before deploying
4. Create an issue in the repository

---

**Note**: The current project structure is optimized for separate deployments. If you need a single Vercel deployment, consider restructuring the project to use Vercel Functions. 