# 🧠 ReMindly Agent

<p align="center">
  <strong>Turn raw knowledge into structured, reusable Markdown with an AI-powered organization pipeline.</strong>
</p>

<p align="center">
  A lightweight AI agent for transforming unstructured explanations, study material, technical notes, and everyday knowledge into clean, organized Markdown.
</p>

<p align="center">
  <a href="https://github.com/Al-Jid/ReMindly-Agent">GitHub Repository</a>
  ·
  <a href="#-getting-started">Getting Started</a>
  ·
  <a href="#-api">API</a>
  ·
  <a href="#-deployment">Deployment</a>
</p>

---

## 📖 About ReMindly Agent

We consume useful information every day.

During university, while learning a new technology, reading documentation, following tutorials, attending lectures, or solving problems, we often understand something once and then forget it later.

The problem is not always learning.

The problem is that useful knowledge is often left as:

- Raw explanations
- Unstructured text
- Scattered notes
- Long paragraphs
- Technical discussions
- Temporary information we never organize

**ReMindly Agent** was built around a simple idea:

> Knowledge becomes more useful when it is organized in a form that can be reviewed, reused, and remembered.

Instead of manually rewriting everything into notes, ReMindly Agent uses an AI-powered processing pipeline to transform raw content into structured Markdown while attempting to preserve the original meaning.

```text
Raw Knowledge
      ↓
AI Processing
      ↓
Validation
      ↓
Quality Review
      ↓
Structured Markdown
      ↓
Reusable Knowledge
```

---

# ✨ Features

## 🤖 AI-Powered Organization

ReMindly Agent sends raw content through an AI organization pipeline designed to convert unstructured information into readable Markdown.

It can intelligently use:

- Headings
- Subheadings
- Bullet points
- Numbered steps
- Code blocks
- Inline code
- Tables
- Structured sections

The objective is not simply to summarize the input.

The objective is to **organize it**.

---

## ⚡ Real-Time Streaming

ReMindly Agent supports streamed AI generation through:

```http
POST /api/organize/stream
```

Instead of waiting for the entire generation process to finish, the frontend can receive progress and generated content incrementally.

The UI exposes the processing pipeline in real time:

```text
Input Received
      ↓
Preparing Instructions
      ↓
Generating Markdown
      ↓
Validating Markdown
      ↓
AI Quality Review
      ↓
Finalizing
```

This provides immediate feedback while the request is being processed.

---

## 🧠 Multiple Processing Modes

The interface supports different processing strategies so users can balance speed and output quality depending on the task.

The backend also adjusts:

- Chunk size
- Output-token budgets
- Processing behavior

based on the selected mode and detail level.

---

## 🎯 Configurable Detail Levels

Users can control how much detail should be retained in the generated notes.

The backend uses separate output budgets for different detail levels, including:

- Short
- Medium
- Detailed
- Preserve

This allows ReMindly Agent to handle both concise notes and content where preserving more of the original material is important.

---

## 🌍 Language-Aware Processing

ReMindly Agent includes language detection for:

- Arabic
- English
- Mixed Arabic and English

The system analyzes the input and can validate whether the generated result matches the expected language behavior.

This is particularly useful for technical notes where Arabic explanations may contain English terminology.

---

## ✍️ Custom Instructions

Users can provide an optional instruction alongside the source text.

For example:

```text
Keep the explanations Arabic and technical terms English.
```

or:

```text
Organize this as beginner-friendly study notes.
```

This gives the user additional control without changing the core organization pipeline.

---

## 📚 Large Input Handling

Long inputs can be automatically divided into manageable chunks.

The chunking system supports configurable:

- Chunk size
- Fast-mode chunk size
- Chunk overlap
- Maximum number of chunks
- Parallel chunk processing

This prevents large inputs from being treated as one uncontrolled model request.

---

## ✅ Markdown Validation

Generated Markdown is validated before the process is considered complete.

The validation layer checks aspects of the generated result such as:

- Output structure
- Expected language
- Content preservation
- Formatting quality
- Validation warnings and errors

Validation information is returned to the frontend and displayed to the user.

---

## 🔎 AI Quality Review

The architecture contains a separate review stage that can evaluate generated output before finalization.

This separates:

```text
Generation
```

from:

```text
Quality Review
```

instead of treating a single model response as automatically final.

---

## 🔄 Retry Support

ReMindly Agent supports configurable generation retries.

If processing or validation requires another attempt, the backend can retry according to:

```env
MAX_GENERATION_RETRIES
```

This behavior is intentionally bounded to avoid uncontrolled API usage.

