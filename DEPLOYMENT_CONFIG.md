# Deployment Configuration Guide

This guide provides step-by-step instructions for configuring your DevDocs AI application with frontend on Vercel and backend on Render.

## 🚀 Deployment Architecture

```
┌─────────────────┐    API Calls    ┌─────────────────┐
│   Frontend      │ ──────────────► │    Backend      │
│   (Vercel)      │                 │   (Render)      │
│                 │                 │                 │
│ Next.js App     │                 │ FastAPI App     │
│ - Document Upload│                 │ - File Processing│
│ - Chat Interface│                 │ - RAG Pipeline  │
│ - User Auth     │                 │ - Database Ops  │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Supabase      │                 │   OpenAI        │
│   - Auth        │                 │   - Embeddings  │
│   - Database    │                 │   - LLM         │
│   - Storage     │                 └─────────────────┘
└─────────────────┘
```

## 📋 Prerequisites

- ✅ GitHub repository with your code
- ✅ Supabase project created
- ✅ OpenAI API key
- ✅ Vercel account
- ✅ Render account

## 🔧 Step 1: Supabase Setup

### 1.1 Create Supabase Project
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Note down your project URL and API keys

### 1.2 Run Database Migrations
```sql
-- Connect to your Supabase database and run:
CREATE EXTENSION IF NOT EXISTS vector;

-- Then run all migration files from supabase/migrations/
```

### 1.3 Create Storage Bucket
```sql
-- In Supabase SQL editor:
INSERT INTO storage.buckets (id, name, public) 
VALUES ('api-docs', 'api-docs', true);
```

## 🔧 Step 2: Backend Deployment (Render)

### 2.1 Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `devdocs-ai-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### 2.2 Set Environment Variables
Add these environment variables in Render:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Frontend URL (for CORS)
FRONTEND_URL=https://dev-docs-d6x8kasmn-omkar-ranes-projects.vercel.app

# Optional: Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### 2.3 Deploy Backend
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Note your backend URL: `https://your-service.onrender.com`

## 🔧 Step 3: Frontend Deployment (Vercel)

### 3.1 Connect Repository to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3.2 Set Environment Variables
Add these environment variables in Vercel:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Backend API URL (CRITICAL)
NEXT_PUBLIC_API_URL=https://your-service.onrender.com

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

### 3.3 Deploy Frontend
1. Click "Deploy"
2. Wait for deployment to complete
3. Your app will be available at: `https://your-project.vercel.app`

## 🔧 Step 4: Verify Configuration

### 4.1 Test Backend Health
```bash
curl https://your-service.onrender.com/
# Should return: {"message": "DevDocs AI API is running", "version": "1.0.0"}
```

### 4.2 Test Frontend-Backend Communication
1. Open your Vercel app
2. Try uploading a document
3. Check browser console for any CORS errors
4. Verify API calls are going to your Render backend

### 4.3 Check Environment Variables
In your browser console, verify:
```javascript
console.log(process.env.NEXT_PUBLIC_API_URL);
// Should show your Render backend URL
```

## 🔧 Step 5: Troubleshooting

### Common Issues

#### 1. CORS Errors
**Symptoms**: Browser console shows CORS errors
**Solution**: 
- Verify `FRONTEND_URL` is set correctly in Render
- Check that your Vercel domain is in the CORS allowlist

#### 2. API Connection Errors
**Symptoms**: 404 or connection refused errors
**Solution**:
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check that your Render service is running
- Ensure the backend URL is accessible

#### 3. Environment Variable Issues
**Symptoms**: "undefined" values in console
**Solution**:
- Redeploy after setting environment variables
- Verify variable names start with `NEXT_PUBLIC_` for frontend
- Check for typos in variable names

#### 4. Database Connection Issues
**Symptoms**: Supabase errors in backend logs
**Solution**:
- Verify Supabase credentials in Render
- Check that migrations have been run
- Ensure vector extension is enabled

### Debug Commands

#### Frontend Debug
```bash
# Check environment variables
echo $NEXT_PUBLIC_API_URL

# Test API connection
curl $NEXT_PUBLIC_API_URL/
```

#### Backend Debug
```bash
# Check environment variables
echo $FRONTEND_URL

# Test Supabase connection
python -c "from supabase_client import get_supabase_client; print('Supabase connected')"
```

## 🔧 Step 6: Production Optimization

### 1. Enable HTTPS
- ✅ Vercel provides HTTPS automatically
- ✅ Render provides HTTPS automatically

### 2. Set Up Monitoring
- Enable Vercel Analytics
- Set up error tracking (Sentry)
- Monitor Render service logs

### 3. Performance Optimization
- Enable caching in Vercel
- Optimize images and assets
- Monitor API response times

## 📊 Verification Checklist

- [ ] Backend deployed on Render and accessible
- [ ] Frontend deployed on Vercel and accessible
- [ ] Environment variables set correctly
- [ ] CORS configured properly
- [ ] Database migrations run
- [ ] Storage bucket created
- [ ] File uploads working
- [ ] Chat interface functional
- [ ] No console errors
- [ ] API calls going to correct backend

## 🎯 Next Steps

1. **Test all functionality**:
   - Document upload
   - Chat interface
   - User authentication
   - File processing

2. **Set up monitoring**:
   - Error tracking
   - Performance monitoring
   - Usage analytics

3. **Optimize performance**:
   - Caching strategies
   - CDN configuration
   - Database optimization

4. **Security review**:
   - API key security
   - CORS configuration
   - Input validation

Your DevDocs AI application should now be fully functional with frontend on Vercel and backend on Render! 🎉 