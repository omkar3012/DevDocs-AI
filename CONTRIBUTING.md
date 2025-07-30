# Contributing to DevDocs AI

Thank you for your interest in contributing to DevDocs AI! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git
- Docker (optional, for local development)

### Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/devdocs-ai.git
   cd devdocs-ai
   ```

2. **Install Dependencies**:
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   ```bash
   # Frontend
   cd frontend
   cp env.example .env.local
   # Edit .env.local with your values
   
   # Backend
   cd ../backend
   cp env.example .env
   # Edit .env with your values
   ```

4. **Database Setup**:
   - Create a Supabase project
   - Run the migrations in `supabase/migrations/`
   - Update environment variables

## 🛠️ Development Workflow

### Code Style

#### Frontend (TypeScript/React)
- Use TypeScript for all new code
- Follow ESLint configuration
- Use Prettier for formatting
- Write meaningful component and function names
- Add JSDoc comments for complex functions

#### Backend (Python/FastAPI)
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public functions
- Use async/await for I/O operations

### Git Workflow

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**:
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit Your Changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and Create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create Pull Request on GitHub
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm run test
npm run test:watch
```

### Backend Testing
```bash
cd backend
python -m pytest
python -m pytest --cov=.
```

### Integration Testing
```bash
# Run the full test suite
npm run test:integration
```

## 📝 Documentation

### Code Documentation
- Add JSDoc comments for TypeScript functions
- Add docstrings for Python functions
- Include examples for complex APIs

### README Updates
- Update README.md for new features
- Add setup instructions for new dependencies
- Update deployment guides if needed

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - OS and version
   - Node.js version
   - Python version
   - Browser (if applicable)

2. **Steps to Reproduce**:
   - Clear, step-by-step instructions
   - Sample data if applicable

3. **Expected vs Actual Behavior**:
   - What you expected to happen
   - What actually happened

4. **Additional Context**:
   - Screenshots if applicable
   - Error messages
   - Console logs

## 💡 Feature Requests

When suggesting features:

1. **Describe the Problem**:
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Propose a Solution**:
   - How should this feature work?
   - Any technical considerations?

3. **Consider Alternatives**:
   - Are there existing solutions?
   - Could this be implemented differently?

## 🔧 Local Development

### Running the Application

1. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   # Available at http://localhost:3000
   ```

2. **Start Backend**:
   ```bash
   cd backend
   uvicorn api:app --reload
   # Available at http://localhost:8000
   ```

3. **Start with Docker**:
   ```bash
   docker-compose up --build
   ```

### Database Development

1. **Local Supabase**:
   ```bash
   # Install Supabase CLI
   npm install -g supabase
   
   # Start local Supabase
   supabase start
   ```

2. **Run Migrations**:
   ```bash
   supabase db reset
   ```

## 📊 Performance Guidelines

### Frontend
- Use React.memo for expensive components
- Implement proper loading states
- Optimize bundle size
- Use lazy loading for routes

### Backend
- Implement proper caching
- Use database indexes
- Optimize database queries
- Add rate limiting

## 🔒 Security Guidelines

- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication
- Follow OWASP guidelines

## 🚀 Deployment

### Testing Before Deployment
```bash
# Frontend
cd frontend
npm run build
npm run test

# Backend
cd backend
python -m pytest
```

### Deployment Checklist
- [ ] All tests pass
- [ ] Code is linted and formatted
- [ ] Documentation is updated
- [ ] Environment variables are configured
- [ ] Database migrations are ready

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the project's coding standards

### Communication
- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Be clear and concise in communications
- Provide context when asking for help

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and other docs first
- **Code Examples**: Look at existing code for patterns

## 🎉 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Project README (for significant contributions)
- Release notes

Thank you for contributing to DevDocs AI! 🚀 