---

## 📝 Markdown Preview

The frontend provides two result views:

- **Markdown**
- **Preview**

The preview renders the generated Markdown so users can inspect the final formatted result directly in the browser.

---

## 📋 Copy Markdown

Generated Markdown can be copied directly from the interface.

---

## 📥 Download `.md`

Users can download the generated result as a Markdown file.

A custom filename can be provided before downloading.

---

## 📊 Live Processing Information

The interface displays useful processing information including:

- Input character count
- Input word count
- Output character count
- Processing time
- Live timer
- Progress percentage
- Current processing stage
- Validation status

---

## ⭐ GitHub Integration

The interface links directly to the project repository and retrieves the current repository star count using GitHub's public API.

Repository:

https://github.com/Al-Jid/ReMindly-Agent

---

# 🏗️ Architecture

ReMindly Agent uses a lightweight client-server architecture.

```text
┌───────────────────────────────────────┐
│                 User                  │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│               Frontend                │
│                                       │
│        HTML + CSS + JavaScript        │
└──────────────────┬────────────────────┘
                   │
                   │ HTTP / SSE
                   ▼
┌───────────────────────────────────────┐
│                FastAPI                │
│                Backend                │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│         ReMindly Agent Pipeline       │
│                                       │
│  Input Processing                     │
│          ↓                            │
│  Prompt Construction                  │
│          ↓                            │
│  Chunking / Processing Strategy       │
│          ↓                            │
│  LLM Generation                       │
│          ↓                            │
│  Markdown Validation                  │
│          ↓                            │
│  Quality Review                       │
│          ↓                            │
│  Finalization                         │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│       OpenAI-Compatible Provider      │
│                                       │
│             OpenRouter                │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│          Structured Markdown          │
└───────────────────────────────────────┘
```

---

# 🔄 Request Lifecycle

A typical streaming request follows this lifecycle:

```text
1. User enters raw content
          ↓
2. Frontend validates the input
          ↓
3. POST /api/organize/stream
          ↓
4. FastAPI receives the request
          ↓
5. Request ID is assigned
          ↓
6. Rate limit / API protection is checked
          ↓
7. Processing instructions are prepared
          ↓
8. Input is processed or chunked if necessary
          ↓
9. AI model generates Markdown
          ↓
10. Tokens are streamed to the browser
          ↓
11. Markdown validation runs
          ↓
12. Quality review may run
          ↓
13. Final output is returned
          ↓
14. UI displays validation and processing data
```

---

# 🧩 Project Structure

```text
ReMindly-Agent/
│
├── app/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── prompts.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── request_id.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── language_detector.py
│   │   ├── llm.py
│   │   ├── organizer.py
│   │   ├── reviewer.py
│   │   └── validator.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── static/
│   ├── app.js
│   ├── index.html
│   └── style.css
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_chunker.py
│   ├── test_config.py
│   ├── test_language_detector.py
│   └── test_validator.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── index.py
├── pyproject.toml
├── requirements.txt
├── vercel.json
└── README.md
```

---

# 🛠️ Tech Stack

## Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- OpenAI Python SDK
- SlowAPI
- python-dotenv

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Server-Sent Events (SSE)
- Marked
- DOMPurify

## AI Integration

- OpenAI-compatible API interface
- OpenRouter-compatible configuration
- Configurable model
- Streaming generation

## Testing & Code Quality

- Pytest
- pytest-asyncio
- Ruff
- Black
- mypy

## Deployment

- Vercel
- Docker

---

# 🚀 Getting Started

## Prerequisites

Before running the project, make sure you have:

- Python 3.12
- Git
- An API key for the configured AI provider

Docker is optional.

---

## 1. Clone the Repository

```bash
git clone https://github.com/Al-Jid/ReMindly-Agent.git
```

Move into the project:

```bash
cd ReMindly-Agent
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Copy the example environment file.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then configure `.env`.

Example:

```env
MODEL_API_KEY=your_api_key_here

MODEL_BASE_URL=https://openrouter.ai/api/v1

MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free

MODEL_TEMPERATURE=0.2

MODEL_TIMEOUT=90

MAX_OUTPUT_TOKENS=8000

CHUNKING_ENABLED=true

CHUNK_SIZE=12000

CHUNK_OVERLAP=0

MAX_CHUNKS=10

MAX_GENERATION_RETRIES=1

ORGANIZE_RATE_LIMIT=10/minute

STREAM_RATE_LIMIT=5/minute

