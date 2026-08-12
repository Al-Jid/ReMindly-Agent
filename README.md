# 📝 Study Notes — AI Markdown Notes Agent

An AI-powered web application that transforms raw explanations, study material, and unstructured text into clean, organized, and easy-to-read **Markdown notes**.

The application uses a lightweight **FastAPI backend**, a simple **HTML/CSS/JavaScript frontend**, and an **OpenAI-compatible LLM API** to intelligently restructure content while preserving its original meaning.

---

## ✨ Overview

Studying from long, unstructured explanations can be difficult.

**Study Notes** solves this by allowing you to paste raw text and automatically transform it into structured Markdown containing:

* Clear headings and subheadings
* Bullet points
* Numbered steps
* Properly formatted code and commands
* Tables when useful
* Cleaner explanations
* Reduced repetition
* Study-friendly structure

Instead of manually rewriting notes, the application uses an AI model to organize them automatically.

---

## 🚀 Features

* 🤖 **AI-powered note organization**
* 📝 Converts raw text into clean Markdown
* 🧠 Preserves the original meaning and facts
* 🗂️ Automatically creates logical sections
* 📌 Uses headings, lists, and formatting intelligently
* 💻 Properly formats code, commands, paths, and technical terms
* 📊 Generates tables when they improve comparisons
* 🌍 Keeps the original input language
* 🎯 Supports additional custom instructions
* 🔐 Keeps API keys securely on the backend
* ⚡ Lightweight FastAPI architecture
* 🌐 Simple web-based user interface
* 🔌 Works with OpenAI-compatible API providers

---

## 🧠 How It Works

The workflow is simple:

```text
User enters raw notes
        ↓
Frontend sends the text
        ↓
FastAPI Backend
        ↓
Markdown Organizer Prompt
        ↓
LLM / AI Model
        ↓
Structured Markdown
        ↓
Result displayed to the user
```

The backend sends the user's text to the configured language model together with a system prompt designed specifically for organizing study notes.

The AI is instructed to:

1. Preserve the original meaning.
2. Avoid inventing information.
3. Remove unnecessary repetition.
4. Keep the original language.
5. Organize content using Markdown.
6. Make the result easy to scan and study.

---

## 🛠️ Tech Stack

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**
* **OpenAI Python SDK**
* **python-dotenv**
* **Pydantic**

### Frontend

* **HTML**
* **CSS**
* **JavaScript**

### AI

The application uses an **OpenAI-compatible API**, allowing the backend to communicate with supported language-model providers using:

```text
MODEL_API_KEY
MODEL_BASE_URL
MODEL_NAME
```

---

## 📁 Project Structure

```text
Study-Notes/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── __init__.py
│   └── main.py
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── server.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Main Files

| File / Directory   | Description                            |
| ------------------ | -------------------------------------- |
| `server.py`        | Main FastAPI server and AI integration |
| `static/`          | Frontend HTML, CSS, and JavaScript     |
| `app/`             | Modular application structure          |
| `requirements.txt` | Python dependencies                    |
| `.env.example`     | Example environment configuration      |
| `.gitignore`       | Files excluded from Git                |
| `README.md`        | Project documentation                  |

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Al-Jid/Study-Notes.git
```

Move into the project directory:

```bash
cd Study-Notes
```

---

## 🐍 2. Create a Virtual Environment

### Windows

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

## 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The project currently uses:

```text
fastapi
uvicorn
openai
python-dotenv
```

---

## 🔑 4. Configure Environment Variables

Copy the example environment file.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then open `.env` and configure your AI provider:

```env
MODEL_API_KEY=your_api_key_here
MODEL_BASE_URL=
MODEL_NAME=your_model_name
```

### Example

For a provider using the default OpenAI-compatible endpoint:

```env
MODEL_API_KEY=your_api_key_here
MODEL_BASE_URL=
MODEL_NAME=your_model_name
```

For another OpenAI-compatible provider:

```env
MODEL_API_KEY=your_api_key_here
MODEL_BASE_URL=https://your-provider-api-url/v1
MODEL_NAME=your_model_name
```

> Never commit your real `.env` file or API key to GitHub.

---

## ▶️ Running the Application

Start the FastAPI server:

```bash
uvicorn server:app --reload
```

You should see output similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open your browser and visit:

```text
http://127.0.0.1:8000
```

---

## 🔌 API Endpoint

The main AI endpoint is:

```http
POST /api/organize
```

### Request Body

```json
{
  "text": "Your raw explanation or study notes",
  "instruction": "Optional additional instruction"
}
```

The `instruction` field is optional.

---

## 📤 Example Request

```json
{
  "text": "AI agents use LLMs but unlike normal language models they can use tools, APIs, memory and external information.",
  "instruction": "Organize this as beginner-friendly study notes."
}
```

---

## 📥 Example Response

```json
{
  "markdown": "# AI Agents\n\n## Overview\n\nAI agents are systems that combine large language models with tools, memory, and external resources..."
}
```

---

## 💡 Example

### Input

```text
AI agents are different from traditional chatbots because agents can use tools.
They can search the web, call APIs and perform actions.
Traditional chatbots mainly respond to prompts.
Agents can break goals into smaller tasks.
```

### Possible Output

