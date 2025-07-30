# DevDocs AI: RAG-Powered Developer Documentation Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/devdocs-ai)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/yourusername/devdocs-ai)

## 🚀 Live Demo

**[Try DevDocs AI Live](https://your-app.vercel.app)**

## 📖 Overview

DevDocs AI is an AI-powered tool that helps developers interact with large API specifications, SDK manuals, and technical documentation through a chat interface. It uses Retrieval-Augmented Generation (RAG) to combine the benefits of fast information retrieval and large language models.

### ✨ Key Features

- 📄 **Smart Document Upload**: Upload API specs (YAML/JSON), SDK PDFs, and Markdown docs
- 🤖 **RAG-Powered Q&A**: Ask questions like "What's the OAuth flow in v3?" and get intelligent answers
- 🔗 **Source Linking**: Every answer links back to the original documentation
- 🔍 **VSCode-style Search**: Fuzzy search and autocomplete for quick navigation
- 📊 **Feedback Loop**: Rate answers to improve quality over time
- 📈 **Analytics**: Query logs and usage analysis with Apache Spark
- 👥 **Multi-user Support**: Secure authentication and user management

---

## 🧱 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Supabase Auth** - Authentication and user management
- **Framer Motion** - Smooth animations

### Backend
- **FastAPI** - High-performance Python web framework
- **LangChain** - LLM orchestration and RAG pipeline
- **OpenAI** - Embeddings and LLM inference
- **Supabase** - Vector database (pgvector) and storage

### Infrastructure
- **Vercel** - Frontend deployment and hosting
- **Supabase** - Database, authentication, and storage
- **Docker** - Containerization for local development

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.9+
- Git
- Supabase account
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/devdocs-ai.git
cd devdocs-ai
```

### 2. Environment Setup

```bash
# Frontend
cd frontend
cp env.example .env.local
# Edit .env.local with your Supabase and OpenAI credentials

# Backend
cd ../backend
cp env.example .env
# Edit .env with your API keys
```

### 3. Install Dependencies

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### 4. Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the migrations in `supabase/migrations/`
3. Enable the vector extension: `CREATE EXTENSION IF NOT EXISTS vector;`

### 5. Start Development

```bash
# Frontend (http://localhost:3000)
cd frontend && npm run dev

# Backend (http://localhost:8000)
cd backend && uvicorn api:app --reload
```

---

## 🚀 Deployment

### Vercel Deployment (Recommended)

1. **Fork this repository**
2. **Deploy to Vercel**:
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/devdocs-ai)

3. **Configure Environment Variables** in Vercel:
   ```
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_api_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

### Manual Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

---

## 📁 Project Structure

```
devdocs-ai/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # App Router pages and layouts
│   ├── components/          # Reusable React components
│   ├── utils/              # Utility functions
│   └── package.json        # Frontend dependencies
├── backend/                 # FastAPI backend services
│   ├── api.py              # Main API endpoints
│   ├── rag_service.py      # RAG pipeline implementation
│   ├── supabase_client.py  # Database client
│   └── requirements.txt    # Python dependencies
├── supabase/               # Database migrations and setup
│   └── migrations/         # SQL migration files
├── docs/                   # Documentation
├── tests/                  # Test files
└── docker-compose.yml      # Local development setup
```

---

## 🔧 Configuration

### Environment Variables

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

#### Backend (.env)
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
```

### Database Configuration

The application uses Supabase with the following key features:
- **Vector Search**: pgvector extension for semantic search
- **Authentication**: Built-in user management
- **Storage**: File upload and management
- **Real-time**: Live updates and notifications

---

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Backend Tests
```bash
cd backend
pytest
pytest --cov=.
```

### Integration Tests
```bash
npm run test:integration
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `npm test && pytest`
5. Commit your changes: `git commit -m 'feat: add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Quality

We use several tools to maintain code quality:
- **Prettier** - Code formatting
- **ESLint** - JavaScript/TypeScript linting
- **Black** - Python code formatting
- **Flake8** - Python linting
- **MyPy** - Python type checking

---

## 📊 Analytics & Monitoring

### Built-in Analytics
- Query patterns and frequency
- Most accessed documentation sections
- User engagement metrics
- Performance monitoring

### Optional Spark Integration
For advanced analytics, you can enable Apache Spark:
- Query pattern analysis
- Documentation coverage metrics
- Performance optimization insights

---

## 🔒 Security

- **Authentication**: Supabase Auth with secure session management
- **API Security**: Rate limiting and input validation
- **Data Protection**: Environment variables for sensitive data
- **CORS**: Properly configured for production domains

---

## 📈 Performance

### Optimizations
- **Vector Search**: Optimized embeddings for fast retrieval
- **Caching**: Intelligent caching of frequent queries
- **CDN**: Global content delivery via Vercel
- **Database**: Optimized indexes and query patterns

### Benchmarks
- **Query Response**: < 2 seconds average
- **Document Processing**: < 30 seconds for 10MB files
- **Concurrent Users**: 100+ simultaneous users

---

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check environment variables are set correctly
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **API Connection Issues**
   - Verify CORS settings
   - Check API endpoints are accessible
   - Ensure environment variables are correct

3. **Database Connection**
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure migrations are run

### Getting Help

- 📖 [Documentation](./docs/)
- 🐛 [GitHub Issues](https://github.com/yourusername/devdocs-ai/issues)
- 💬 [GitHub Discussions](https://github.com/yourusername/devdocs-ai/discussions)
- 📧 [Email Support](mailto:support@devdocs-ai.com)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for providing the LLM capabilities
- **Supabase** for the excellent database and auth platform
- **Vercel** for seamless deployment and hosting
- **LangChain** for the RAG framework
- **Next.js** for the amazing React framework

---

## 📞 Support

- **Documentation**: [docs.devdocs-ai.com](https://docs.devdocs-ai.com)
- **Community**: [GitHub Discussions](https://github.com/yourusername/devdocs-ai/discussions)
- **Issues**: [GitHub Issues](https://github.com/yourusername/devdocs-ai/issues)
- **Email**: support@devdocs-ai.com

---

<div align="center">

**Made with ❤️ by the DevDocs AI Team**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/devdocs-ai?style=social)](https://github.com/yourusername/devdocs-ai)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/devdocs-ai?style=social)](https://github.com/yourusername/devdocs-ai)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/devdocs-ai)](https://github.com/yourusername/devdocs-ai/issues)

</div> 