APP_API_KEY=
```

Additional performance settings supported by the backend include:

```env
FAST_SINGLE_PASS_MAX_CHARS=16000
FAST_CHUNK_SIZE=18000
MAX_PARALLEL_CHUNKS=3
```

---

# 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MODEL_API_KEY` | — | API key used to authenticate with the AI provider |
| `MODEL_BASE_URL` | `https://openrouter.ai/api/v1` | OpenAI-compatible API endpoint |
| `MODEL_NAME` | `nvidia/nemotron-3-super-120b-a12b:free` | AI model used by the application |
| `MODEL_TEMPERATURE` | `0.2` | Generation temperature |
| `MODEL_TIMEOUT` | `90` | Model request timeout in seconds |
| `MAX_OUTPUT_TOKENS` | `8000` | Global maximum output-token budget |
| `CHUNKING_ENABLED` | `true` | Enables automatic processing of large inputs in chunks |
| `CHUNK_SIZE` | `12000` | Standard chunk size |
| `FAST_CHUNK_SIZE` | `18000` | Chunk size used by fast processing |
| `CHUNK_OVERLAP` | `0` | Character overlap between chunks |
| `MAX_CHUNKS` | `10` | Maximum allowed number of chunks |
| `FAST_SINGLE_PASS_MAX_CHARS` | `16000` | Maximum size for selected fast single-pass processing |
| `MAX_PARALLEL_CHUNKS` | `3` | Maximum chunk-processing concurrency |
| `MAX_GENERATION_RETRIES` | `1` | Maximum configured generation retries |
| `ORGANIZE_RATE_LIMIT` | `10/minute` | Rate limit for the standard organize endpoint |
| `STREAM_RATE_LIMIT` | `5/minute` | Rate limit for streaming requests |
| `APP_API_KEY` | empty | Optional application-level API protection |

> `MODEL_API_KEY` must be configured for AI generation to work.

---

# ⚠️ Secret Management

Never commit your real API key.

Do **not** write secrets directly inside frontend JavaScript:

```javascript
const API_KEY = "your-secret-key";
```

Frontend JavaScript is delivered to the user's browser and can be inspected.

ReMindly Agent instead follows this architecture:

```text
Browser
   ↓
ReMindly Backend
   ↓
Environment Variable
   ↓
AI Provider
```

Your real key should exist only in a local `.env` file or in the environment-variable configuration of your deployment platform.

Make sure `.env` is excluded from Git.

If a real API key is ever committed publicly, revoke it immediately and create a new one.

---

# ▶️ Run Locally

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The application should become available at:

```text
http://127.0.0.1:8000
```

---

# ❤️ Health Check

The application exposes:

```http
GET /api/health
```

The health endpoint reports application status and configuration checks.

Example structure:

```json
{
  "status": "ok",
  "service": "ReMindly Agent",
  "version": "2.2.1",
  "checks": {}
}
```

A degraded status indicates that one or more required configuration checks are not passing.

---

# 🔌 API

ReMindly Agent currently exposes both standard and streaming organization endpoints.

## Standard Request

```http
POST /api/organize
```

This endpoint returns the completed result as a normal JSON response.

---

## Streaming Request

```http
POST /api/organize/stream
```

This endpoint uses Server-Sent Events to stream processing updates and generated content.

The web interface uses this endpoint for the live generation experience.

---

# 📤 Request Example

A request can contain the source text together with optional processing preferences.

Conceptually:

```json
{
  "text": "Raw text to organize...",
  "instruction": "Optional custom instruction",
  "mode": "balanced",
  "language": "english",
  "detail_level": "medium"
}
```

---

# 📥 Response Information

A completed organization result can include information such as:

```json
{
  "markdown": "# Organized Notes",
  "mode": "balanced",
  "language": "english",
  "detail_level": "medium",
  "reviewed": true,
  "retried": false,
  "processing_time": 2.5,
  "input_characters": 1500,
  "output_characters": 1200,
  "request_id": "request-id",
  "validation": {
    "valid": true,
    "issues": []
  }
}
```

---

# 📡 Streaming Events

During a streaming request, the frontend can receive different SSE events representing the current state of the pipeline.

The client supports events including:

```text
progress
token
replace
completed
error
```

### `progress`

Updates the current processing stage and percentage.

### `token`

Appends newly generated content to the Markdown editor.

### `replace`

Replaces the current generated content when the backend produces a revised version.

### `completed`

Contains the final Markdown and processing metadata.

### `error`

Indicates that processing failed.

---

# 🛡️ API Protection

ReMindly Agent supports an optional application-level API key:

```env
APP_API_KEY=
```

