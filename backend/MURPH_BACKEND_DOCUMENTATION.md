# Murph Backend Repository Documentation

## Overview

Murph is an AI-assisted pay-per-use learning marketplace backend built with FastAPI. It allows students to pay only for the time they actually spend watching course videos, with real-time session metering via WebSockets, AI-powered course discovery, and credibility-based review validation.

## Project Structure

```
murph-backend/
├── README.md                           # Project overview and setup
├── requirements.txt                    # Python dependencies
├── app/
│   ├── main.py                         # FastAPI application entry point
│   ├── config.py                       # Application configuration
│   ├── dependencies.py                 # Dependency injection
│   ├── __init__.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── router.py               # Main API router
│   │   │   ├── auth.py                 # Authentication endpoints
│   │   │   ├── users.py                # User management
│   │   │   ├── courses.py              # Course CRUD operations
│   │   │   ├── videos.py               # Video management
│   │   │   ├── discovery.py            # AI-powered course discovery
│   │   │   ├── wallet.py               # Wallet operations
│   │   │   ├── sessions.py             # Learning session management
│   │   │   ├── payments.py             # Payment operations
│   │   │   ├── reviews.py              # Review system
│   │   │   ├── teacher.py              # Teacher dashboard
│   │   │   └── __init__.py
│   │   └── websocket/
│   │       ├── session_metering.py     # WebSocket metering
│   │       └── __init__.py
│   ├── core/
│   │   ├── security.py                 # JWT token handling
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── constants.py                # Application constants
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py                     # User data models
│   │   ├── course.py                   # Course and video models
│   │   ├── session.py                  # Session models
│   │   ├── payment.py                  # Payment models
│   │   ├── review.py                   # Review models
│   │   ├── discovery.py                # Discovery models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py                     # Authentication schemas
│   │   ├── user.py                     # User schemas
│   │   ├── course.py                   # Course schemas
│   │   ├── session.py                  # Session schemas
│   │   ├── payment.py                  # Payment schemas
│   │   ├── review.py                   # Review schemas
│   │   ├── discovery.py                # Discovery schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py             # Authentication business logic
│   │   ├── course_service.py           # Course management logic
│   │   ├── discovery_service.py        # AI discovery logic
│   │   ├── payment_service.py          # Payment processing logic
│   │   ├── review_service.py           # Review processing logic
│   │   ├── session_service.py          # Session management logic
│   │   ├── teacher_service.py          # Teacher dashboard logic
│   │   └── __init__.py
│   ├── integrations/
│   │   ├── ai_client.py                # AI provider integration
│   │   ├── finternet_client.py         # Payment gateway integration
│   │   ├── supabase_client.py          # Database and storage client
│   │   ├── supabase_storage.py         # Storage utilities
│   │   └── __init__.py
│   ├── utils/
│   │   ├── credibility.py              # Review credibility calculation
│   │   ├── helpers.py                  # Utility functions
│   │   └── __init__.py
├── migrations/
│   └── 001_initial_schema.sql          # Database schema
├── tests/
│   └── __init__.py                     # Test files (empty)
└── .env.example                        # Environment variables template
```

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs with Python 3.10+
- **Uvicorn**: ASGI server for running FastAPI applications
- **Pydantic**: Data validation and serialization

### Database & Storage
- **Supabase**: PostgreSQL database with real-time capabilities
- **Supabase Storage**: File storage for course videos

### Authentication & Security
- **JWT (JSON Web Tokens)**: Token-based authentication
- **PassLib with bcrypt**: Password hashing
- **OAuth2**: Token-based authorization

### Real-time Features
- **WebSockets**: Real-time session metering
- **Async/Await**: Asynchronous operations throughout

### AI Integration
- **OpenAI**: GPT models for AI discovery
- **Anthropic Claude**: Alternative AI provider
- **Google Gemini**: Additional AI provider
- **Groq**: Fast inference AI provider

### Payments
- **Finternet**: Custom payment gateway for micro-payments and fund locking

