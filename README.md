# Social Media App - Backend

A high-performance, asynchronous REST API built with FastAPI, designed for a modern social media platform.

## 🚀 Features

- **Robust Authentication**: JWT-based authentication with Access and Refresh tokens.
- **Email Verification**: Secure onboarding with OTP (One-Time Password) emails.
- **Social Core**: Complete Follow/Unfollow system, Post creation, Liking, and Threaded commenting.
- **AI-Powered Bios**: Integration with Groq AI (Llama 3) to generate creative user bios.
- **Smart Notifications**: Real-time logic for follow, like, and comment alerts.
- **Media Management**: Secure, validated file uploads for profile pictures and posts.
- **Database Migrations**: Managed with Alembic for seamless schema updates.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI Integration**: [Groq Cloud SDK](https://console.groq.com/)
- **Security**: Passlib (Bcrypt), Python-jose (JWT)

## 📦 Project Structure

```text
backend/
├── app/
│   ├── api/          # API Routes (Auth, Social, AI, etc.)
│   ├── core/         # Config, Security, and Settings
│   ├── db/           # Database session and Base class
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic validation schemas
│   └── services/     # Core business logic (Service Layer)
├── alembic/          # Database migration history
└── main.py           # Application entry point
```

## ⚙️ Setup & Installation

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=sqlite:///./sql_app.db
   SECRET_KEY=your_super_secret_key
   GROQ_API_KEY=your_groq_api_key
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_password
   ```

4. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

5. **Start the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📖 API Documentation

Once the server is running, visit:
- **Interactive Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative Docs (Redoc)**: `http://127.0.0.1:8000/redoc`