If `APP_API_KEY` is empty, this additional protection is disabled.

When configured, protected API requests must provide:

```http
X-API-Key: your-app-api-key
```

This is separate from `MODEL_API_KEY`.

```text
MODEL_API_KEY
    → authenticates the backend with the AI provider

APP_API_KEY
    → optionally protects access to the ReMindly API
```

---

# 🚦 Rate Limiting

The backend includes IP-based rate limiting through SlowAPI.

Default limits:

```env
ORGANIZE_RATE_LIMIT=10/minute
STREAM_RATE_LIMIT=5/minute
```

These values can be changed through environment variables.

---

# 🆔 Request IDs

Requests are assigned a request ID by middleware.

This improves:

- Debugging
- Error tracing
- Server logging
- Request correlation

When an internal processing error occurs, the API can return the corresponding request ID without exposing internal exception details to the client.

---

# 🧠 AI Provider

The application communicates through the OpenAI Python SDK using an OpenAI-compatible API interface.

The provider is controlled through:

```env
MODEL_API_KEY=
MODEL_BASE_URL=
MODEL_NAME=
```

The current default base URL is:

```text
https://openrouter.ai/api/v1
```

This means the architecture is not tightly coupled to a single model name.

A compatible provider/model can be selected through configuration rather than exposing credentials or provider logic in the frontend.

---

# 🧪 Testing

The repository contains automated tests for core application behavior.

Current test areas include:

```text
tests/
├── test_api.py
├── test_chunker.py
├── test_config.py
├── test_language_detector.py
└── test_validator.py
```

Run the test suite with:

```bash
pytest
```

---

# 🧹 Code Quality

The project includes configuration for:

- Black
- Ruff
- mypy

### Ruff

```bash
ruff check .
```

### Black

```bash
black --check .
```

### mypy

```bash
mypy app
```

---

# 🐳 Docker

ReMindly Agent includes a production-oriented `Dockerfile`.

Build the image:

```bash
docker build -t remindly-agent .
```

Run the container:

```bash
docker run \
  --env-file .env \
  -p 8000:8000 \
  remindly-agent
```

Then open:

```text
http://127.0.0.1:8000
```

The container:

- Uses Python 3.12 slim
- Runs as a non-root application user
- Exposes port `8000`
- Includes a health check
- Starts the application through Uvicorn

---

# ☁️ Deployment

## Vercel

The repository contains:

```text
vercel.json
index.py
```

for Vercel deployment.

Before deploying, configure the required environment variables in the Vercel project.

At minimum:

```env
MODEL_API_KEY=your_api_key
```

The current provider configuration can also be explicitly configured:

```env
MODEL_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=nvidia/nemotron-3-super-120b-a12b:free
```

Additional configuration can be added according to the environment-variable table above.

> Never commit production secrets to the repository.

When the Vercel project is connected to the GitHub repository, pushes to the configured production branch can trigger new deployments automatically.

---

# 💾 Local Draft Persistence

The frontend stores the current working draft in browser `localStorage`.

This includes information such as:

- Input text
- Generated Markdown
- Custom instruction
- Filename
- Mode
- Language
- Detail level

This helps preserve the user's current work if the page is refreshed.

The Clear action removes the saved local draft.

---

# 🎨 User Interface

The ReMindly Agent interface is designed around a focused workspace.

The primary interface contains:

```text
┌───────────────────────────────────────────────┐
│ ReMindly Agent             GitHub / Star     │
│                                               │
│ Mode       Language       Detail Level        │
│                                               │
│ ┌────────────────┐ ┌────────────────────────┐ │
│ │ Raw Explanation│ │ Result                 │ │
│ │                │ │ Markdown / Preview     │ │
│ │                │ │                        │ │
│ └────────────────┘ └────────────────────────┘ │
│                                               │
│          Live Processing Pipeline             │
└───────────────────────────────────────────────┘
```

The interface is responsive and supports smaller screens through dedicated layout breakpoints.

---

# 🎯 Example Use Cases

ReMindly Agent can be used for more than traditional lecture notes.

## 📚 Studying

Convert long explanations into structured revision material.

## 💻 Programming

Organize:

- Code explanations
- Commands
- Framework concepts
- Error-solving notes
- Technical tutorials
- API concepts

## 🤖 Artificial Intelligence

Organize material about:

- Machine Learning
- Deep Learning
- Large Language Models
- AI Agents
- RAG
- Prompt Engineering

## 📝 Lectures

Turn raw lecture content into structured Markdown that can be reviewed later.

## 📖 Documentation

