# FastAPI Agent Server

A production-level FastAPI server for user and agent management with MongoDB backend.

## Features

- **User Management**: Registration, authentication, profile management
- **Agent Management**: Create, update, delete, and search AI agents
- **JWT Authentication**: Secure token-based authentication
- **MongoDB Integration**: Async MongoDB operations with Motor
- **Production Ready**: Logging, error handling, CORS, health checks
- **Docker Support**: Complete containerization with Docker Compose
- **Comprehensive Testing**: Unit tests with pytest
- **API Documentation**: Auto-generated with FastAPI/OpenAPI

## Project Structure

```
fastapi-agent-server/
├── app/
│   ├── core/           # Core configuration and security
│   ├── database/       # Database connection and utilities
│   ├── models/         # Pydantic models for User and Agent
│   ├── routers/        # API route handlers
│   ├── schemas/        # Request/response schemas
│   ├── services/       # Business logic layer
│   └── utils/          # Utilities and middleware
├── tests/              # Test suite
├── docs/               # Documentation
├── main.py             # FastAPI application
├── run.py              # Production server script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
└── docker-compose.yml # Multi-container setup
```

## Models

### User Model

- First name, last name, email, username
- Secure password hashing with bcrypt
- Phone number (optional)
- Active status and verification flags
- List of associated agent IDs
- Timestamps for creation, updates, and last login

### Agent Model

- Name, description, and system prompt
- Provider configuration for TTS, STT, and LLM
- Feature flags (voice chat, text chat, file upload, etc.)
- Created by user (foreign key relationship)
- Active status and timestamps

## Quick Start

### Using Docker Compose (Recommended)

1. Clone and setup:

```bash
git clone <repository>
cd fastapi-agent-server
cp .env.example .env
# Edit .env with your configurations
```

2. Start services:

```bash
docker-compose up -d
```

3. Access the application:

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MongoDB Admin: http://localhost:8081

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start MongoDB:

```bash
# Using Docker
docker run -d -p 27017:27017 mongo:7

# Or install MongoDB locally
```

3. Set environment variables:

```bash
cp .env.example .env
# Edit .env file
```

4. Run the server:

```bash
python run.py
# Or for development with auto-reload:
uvicorn main:app --reload
```

## API Endpoints

### Authentication & Users

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `PUT /api/v1/auth/me` - Update current user
- `DELETE /api/v1/auth/me` - Delete current user

### Agents

- `POST /api/v1/agents/` - Create new agent
- `GET /api/v1/agents/` - Get user's agents
- `GET /api/v1/agents/{agent_id}` - Get specific agent
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `DELETE /api/v1/agents/{agent_id}` - Delete agent
- `GET /api/v1/agents/search?q=query` - Search agents
- `GET /api/v1/agents/stats` - Get agent statistics

## Example Usage

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "John",
       "last_name": "Doe",
       "email": "john@example.com",
       "username": "johndoe",
       "password": "securepassword123"
     }'
```

### Create an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My AI Assistant",
       "description": "A helpful AI assistant",
       "prompt": "You are a helpful AI assistant.",
       "provider_config": {
         "tts_provider": "openai",
         "stt_provider": "openai",
         "llm_provider": "openai"
       },
       "features": {
         "voice_chat": true,
         "text_chat": true,
         "memory": true
       }
     }'
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Production Deployment

1. Set strong secret keys in environment variables
2. Use proper MongoDB authentication
3. Configure CORS for your domain
4. Set up SSL/TLS certificates
5. Use a reverse proxy (nginx/caddy)
6. Monitor logs and metrics

## Environment Variables

Create a `.env` file with the following variables:

```env
APP_NAME=FastAPI Agent Server
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=agent_server_db
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- User permission checks
- SQL injection protection (NoSQL)
- Request logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