```markdown
# AI Agents

## What Makes AI Agents Different?

AI agents can do more than traditional chatbots.

### AI Agents

AI agents can:

- Use external tools
- Search the web
- Call APIs
- Perform actions
- Break complex goals into smaller tasks

### Traditional Chatbots

Traditional chatbots mainly:

- Receive a prompt
- Generate a response

## Key Difference

Traditional chatbot:

User → Prompt → Answer

AI Agent:

User → Goal → Plan → Tools → Actions → Result
```

---

## 🎯 Use Cases

Study Notes can be useful for organizing:

### 📚 Study Material

Turn long explanations into structured revision notes.

### 💻 Programming Notes

Organize:

* Code explanations
* Commands
* Framework concepts
* API documentation
* Technical tutorials

### 🤖 AI & Machine Learning Notes

Structure complex topics such as:

* AI Agents
* Large Language Models
* RAG
* Prompt Engineering
* Machine Learning
* Deep Learning

### 📝 Lecture Notes

Convert unstructured lecture text into study-friendly sections.

### 📖 Articles

Turn long technical articles into organized Markdown.

### 🔬 Research Notes

Restructure research material without manually formatting every section.

---

## 🏗️ Architecture

The application follows a simple client-server architecture:

```text
┌──────────────────────┐
│        User          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Frontend       │
│ HTML / CSS / JS      │
└──────────┬───────────┘
           │
           │ HTTP Request
           ▼
┌──────────────────────┐
│       FastAPI        │
│       Backend        │
└──────────┬───────────┘
           │
           │ API Call
           ▼
┌──────────────────────┐
│   Language Model     │
│ OpenAI-Compatible API│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Structured Markdown  │
└──────────────────────┘
```

---

## 🔐 Security

The API key is intentionally stored on the **Python backend** instead of the frontend.

Frontend JavaScript runs inside the user's browser and can be inspected using browser developer tools.

Storing an API key directly inside JavaScript would expose it publicly.

For this reason:

```text
Browser
   ↓
FastAPI Backend
   ↓
Environment Variables
   ↓
AI Provider
```

The API key remains inside:

```text
.env
```

and should never be added to Git.

---

## ⚠️ Important Security Rules

Never put secrets directly inside:

```javascript
const API_KEY = "secret-key";
```

Never commit:

```text
.env
```

Make sure `.gitignore` includes:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

If an API key is accidentally committed to GitHub, revoke it immediately and generate a new one.

---

## 🧩 Environment Variables

| Variable         | Required | Description                      |
| ---------------- | -------: | -------------------------------- |
| `MODEL_API_KEY`  |      Yes | API key for the AI provider      |
| `MODEL_NAME`     |      Yes | Model used to organize notes     |
| `MODEL_BASE_URL` |       No | Custom OpenAI-compatible API URL |

---

## 📦 Dependencies

The Python dependencies are defined in:

```text
requirements.txt
```

Current dependencies include:

```text
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
openai>=1.0.0
python-dotenv>=1.0.0
```

Install all dependencies using:

```bash
pip install -r requirements.txt
```

---

## 🧪 Development Mode

Run the server with automatic reload:

```bash
uvicorn server:app --reload
```

The `--reload` option automatically restarts the development server whenever Python source files change.

> `--reload` is intended for development and should not normally be used in production.

---

## 🛣️ Roadmap

Possible future improvements:

* [ ] Markdown live preview
* [ ] Dark mode
* [ ] Export notes as `.md`
* [ ] Export notes as PDF
* [ ] Copy Markdown button
* [ ] Save notes locally
* [ ] Note history
* [ ] Multiple AI provider presets
* [ ] Model selector
* [ ] Streaming AI responses
* [ ] Authentication
* [ ] User accounts
* [ ] Cloud database integration
* [ ] Tags and folders
* [ ] Search saved notes
* [ ] Automatic summaries
* [ ] Flashcard generation
* [ ] Quiz generation
* [ ] Multiple note styles
* [ ] Docker support
* [ ] Production deployment configuration

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome.

### Contribution Workflow

Fork the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Study-Notes.git
```

Create a new branch:

```bash
git checkout -b feature/your-feature-name
```

Make your changes, then commit:

```bash
git add .
git commit -m "Add new feature"
```

Push the branch:

```bash
git push origin feature/your-feature-name
```

Then open a **Pull Request** on GitHub.

---

## 🐛 Issues

If you find a bug or have a feature suggestion, open an issue in the repository.

When reporting bugs, try to include:

* What happened
* What you expected
* Steps to reproduce the issue
* Operating system
* Python version
* Relevant error messages

---

## 👨‍💻 Author

Developed by **Al-Jid**

GitHub:

```text
https://github.com/Al-Jid
```

Repository:

```text
https://github.com/Al-Jid/Study-Notes
```

---

## ⭐ Support

If you find this project useful, consider giving the repository a **Star ⭐**.

It helps support the project and makes it easier for others to discover.

---

## 📌 Project Goal

The goal of **Study Notes** is simple:

> Turn complicated, unstructured explanations into clean, structured, study-friendly notes using AI.

```text
Raw Knowledge
     ↓
AI Organization
     ↓
Structured Notes
     ↓
Better Learning
```

---

<p align="center">
  Built for learning, studying, and organizing knowledge with AI.
</p>
