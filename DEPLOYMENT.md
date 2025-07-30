# Deployment Guide: GitHub + Vercel

This guide will help you deploy DevDocs AI to GitHub and Vercel for production use.

## 🚀 Quick Deployment Steps

### 1. GitHub Repository Setup

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DevDocs AI project"
   ```

2. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com) and create a new repository
   - Name it `devdocs-ai` or your preferred name
   - Make it public or private as needed

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/devdocs-ai.git
   git branch -M main
   git push -u origin main
   ```

### 2. Vercel Deployment

#### Option A: Deploy Frontend Only (Recommended)

1. **Connect Repository**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Select the repository you just created

2. **Configure Project Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

3. **Environment Variables**:
   Add the following environment variables in Vercel:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete
   - Your frontend will be available at `https://your-project.vercel.app`

**Note**: This deploys only the frontend. You'll need to deploy the backend separately (see Backend API Deployment section below).

#### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Set environment variables
   - Deploy

### 3. Backend API Deployment

For the backend API, you have several options:

#### Option A: Vercel Functions (Recommended for MVP)

1. **Deploy Backend to Vercel**:
   ```bash
   cd backend
   vercel
   ```

2. **Update Frontend API Calls**:
   Update your frontend to use the Vercel function URL:
   ```typescript
   const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-backend.vercel.app';
   ```

#### Option B: Railway/Render (For Production)

1. **Railway Deployment**:
   - Connect your GitHub repo to Railway
   - Set environment variables
   - Deploy the backend directory

2. **Render Deployment**:
   - Create a new Web Service on Render
   - Connect your GitHub repo
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

## 🔧 Environment Configuration

### Required Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Backend API URL (if deployed separately)
NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

### Vercel Environment Variables

Set these in your Vercel project settings:

1. Go to your project dashboard
2. Navigate to Settings → Environment Variables
3. Add each variable with appropriate values

## 📊 Database Setup

### Supabase Setup

1. **Create Supabase Project**:
   - Go to [Supabase](https://supabase.com)
   - Create a new project
   - Note down your project URL and API keys

2. **Run Migrations**:
   ```bash
   # Connect to your Supabase database
   psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
   
   # Run the migration files
   \i supabase/migrations/001_initial_schema.sql
   \i supabase/migrations/002_fix_vector_search.sql
   \i supabase/migrations/003_complete_setup.sql
   \i supabase/migrations/004_add_missing_fields.sql
   \i supabase/migrations/005_fix_vector_dimensions.sql
   \i supabase/migrations/006_revert_to_openai.sql
   ```

3. **Enable Vector Extension**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## 🔒 Security Considerations

### API Key Security

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** for production use
4. **Use service role keys** only on the backend

### CORS Configuration

Update your backend CORS settings for production:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.vercel.app",
        "http://localhost:3000"  # For development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Production Optimization

### Frontend Optimization

1. **Enable Compression**:
   ```javascript
   // next.config.js
   const nextConfig = {
     compress: true,
     // ... other config
   }
   ```

2. **Optimize Images**:
   ```javascript
   // next.config.js
   const nextConfig = {
     images: {
       formats: ['image/webp', 'image/avif'],
       // ... other config
     }
   }
   ```

### Backend Optimization

1. **Add Caching**:
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.redis import RedisBackend
   
   FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
   ```

2. **Rate Limiting**:
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

## 📈 Monitoring & Analytics

### Vercel Analytics

1. **Enable Vercel Analytics**:
   - Go to your project settings
   - Enable Analytics
   - Add the tracking code to your app

### Error Monitoring

1. **Sentry Integration**:
   ```bash
   npm install @sentry/nextjs
   ```

2. **Configure Sentry**:
   ```javascript
   // sentry.client.config.js
   import * as Sentry from "@sentry/nextjs";
   
   Sentry.init({
     dsn: "your-sentry-dsn",
     tracesSampleRate: 1.0,
   });
   ```

## 🔄 Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check environment variables are set correctly
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **API Connection Issues**:
   - Verify CORS settings
   - Check API endpoints are accessible
   - Ensure environment variables are correct

3. **Database Connection**:
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure migrations are run

### Debug Commands

```bash
# Check build locally
npm run build

# Test API locally
cd backend && uvicorn api:app --reload

# Check environment variables
vercel env ls

# View deployment logs
vercel logs
```

## 📞 Support

If you encounter issues:

1. Check the [Vercel Documentation](https://vercel.com/docs)
2. Review [Supabase Documentation](https://supabase.com/docs)
3. Check GitHub Issues for similar problems
4. Create an issue in the repository

---

## ✅ Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] Environment variables configured
- [ ] Supabase database set up with migrations
- [ ] Frontend deployed to Vercel
- [ ] Backend API deployed
- [ ] CORS settings configured
- [ ] Domain configured (if using custom domain)
- [ ] SSL certificate active
- [ ] Monitoring and analytics set up
- [ ] Error tracking configured
- [ ] Performance optimization applied

Your DevDocs AI application should now be live and ready for production use! 🎉 