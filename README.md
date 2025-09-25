# ZOOP FNOL Agent 🚗📋

A sophisticated AI-powered **First Notice of Loss (FNOL)** insurance claim processing system that automates claim intake, risk assessment, and routing using advanced LLM agents.

## 🎯 Overview

The ZOOP FNOL Agent is an intelligent insurance claim processing system that leverages Google's Gemini AI to automatically:

- **Validate and parse** incoming insurance claims
- **Assess fraud risk** using AI-powered analysis
- **Route claims** to appropriate adjusters based on complexity and priority
- **Process claims** efficiently with minimal human intervention

## 🏗️ Project Structure

```
ZOOP_FNOL_AGENT/
├── README.md
├── backend/
│   ├── env.local                    # Environment configuration
│   ├── fnol.db                      # SQLite database
│   ├── requirements.txt             # Python dependencies
│   ├── sample_data.json            # Test claim data
│   └── app/
│       ├── main.py                  # FastAPI application entry point
│       ├── agents/                  # AI Agent modules
│       │   ├── __init__.py
│       │   ├── intake_agent.py      # Claim validation & parsing
│       │   ├── risk_assessment_agent.py  # Fraud risk analysis
│       │   └── routing_agent.py     # Claim routing decisions
│       ├── db/
│       │   └── database.py          # Database configuration
│       ├── model/                   # SQLAlchemy models
│       │   ├── claims.py            # Claim model
│       │   └── claim_assessment.py  # Assessment model
│       ├── route/
│       │   └── claim_route.py       # API endpoints
│       ├── schema/                  # Pydantic schemas
│       │   ├── __init__.py
│       │   ├── claim_schema.py      # Claim data validation
│       │   ├── claim_assessment_schema.py
│       │   ├── risk_schema.py       # Risk assessment output
│       │   └── routing_decision_schema.py
│       └── service/                 # Business logic
│           ├── claim_service.py     # Main claim processing
│           └── llm_service.py       # LLM integration
└── frontend/                        # Frontend application (TBD)
```

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI (Python web framework)
- **Database**: SQLite with SQLAlchemy (async support)
- **AI/ML**:
  - Google Gemini AI (LLM)
  - LangChain (AI framework)
  - LangSmith (tracing & monitoring)
- **Data Validation**: Pydantic
- **Authentication**: (TBD)

### Development & Deployment

- **Language**: Python 3.8+
- **Database ORM**: SQLAlchemy (async)
- **API Documentation**: Swagger/OpenAPI (auto-generated)
- **Environment Management**: python-dotenv

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- (Optional) LangSmith API key for tracing

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ravin1100/Zoop_FNOL_Agent.git
   cd ZOOP_FNOL_AGENT
   ```

2. **Navigate to backend directory**

   ```bash
   cd backend
   ```

3. **Create virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**

   Update the `env.local` file with your API keys:

   ```env
   DATABASE_URL="sqlite+aiosqlite:///./fnol.db"

   # Required: Google Gemini API Key
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Optional: LangSmith for tracing (recommended for development)
   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   LANGSMITH_PROJECT="Zoop FNOL Agent"

   # Optional: OpenAI (currently not used)
   # OPENAI_API_KEY=your-openai-api-key
   ```

### Running the Application

1. **Start the FastAPI server**

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the application**
   - **API Base URL**: http://localhost:8000
   - **Interactive API Docs**: http://localhost:8000/docs
   - **ReDoc Documentation**: http://localhost:8000/redoc

### Testing the API

You can test the claim processing using the provided sample data:

```bash
# Example: Process a claim using curl
curl -X POST "http://localhost:8000/claims/process" \
     -H "Content-Type: application/json" \
     -d @sample_data.json
```

Or use the interactive Swagger UI at http://localhost:8000/docs

## 📋 API Endpoints

### Claim Processing

- `POST /claims/process` - Process a new insurance claim
- `GET /claims/{claim_id}` - Retrieve claim details
- `GET /claims/` - List all claims

### Health Check

- `GET /` - Basic health check endpoint

## 🤖 AI Agents

### 1. Intake Agent

- **Purpose**: Validates and parses incoming claim data
- **Features**:
  - Field validation
  - Data normalization
  - Missing data identification

### 2. Risk Assessment Agent

- **Purpose**: Analyzes claims for potential fraud
- **Features**:
  - Fraud risk scoring (0-10 scale)
  - Suspicious pattern detection
  - Risk factor analysis

### 3. Routing Agent

- **Purpose**: Determines claim routing and priority
- **Features**:
  - Adjuster tier assignment (1-3)
  - Priority level determination
  - Workload balancing

## 📊 Sample Data

The project includes `sample_data.json` with 15 test scenarios covering:

- ✅ Standard auto claims
- ⚠️ High-risk fraud cases
- 🚨 Urgent priority claims
- 💰 High-value claims
- ❌ Incomplete data scenarios

## 🔧 Configuration

### Environment Variables

| Variable            | Description                | Required |
| ------------------- | -------------------------- | -------- |
| `DATABASE_URL`      | SQLite database connection | ✅       |
| `GOOGLE_API_KEY`    | Google Gemini API key      | ✅       |
| `LANGSMITH_TRACING` | Enable LangSmith tracing   | ❌       |
| `LANGSMITH_API_KEY` | LangSmith API key          | ❌       |
| `LANGSMITH_PROJECT` | LangSmith project name     | ❌       |

### Database

The application uses SQLite with automatic table creation on startup. The database file (`fnol.db`) will be created automatically in the backend directory.

## 🧪 Development

### Project Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   AI Agents     │    │   Database      │
│   Routes        │────│   (Gemini AI)   │────│   (SQLite)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   Schemas       │    │   Services      │    │   Models        │
    │   (Validation)  │    │   (Business)    │    │   (SQLAlchemy)  │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

- **Async/Await**: Full async support for database and API operations
- **Type Safety**: Comprehensive Pydantic schemas for data validation
- **AI Integration**: Structured output from LLMs using Pydantic models
- **Error Handling**: Robust error handling throughout the application
- **Logging**: Comprehensive logging for debugging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚧 Future Enhancements

- [ ] Frontend React/Next.js application
- [ ] User authentication and authorization
- [ ] Advanced fraud detection models
- [ ] Real-time claim status tracking
- [ ] Integration with external insurance APIs
- [ ] Mobile application
- [ ] Advanced analytics and reporting

## 📞 Support

For support and questions, please open an issue in the GitHub repository.

---

**Built with ❤️ using FastAPI and Google Gemini AI**
