# Access Navigator AI

> **AI-Powered Multi-Agent Accessibility Navigation System for Stadiums**
>
> Built for PromptWars Virtual Competition

---

## Overview

Access Navigator AI is a production-grade accessibility navigation system that uses a **Multi-Agent AI Architecture** to help fans with disabilities navigate stadiums safely and efficiently. The system combines real-time crowd monitoring, predictive analytics, and natural language AI assistance to deliver personalized, accessible routing.

### Key Features

- **Multi-Agent AI System** - 4 specialized AI agents working together
- **Real-time Stadium Mapping** - Live SVG floor plans with crowd density
- **AI Route Planning** - Chain-of-Thought reasoning for optimal accessible routes
- **Conversational AI** - Natural language interface with streaming responses
- **Predictive Analytics** - LLM-powered crowd forecasting
- **Live Captioning** - PA announcement processing for Deaf/hard-of-hearing fans
- **Voice Input** - Speech recognition for hands-free destination entry
- **Demo Scenarios** - 5 pre-built scenarios for presentation
- **Multi-Stadium Support** - 3 stadiums with full data models

---

## AI Agent Architecture

```
User Request
    |
    v
+-------------------+     +-------------------+     +-------------------+
|  PerceptionAgent  | --> |   ReasoningAgent  | --> | CommunicationAgent|
|  (Senses/Scans)   |     |  (Thinks/Decides) |     |  (Formats/Speaks) |
+-------------------+     +-------------------+     +-------------------+
    |                            |                           |
    v                            v                           v
Zone Summary               Route Decision             Accessible Output
Crowd Analysis             CoT Reasoning              Haptic/Visual/Audio
Anomaly Detection          Confidence Score           Multi-channel Delivery

+-------------------+
| ConversationalAgent |
|  (ReAct Pattern)    |
+-------------------+
    |
    v
Natural Language Understanding
Intent Classification
Multi-agent Orchestration
Streaming Responses
```

### Agent Details

| Agent | Role | Technology |
|-------|------|------------|
| **PerceptionAgent** | Normalizes sensor data, detects anomalies | Deterministic + LLM summarization |
| **ReasoningAgent** | Route optimization, caption classification | Chain-of-Thought (CoT) prompting |
| **CommunicationAgent** | Formats output for accessibility | Multi-channel formatting |
| **ConversationalAgent** | Natural language interface | ReAct pattern with streaming |

---

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Pydantic** - Type-safe data validation
- **Multi-Provider LLM** - Groq (primary) + Gemini (fallback)
- **Streaming SSE** - Real-time token streaming
- **Background Simulation** - Live crowd dynamics

### Frontend
- **React 18** + TypeScript
- **Tailwind CSS** + shadcn/ui
- **Vite** - Ultra-fast build tool
- **Lucide React** - Beautiful icons
- **Sonner** - Toast notifications

### AI/ML
- **Chain-of-Thought Prompting** - Transparent AI reasoning
- **ReAct Pattern** - Reasoning + Acting for conversational AI
- **Few-Shot Learning** - In-context examples for better accuracy
- **Structured JSON Output** - Type-safe LLM responses

---

## Project Structure

```
backend/
  main.py                 # FastAPI app with all endpoints
  requirements.txt        # Python dependencies
  Dockerfile             # Container config
  core/
    config.py            # Environment configuration
    database.py          # In-memory stadium database
  models/
    schemas.py           # Pydantic data models
  services/
    llm_service.py       # Multi-provider LLM with streaming
    prediction_service.py # AI crowd predictions
  agents/
    perception_agent.py   # Data normalization
    reasoning_agent.py    # Route optimization (CoT)
    communication_agent.py # Output formatting
    conversational_agent.py # NL interface (ReAct)

frontend/
  src/
    config/api.ts        # API endpoints configuration
    hooks/               # Custom React hooks
    components/          # Reusable UI components
    pages/               # Page-level components
    App.tsx             # Root component
    main.tsx            # Entry point
    index.css           # Global styles
  public/               # Static assets
  dist/                 # Production build
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- API key for Groq or Gemini

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_key_here"
# OR
export GEMINI_API_KEY="your_key_here"

# Run the server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
```

The frontend will be available at `http://localhost:3000`

### Docker (Optional)

```bash
cd backend
docker build -t access-navigator-ai .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key access-navigator-ai
```

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with feature flags |
| GET | `/api/stadiums` | List all stadiums |
| GET | `/api/zones` | Get zones for a stadium |
| GET | `/api/graph` | Get connectivity graph |
| GET | `/api/coordinates` | Get zone coordinates for map |

### Routing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/route` | AI route calculation (multi-agent) |
| POST | `/api/route/simple` | Quick route lookup |

### AI Services

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/caption` | Process PA announcement |
| POST | `/api/chat` | Conversational AI |
| POST | `/api/chat/stream` | Streaming conversational AI (SSE) |
| GET | `/api/predictions/{id}` | AI crowd predictions |
| GET | `/api/analytics/{id}` | Stadium analytics with AI insights |

### Data & Demo

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/data/upload` | Upload CSV/JSON zone data |
| POST | `/api/zones/batch-update` | Batch update zones |
| POST | `/api/demo/scenario` | Trigger demo scenarios |
| GET | `/api/announcements` | Get announcement history |

---

## Demo Scenarios

1. **Normal** - Reset all zones to operational
2. **Blocked Paths** - Block accessibility routes, test AI rerouting
3. **Emergency** - High density in upper levels
4. **Halftime** - Crowd surge in concourses
5. **Evacuation** - All exits congested, find accessible egress

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes* | - | Groq API key |
| `GEMINI_API_KEY` | Yes* | - | Gemini API key |
| `PRIMARY_LLM` | No | `groq` | Primary LLM provider |
| `API_PORT` | No | `8000` | Server port |
| `ENABLE_STREAMING` | No | `true` | Enable streaming responses |
| `ENABLE_PREDICTIONS` | No | `true` | Enable AI predictions |
| `ENABLE_ANALYTICS` | No | `true` | Enable analytics |
| `ENABLE_CONVERSATIONAL_AI` | No | `true` | Enable chat |

*At least one LLM API key is required

---

## Architecture Highlights

### Chain-of-Thought (CoT) Reasoning
The ReasoningAgent uses explicit step-by-step thinking:
1. **Filter** - Eliminate invalid paths for the accessibility need
2. **Score** - Rate each valid path (0-100)
3. **Compare** - Weigh accessibility vs time vs crowd
4. **Select** - Choose the optimal path
5. **Explain** - Generate human-readable reasoning

### ReAct Pattern (ConversationalAgent)
The conversational AI follows Reasoning + Acting:
1. **Understand** - Detect user intent from natural language
2. **Plan** - Decide which tools/agents to invoke
3. **Execute** - Gather context from zone data, route calculations
4. **Respond** - Generate natural language response with results

### Multi-Provider LLM with Fallback
- Primary: Groq (ultra-fast inference)
- Fallback: Gemini (if Groq fails)
- Automatic JSON parsing with error recovery
- Streaming support for real-time responses

---

## Accessibility Features

- ♿ **Wheelchair routing** - Avoids stairs, blocked elevators
- 🦻 **Hearing impaired** - Live captioning, visual alerts
- 👁️ **Visual impaired** - Audio descriptions, tactile guidance
- 🎤 **Voice input** - Speech recognition for destination entry
- 📳 **Haptic feedback** - Vibration alerts for critical notifications
- 🌐 **WCAG compliant** - ARIA labels, keyboard navigation, focus management

---

## License

MIT License - Built for PromptWars Virtual Competition
