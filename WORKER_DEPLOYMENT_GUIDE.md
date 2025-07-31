# Worker Deployment Guide

This guide explains how to deploy the document processing worker alongside your main API on Render.

## 🚨 Current Situation

Right now:
- ✅ **Main API** is deployed and working (handles immediate processing)
- ❌ **Kafka Worker** is not running (handles background processing)
- 🔍 **Kafka Connection Error** shows the worker isn't available

## 🚀 Deployment Options

### Option 1: Deploy Separate Worker Service on Render (Recommended)

Deploy the worker as a separate Render service:

#### Step 1: Create New Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Background Worker"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `devdocs-worker`
   - **Runtime**: `Python 3`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python embedding_worker.py`

#### Step 2: Set Environment Variables
Add the same environment variables as your main API:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key
OPENAI_API_KEY=your_openai_key
KAFKA_BOOTSTRAP_SERVERS=your_kafka_url
```

#### Step 3: Set Up Managed Kafka
Since Render doesn't provide Kafka, use a managed service:

**Option A: Upstash Kafka (Recommended)**
```bash
# Sign up at https://upstash.com/
# Create a Kafka cluster
# Get connection string like: kafka-abc123.upstash.io:9092
```

**Option B: Confluent Cloud**
```bash
# Sign up at https://confluent.cloud/
# Create cluster and get bootstrap servers
```

**Option C: CloudKarafka**
```bash
# Sign up at https://cloudkarafka.com/
# Create instance and get connection details
```

### Option 2: Use Redis Instead of Kafka (Simpler)

Replace Kafka with Redis for simpler deployment:

#### Step 1: Add Redis to Your Services
1. In Render Dashboard, add Redis service:
   - **Type**: Redis
   - **Name**: `devdocs-redis`
   - **Plan**: Starter

#### Step 2: Update API to Use Redis
```python
# In api.py, replace kafka_producer with redis_producer
from redis_producer import RedisProducer

# Replace this line:
# kafka_producer = KafkaProducer()
redis_producer = RedisProducer()

# In upload endpoint, replace:
# kafka_producer.send_message("api-doc-upload", kafka_event)
redis_producer.send_document_processing_message(doc_id, storage_path, doc_type, user_id, file.filename)
```

#### Step 3: Deploy Redis Worker
1. Create new Background Worker on Render
2. **Start Command**: `python redis_worker.py`
3. **Environment Variables**: Add `REDIS_URL` from your Redis service

### Option 3: Keep Immediate Processing Only

Since immediate processing is working, you can skip the worker entirely:

#### Pros:
- ✅ Simpler deployment
- ✅ No additional services needed
- ✅ Documents process immediately

#### Cons:
- ⚠️  No fallback if immediate processing fails
- ⚠️  API requests take longer (processing during upload)
- ⚠️  No background processing for large files

## 🔧 Quick Fix: Disable Kafka Errors

If you want to keep using immediate processing and ignore Kafka errors:

<function_calls>
<invoke name="read_file">
<parameter name="target_file">backend/api.py