### Additional Libraries
- **httpx**: Async HTTP client for external API calls
- **websockets**: WebSocket client/server library
- **python-multipart**: File upload handling
- **python-dotenv**: Environment variable management
- **uuid7**: UUID generation
- **aiofiles**: Async file operations

## Dependencies (requirements.txt)

```
fastapi==0.115.6
uvicorn[standard]==0.32.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.17
supabase==2.10.0
httpx==0.27.2
websockets==13.1
pydantic[email]==2.10.3
pydantic-settings==2.7.0
python-dotenv==1.0.1
openai==1.58.1
anthropic==0.40.0
google-generativeai==0.8.3
groq==0.13.0
aiofiles==24.1.0
uuid7==0.1.0
```

## Configuration

### Environment Variables (.env)

```bash
# App settings
APP_NAME=Murph
DEBUG=true

# Supabase settings
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Finternet settings
FINTERNET_API_URL=https://api.finternetlab.io
FINTERNET_API_KEY=your_finternet_api_key
FINTERNET_WEBHOOK_SECRET=your_webhook_secret

# AI settings (choose one)
OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key
# GOOGLE_AI_API_KEY=your_google_key
# GROQ_API_KEY=your_groq_key

# Session settings
DEFAULT_LOCK_AMOUNT=30.00
MIN_SESSION_DURATION_SECONDS=60
METERING_UPDATE_INTERVAL_SECONDS=5
```

### Application Configuration (config.py)

The configuration uses Pydantic Settings for type-safe environment variable handling:

- App settings: name, debug mode, secret keys
- Database: Supabase connection details
- Payments: Finternet API configuration
- AI: Multiple provider support with automatic selection
- Sessions: Metering and locking parameters

## Database Schema

### Tables Overview

1. **users**: User accounts (students/teachers)
2. **categories**: Course categories
3. **courses**: Course metadata
4. **course_videos**: Individual video files
5. **sessions**: Learning sessions with metering
6. **session_video_progress**: Video watching progress
7. **transactions**: Payment transactions
8. **reviews**: Course reviews with credibility
9. **teacher_earnings**: Teacher payment records
10. **discovery_chat_history**: AI chat conversations

### Key Relationships

- Users → Courses (teacher_id)
- Courses → Course Videos (course_id)
- Users → Sessions (student_id)
- Courses → Sessions (course_id)
- Sessions → Session Video Progress
- Sessions → Transactions
- Sessions → Reviews (unique)
- Sessions → Teacher Earnings

### Database Migration (001_initial_schema.sql)

Complete PostgreSQL schema with:
- UUID primary keys
- Foreign key constraints
- Indexes for performance
- Default categories insertion
- JSONB for flexible metadata

## Data Models

### User Models (models/user.py)

**UserBase**: Common user fields (email, name, type, wallet)
**UserCreate**: Registration data
**UserUpdate**: Profile update fields
**UserInDB**: Database representation with hash
**User**: Public user data
**UserProfile**: Extended profile (same as User)

### Course Models (models/course.py)

**CategoryBase**: Category name and description
**CourseBase**: Course metadata (title, description, price)
**CourseCreate/Update**: CRUD operations
**Course**: Full course data with stats
**CourseWithDetails**: Course with teacher/category names
**CourseVideoBase**: Video metadata
**CourseVideo**: Video with URLs
**CourseVideoWithUrl**: Video with signed URLs

### Session Models (models/session.py)

**SessionBase**: Basic session (course_id)
**SessionCreate/Update**: Session operations
**Session**: Full session data with costs
**SessionWithDetails**: Session with names
**SessionVideoProgress**: Individual video progress
**SessionMeteringUpdate**: Real-time metering data

### Payment Models (models/payment.py)

**TransactionBase**: Transaction metadata
**Transaction**: Full transaction record
**WalletBalance**: Wallet balance info
**LockFundsRequest/Result**: Fund locking
**SettlementRequest/Result**: Payment settlement
**BonusPaymentRequest/Result**: Quality bonuses

### Review Models (models/review.py)