Restructure technical information into a cleaner personal reference.

## 💼 Work Knowledge

Turn explanations, procedures, and technical discoveries into reusable notes instead of relying on memory.

## 🔬 Research

Organize raw research material into a more navigable Markdown structure.

---

# 🔒 Security Design

Security-related decisions currently implemented in the project include:

- AI provider secrets remain server-side
- Optional API-level authentication
- Constant-time API-key comparison
- IP-based rate limiting
- Request IDs for traceability
- Generic internal-error responses
- Sanitized Markdown preview when DOMPurify is available
- Configurable model timeouts
- Bounded chunk counts
- Bounded generation retries
- Bounded output-token budgets

Security should still be reviewed whenever the application is exposed to untrusted public traffic.

---

# ⚙️ Performance Design

ReMindly Agent includes several controls intended to prevent unnecessary model usage and improve processing behavior:

```text
FAST_SINGLE_PASS_MAX_CHARS
FAST_CHUNK_SIZE
CHUNK_SIZE
MAX_CHUNKS
MAX_PARALLEL_CHUNKS
MAX_OUTPUT_TOKENS
MAX_GENERATION_RETRIES
```

The application can therefore choose between:

```text
Single-pass processing
```

and:

```text
Chunked processing
```

depending on input size and processing mode.

---

# 🧭 Design Principles

ReMindly Agent is built around several principles.

### Preserve Meaning

Organization should not silently change the meaning of the source material.

### Structure Before Decoration

Markdown formatting should improve readability rather than add unnecessary complexity.

### Keep Secrets Server-Side

Provider credentials never belong in browser JavaScript.

### Validate Generated Output

Model output should not automatically be treated as correct simply because generation completed.

### Make Processing Visible

Streaming progress gives the user feedback instead of presenting AI processing as an unexplained loading state.

### Keep the Architecture Lightweight

The project intentionally uses a small frontend stack and modular FastAPI backend rather than introducing unnecessary infrastructure.

---

# 🗺️ Future Development

Potential future directions include:

- [ ] User authentication
- [ ] User accounts
- [ ] Persistent note history
- [ ] Database-backed notes
- [ ] Folders and tags
- [ ] Search across saved notes
- [ ] PDF export
- [ ] Additional export formats
- [ ] Flashcard generation
- [ ] Quiz generation
- [ ] Automatic summaries
- [ ] Multiple note templates
- [ ] Provider presets
- [ ] Model selector
- [ ] Personal knowledge base
- [ ] Semantic search
- [ ] RAG over saved notes
- [ ] Agent tools
- [ ] Cloud synchronization
- [ ] Sharing and collaboration

---

# 🤝 Contributing

Contributions, bug reports, and improvements are welcome.

## 1. Fork the Repository

Fork:

```text
Al-Jid/ReMindly-Agent
```

Then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/ReMindly-Agent.git
```

---

## 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## 3. Make Your Changes

Before committing, run the relevant tests and quality checks.

For example:

```bash
pytest
ruff check .
```

---

## 4. Commit

```bash
git add .
git commit -m "Add your feature"
```

---

## 5. Push

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request against the main repository.

---

# 🐛 Bug Reports

If you encounter a bug, open a GitHub issue and include as much relevant information as possible:

- Description of the problem
- Expected behavior
- Actual behavior
- Steps to reproduce
- Operating system
- Python version
- Browser, when relevant
- Relevant logs
- Request ID, when available

Do **not** include API keys or other secrets in issues.

---

# 👨‍💻 Author

Developed by **Al-Jid**.

GitHub:

https://github.com/Al-Jid

Project Repository:

https://github.com/Al-Jid/ReMindly-Agent

---

# ⭐ Support

If ReMindly Agent is useful to you, consider giving the repository a **Star ⭐**.

It helps the project become easier to discover and supports continued development.

---

# 📌 Project Vision

ReMindly Agent started from a common problem:

We learn something useful, understand it, move on, and later realize that we never turned that knowledge into something we can easily revisit.

The long-term goal is to reduce that gap.

```text
Learn Something
      ↓
Capture It
      ↓
ReMindly Agent
      ↓
Organize It
      ↓
Preserve It
      ↓
Find It Again
      ↓
Remember & Reuse It
```

ReMindly Agent is intended to evolve beyond a simple text formatter into an intelligent system for **capturing, organizing, reviewing, and reusing knowledge**.

---

<p align="center">
  <strong>ReMindly Agent</strong>
</p>

<p align="center">
  Turn raw knowledge into something worth remembering.
</p>
