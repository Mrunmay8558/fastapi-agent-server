# FastAPI MongoDB Project - Restructured

This project has been completely restructured to follow the [MongoDB Labs Full-Stack FastAPI MongoDB Template](https://github.com/mongodb-labs/full-stack-fastapi-mongodb) best practices and patterns.

## 🚀 Major Improvements

### 1. **Modern Database Architecture**
- **ODMantic Integration**: Replaced basic PyMongo/Motor with ODMantic ODM for better type safety and automatic serialization
- **Generic CRUD Operations**: Implemented inheritance-based CRUD operations following the template pattern
- **Database Dependency Injection**: Proper FastAPI dependency injection for database operations
- **Automatic Indexing**: Database initialization script with proper indexes for performance

### 2. **Enhanced Project Structure**
```
fastapi-agent-server/
├── app/
│   ├── crud/                 # Generic and specific CRUD operations
│   │   ├── base.py          # Generic CRUD base class
│   │   ├── crud_user.py     # User-specific CRUD operations
│   │   └── crud_agent.py    # Agent-specific CRUD operations
│   ├── models/              # ODMantic data models
│   │   ├── user.py          # User ODMantic model
│   │   └── agent.py         # Agent ODMantic model
│   ├── schemas/             # Pydantic schemas for API
│   │   ├── user.py          # User API schemas
│   │   ├── agent.py         # Agent API schemas
│   │   └── token.py         # Authentication schemas
│   ├── routers/             # FastAPI route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management endpoints
│   │   └── agents.py        # Agent management endpoints
│   ├── core/                # Core functionality
│   │   ├── config.py        # Enhanced configuration with security
│   │   └── security.py      # JWT authentication and dependencies
│   └── database/            # Database configuration and initialization
│       ├── mongodb.py       # ODMantic engine configuration
│       └── init_db.py       # Database initialization script
```

### 3. **Advanced Authentication & Security**
- **OAuth2 with JWT**: Production-ready token authentication
- **Role-based Access Control**: Superuser and regular user permissions
- **Secure Password Hashing**: bcrypt password hashing
- **Token Validation**: Proper JWT token validation and user session management

### 4. **API Architecture Improvements**
- **API Versioning**: Proper `/api/v1/` prefix structure
- **Response Models**: Comprehensive Pydantic schemas for all endpoints
- **Error Handling**: Standardized HTTP exception handling
- **Documentation**: Auto-generated OpenAPI documentation

### 5. **Database Features**
- **Soft Deletes**: Users and agents are deactivated instead of hard deleted
- **Timestamps**: Automatic created_at and updated_at tracking
- **Relationships**: Proper ObjectId references between users and agents
- **Indexing**: Performance-optimized database indexes
- **Validation**: Field-level validation with custom validators

## 🛠 Technical Stack

- **FastAPI 0.104.1**: Modern async web framework
- **ODMantic 1.0.2**: MongoDB ODM with Pydantic integration
- **Motor 3.3.2**: Async MongoDB driver
- **Pydantic 2.9.2**: Data validation and serialization
- **JWT Authentication**: python-jose with cryptography
- **Password Hashing**: passlib with bcrypt

## 🚦 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```env
# App Settings
APP_NAME="FastAPI Agent Server"
DEBUG=False
SECRET_KEY="your-secret-key-here"

# Database
MONGODB_URL="mongodb://localhost:27017"
DATABASE_NAME="agent_server_db"

# First Superuser
FIRST_SUPERUSER_EMAIL="admin@example.com"
FIRST_SUPERUSER_USERNAME="admin"
FIRST_SUPERUSER_PASSWORD="changethis"
```

### 3. Initialize Database
```bash
python app/database/init_db.py
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login/access-token` - Login and get JWT token
- `POST /api/v1/auth/test-token` - Test token validity

### Users
- `POST /api/v1/users/register` - Register new user
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/` - List users (superuser only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user (superuser only)

### Agents
- `POST /api/v1/agents/` - Create new agent
- `GET /api/v1/agents/` - List user's agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `PUT /api/v1/agents/{agent_id}` - Update agent
- `DELETE /api/v1/agents/{agent_id}` - Delete agent (soft delete)

## 🔧 CRUD Operations

The application now uses generic CRUD operations with inheritance:

```python
# Example usage
from app import crud
from app.database.mongodb import get_engine

engine = await get_engine()

# Create user
user = await crud.user.create(engine, obj_in=user_data)

# Get user by email
user = await crud.user.get_by_email(engine, email="user@example.com")

# Update user
updated_user = await crud.user.update(engine, db_obj=user, obj_in=update_data)

# Delete user (soft delete)
await crud.user.remove(engine, id=user.id)
```

## 🔒 Security Features

- **JWT Token Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing
- **Field Validation**: Pydantic field validation with custom validators
- **CORS Support**: Configurable CORS settings
- **Rate Limiting Ready**: Structure ready for rate limiting middleware

## 📊 Database Schema

### User Model
- Email and username uniqueness
- Password hashing
- User roles (superuser/regular)
- Agent associations
- Activity tracking

### Agent Model  
- Provider configurations (TTS, STT, LLM)
- Feature toggles
- Owner relationships
- Soft delete capability
- Search indexing

## 🎯 Key Benefits

1. **Production Ready**: Follows industry best practices and MongoDB Labs template
2. **Type Safety**: Full TypeScript-like type safety with Pydantic and ODMantic
3. **Scalable Architecture**: Generic CRUD operations and modular structure
4. **Performance Optimized**: Database indexing and async operations
5. **Security First**: Comprehensive authentication and validation
6. **Developer Experience**: Auto-generated docs and clear error messages

## 📖 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health