**ReviewBase**: Basic review (rating, text)
**Review**: Full review with credibility
**ReviewWithDetails**: Review with names
**CredibilityCalculation**: Credibility computation

### Discovery Models (models/discovery.py)

**ChatMessage**: AI conversation messages
**DiscoveryChatRequest/Response**: Chat API
**DiscoveryChatHistory**: Chat history

## API Schemas

### Authentication Schemas (schemas/auth.py)

**LoginRequest**: Email/password
**TokenResponse**: JWT tokens
**RegisterRequest**: Registration data
**UserProfileResponse**: User profile
**UpdateProfileRequest**: Profile updates

### Course Schemas (schemas/course.py)

**CategoryResponse**: Category data
**CourseCreateRequest/UpdateRequest**: CRUD requests
**CourseResponse**: Full course data
**CourseListResponse**: Paginated courses
**CourseVideoUploadRequest**: Video upload
**CourseVideoResponse**: Video data
**SignedUrlResponse**: Signed URLs

### Session Schemas (schemas/session.py)

**SessionStartRequest/Response**: Session initiation
**SessionEndRequest/Response**: Session completion
**SessionResponse**: Session data
**SessionListResponse**: Session lists
**ActiveSessionResponse**: Current session
**SessionMeteringUpdate**: Metering updates

### Payment Schemas (schemas/payment.py)

**WalletConnectRequest**: Wallet connection
**WalletBalanceResponse**: Balance info
**TransactionResponse**: Transaction data
**TransactionListResponse**: Transaction lists

### Review Schemas (schemas/review.py)

**ReviewCreateRequest**: Review submission
**ReviewResponse**: Full review
**ReviewListResponse**: Review lists

### Discovery Schemas (schemas/discovery.py)

**DiscoveryChatRequest/Response**: AI chat
**SuggestedCourse**: Course suggestions
**ChatMessageResponse**: Chat messages
**DiscoveryChatHistoryResponse**: Chat history

## Business Logic Services

### Authentication Service (services/auth_service.py)

**register_user()**: User registration with password hashing
**authenticate_user()**: Login verification
**create_tokens()**: JWT token generation
**refresh_access_token()**: Token refresh
**get_current_user()**: User retrieval
**update_user_profile()**: Profile updates

### Course Service (services/course_service.py)

**create_course()**: Course creation
**get_course()**: Course retrieval with joins
**update_course()**: Course updates
**delete_course()**: Course deletion
**list_courses()**: Course listing with filters
**add_video_to_course()**: Video addition
**get_course_videos()**: Video listing
**generate_signed_url()**: Video access URLs

### Session Service (services/session_service.py)

**start_session()**: Session initialization with fund locking
**end_session()**: Session completion with settlement
**get_session()**: Session retrieval
**list_user_sessions()**: Session history
**update_session_progress()**: Progress tracking
**get_active_session()**: Current session check

### Payment Service (services/payment_service.py)

**lock_funds()**: Fund locking for sessions
**settle_payment()**: Payment distribution
**process_quality_bonus()**: Bonus payments
**get_wallet_balance()**: Balance checking
**get_transaction_history()**: Transaction listing

### Review Service (services/review_service.py)

**create_review()**: Review creation with credibility
**get_reviews_for_course()**: Course reviews
**calculate_credibility()**: Credibility scoring
**process_quality_bonus()**: Bonus calculation

### Discovery Service (services/discovery_service.py)

**chat_with_ai()**: AI conversation
**get_course_suggestions()**: Course recommendations
**save_chat_message()**: Chat persistence
**get_chat_history()**: Chat retrieval

### Teacher Service (services/teacher_service.py)

**get_teacher_dashboard()**: Dashboard data
**get_teacher_earnings()**: Earnings history
**get_teacher_courses()**: Course management
**get_teacher_reviews()**: Review analytics

## External Integrations

### Supabase Client (integrations/supabase_client.py)

**SupabaseClient**: Regular client for user operations
**SupabaseServiceClient**: Service client for admin operations
**SupabaseStorageClient**: File storage operations
- upload_video(): File uploads
- get_signed_url(): Secure access URLs
- delete_video(): File deletion

