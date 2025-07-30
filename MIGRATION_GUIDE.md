# Migration Guide: Hugging Face to OpenAI

This guide helps you migrate from Hugging Face Inference API back to OpenAI in DevDocs AI.

## 🔄 What Changed

### Dependencies
- **Removed**: `langchain-huggingface`, `huggingface_hub`, `sentence-transformers`
- **Added**: `langchain-openai`, `openai`

### Environment Variables
- **Removed**: `HUGGINGFACEHUB_API_TOKEN`
- **Added**: `OPENAI_API_KEY`

### Models
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` → `text-embedding-ada-002`
- **LLM**: `mistralai/Mistral-7B-Instruct-v0.2` → `gpt-3.5-turbo`

## 🚀 Migration Steps

### 1. Update Environment Variables

Edit your `.env` file:

```bash
# Remove this line:
# HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here

# Add this line:
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### 3. Update Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Test the Integration

```bash
cd backend
python test_openai.py
```

## 🔧 Configuration Options

### Changing the LLM Model

You can change the LLM model by editing `backend/rag_service.py`:

```python
self.llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # Change this
    temperature=0.2,
    max_tokens=1000
)
```

### Alternative Models

- `gpt-4` - More capable but more expensive
- `gpt-4-turbo` - Faster and more cost-effective
- `gpt-3.5-turbo-16k` - For longer conversations

### Changing Embeddings Model

OpenAI embeddings are automatically handled by the API, but you can specify the model:

```python
self.embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002"  # Default model
)
```

## 📊 Performance Comparison

| Aspect | Hugging Face | OpenAI |
|--------|--------------|--------|
| Embedding Dimension | 384 | 1536 |
| Embedding Speed | Moderate | Fast |
| LLM Response Time | Moderate | Fast |
| Cost | Free tier available | Per token |
| Model Control | Full control | Limited |
| Offline Capability | Yes | No |

## 🐛 Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Ensure `OPENAI_API_KEY` is set in `.env`
   - Verify the key is valid and has sufficient credits

2. **"Model not found"**
   - Check the `model_name` in `rag_service.py`
   - Ensure you have access to the specified model

3. **Rate limiting**
   - OpenAI has rate limits based on your plan
   - Consider implementing retry logic

4. **Embedding dimension mismatch**
   - If you have existing embeddings, they need to be regenerated
   - The vector dimension changed from 384 to 1536
   - Clear your `api_chunks` table and re-upload documents

### Regenerating Embeddings

If you have existing documents with Hugging Face embeddings:

```sql
-- Clear existing chunks (WARNING: This will delete all embeddings)
DELETE FROM api_chunks;

-- Re-upload your documents to regenerate embeddings
```

## 🔄 Rollback

If rollback is needed:
1. Restore original `requirements.txt`
2. Restore original `rag_service.py`
3. Set `HUGGINGFACEHUB_API_TOKEN` in `.env`
4. Remove `OPENAI_API_KEY`
5. Reinstall dependencies

## 📚 Documentation

- `README.md` - Updated with OpenAI integration details
- `PROJECT_SUMMARY.md` - Updated backend stack description
- `DOCKER_SETUP.md` - Updated Docker configuration 