### Finternet Client (integrations/finternet_client.py)

**FinternetClient**: Payment gateway integration
- get_wallet_balance(): Balance checking
- lock_funds(): Fund reservation
- settle_payment(): Payment processing
- process_quality_bonus(): Bonus payments
- verify_webhook_signature(): Webhook validation

### AI Client (integrations/ai_client.py)

**AIClient**: Multi-provider AI integration
Supports: OpenAI, Anthropic, Google, Groq
- chat_completion(): Text generation
- Automatic provider selection based on available keys

## Utility Functions

### Credibility Calculation (utils/credibility.py)

**calculate_review_credibility()**: 
- Engagement depth (40%): Watch percentage
- Rating-behavior consistency (35%): Rating vs engagement
- Session duration (15%): Time spent
- Video coverage (10%): Videos watched

**calculate_quality_bonus()**: 
- Bonus for credible positive reviews
- 5-15% of base payment based on credibility

### Helpers (utils/helpers.py)

**generate_uuid()**: UUID generation
**format_datetime()**: ISO formatting
**calculate_watch_percentage()**: Progress calculation
**calculate_session_cost()**: Cost computation
**validate_user_type()**: Type validation
**validate_rating()**: Rating validation
**paginate_results()**: List pagination

## API Endpoints

### Authentication (/api/v1/auth)

**POST /register**: User registration
**POST /login**: User login
**POST /refresh**: Token refresh
**GET /me**: Current user profile
**PUT /me**: Update profile

### Users (/api/v1/users)

**GET /{user_id}**: Get user profile
**PUT /{user_id}**: Update user (admin)

### Courses (/api/v1/courses)

**POST /**: Create course
**GET /**: List courses (with filters)
**GET /{course_id}**: Get course details
**PUT /{course_id}**: Update course
**DELETE /{course_id}**: Delete course
**POST /{course_id}/videos**: Add video
**GET /{course_id}/videos**: List videos
**GET /{course_id}/videos/{video_id}/url**: Get signed URL

### Sessions (/api/v1/sessions)

**POST /start**: Start session
**POST /{session_id}/end**: End session
**GET /{session_id}**: Get session
**GET /**: List user sessions
**GET /active**: Get active session

### Payments (/api/v1/payments)

**POST /wallet/connect**: Connect wallet
**GET /wallet/balance**: Get balance
**GET /transactions**: List transactions

### Reviews (/api/v1/reviews)

**POST /courses/{course_id}/reviews**: Create review
**GET /courses/{course_id}/reviews**: List reviews

### Discovery (/api/v1/discovery)

**POST /chat**: AI chat
**GET /chat/history**: Chat history

### Teacher (/api/v1/teacher)

**GET /dashboard**: Teacher dashboard
**GET /earnings**: Earnings history
**GET /courses**: Teacher courses
**GET /reviews**: Teacher reviews

## WebSocket Endpoints

### Session Metering (/ws/session/{session_id})

Real-time session metering with:
- Connection authentication
- Progress updates every 5 seconds
- Cost calculation
- Video progress tracking
- Automatic session ending on disconnect

## Core Components

### Security (core/security.py)

**JWT Operations**:
- create_access_token(): Access token creation
- create_refresh_token(): Refresh token creation
- verify_token(): Token validation

**Password Operations**:
- get_password_hash(): Password hashing
- verify_password(): Password verification

### Exceptions (core/exceptions.py)

**Custom Exceptions**:
- AuthenticationError: Login/authorization failures
- NotFoundError: Resource not found
- AuthorizationError: Permission denied
- ValidationError: Input validation failures

### Constants (core/constants.py)

**User Types**: student, teacher
**Session Statuses**: active, completed, cancelled
**Transaction Types**: lock, payment, refund, quality_bonus
**Transaction Statuses**: pending, completed, failed
**Chat Roles**: user, assistant
**Default Categories**: Programming, Data Science, etc.

## Testing

### Test Structure
- Unit tests for services
- Integration tests for API endpoints
- WebSocket tests for real-time features
- Database tests with test fixtures

### Test Commands
```bash
pytest                    # Run all tests
pytest tests/test_auth.py # Run specific test file
pytest -v                # Verbose output
pytest --cov=app         # Coverage report
```

## Deployment

### Production Considerations

1. **Environment Variables**: Secure key management
2. **Database**: Connection pooling, migrations
3. **Caching**: Redis for session data
4. **Load Balancing**: Multiple app instances
5. **Monitoring**: Logging, metrics, health checks
6. **Security**: HTTPS, CORS configuration
7. **File Storage**: CDN for video delivery

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Scaling Considerations

- **Horizontal Scaling**: Stateless FastAPI instances
- **Database Scaling**: Read replicas, connection pooling
- **Storage Scaling**: CDN integration
- **WebSocket Scaling**: Redis pub/sub for broadcasting
- **AI Scaling**: Request queuing, caching

## Key Features Implementation

### Pay-Per-Use Billing

1. **Fund Locking**: Pre-authorize payment at session start
2. **Real-time Metering**: WebSocket updates every 5 seconds
3. **Cost Calculation**: Per-minute pricing
4. **Settlement**: Pay teacher, refund unused funds

### AI-Powered Discovery

1. **Multi-Provider Support**: OpenAI, Anthropic, Google, Groq
2. **Conversational Interface**: Chat-based course recommendations
3. **Context Awareness**: User preferences and history
4. **Course Matching**: Natural language processing

### Credibility-Based Reviews

1. **Multi-Factor Scoring**: Watch percentage, rating consistency, duration
2. **Quality Bonuses**: Additional payments for credible positive reviews
3. **Weighted Ratings**: Credibility-adjusted course ratings
4. **Fraud Prevention**: Suspicious review detection

### Real-Time Session Management

1. **WebSocket Connection**: Persistent metering connection
2. **Progress Tracking**: Video-level progress monitoring
3. **Automatic Ending**: Session cleanup on disconnect
4. **Cost Updates**: Live cost calculation and balance checking

## Security Measures

### Authentication
- JWT tokens with expiration
- Password hashing with bcrypt
- Refresh token rotation

### Authorization
- Role-based access (student/teacher)
- Resource ownership validation
- API endpoint protection

### Data Protection
- Input validation with Pydantic
- SQL injection prevention
- XSS protection

### Payment Security
- Fund locking to prevent overspending
- Webhook signature verification
- Secure API key management

## Performance Optimizations

### Database
- Indexed queries for common lookups
- Efficient joins with selected fields
- Pagination for large result sets

### API
- Async/await for I/O operations
- Connection pooling for external APIs
- Caching for frequently accessed data

### Real-time
- Efficient WebSocket message formatting
- Batched updates for progress tracking
- Connection cleanup on disconnect

## Monitoring & Logging

### Application Metrics
- Request/response times
- Error rates by endpoint
- WebSocket connection counts
- Database query performance

### Business Metrics
- Session duration distribution
- Payment success rates
- User engagement metrics
- AI response quality

### Logging
- Structured logging with context
- Error tracking with stack traces
- Audit logs for financial operations
- Performance monitoring

## Future Enhancements

### Planned Features
1. **Mobile App Support**: React Native companion app
2. **Advanced Analytics**: Detailed learning insights
3. **Social Features**: Student communities, discussions
4. **Certification**: Course completion certificates
5. **Live Sessions**: Real-time interactive sessions
6. **Content Moderation**: AI-powered content review
7. **Multi-language Support**: Internationalization
8. **Advanced AI**: Personalized learning paths

### Technical Improvements
1. **GraphQL API**: More flexible data fetching
2. **Microservices**: Service decomposition
3. **Event Sourcing**: Audit trail and replay
4. **Machine Learning**: Recommendation algorithms
5. **Blockchain Integration**: Decentralized credentials
6. **Real-time Collaboration**: Multi-user sessions

This comprehensive documentation covers all aspects of the Murph backend repository, providing detailed insights into its architecture, implementation, and capabilities for comparison with other similar projects.