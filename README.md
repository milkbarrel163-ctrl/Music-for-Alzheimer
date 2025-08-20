# MusicAlzheimer Backend

## Overview

The MusicAlzheimer backend provides AI-powered music therapy services through a FastAPI server with Model Context Protocol (MCP) support for AI assistant integration.

## Features

- 🤖 **MCP Server**: Full Model Context Protocol implementation for AI assistants
- 🎵 **Music Generation**: AI-powered therapeutic music creation
- 📊 **Session Management**: Track and analyze therapy sessions
- 🔄 **Real-time Communication**: WebSocket support for live updates
- 🎯 **Patient Profiles**: Personalized therapy based on patient preferences
- 💡 **AI Suggestions**: Intelligent recommendations for therapy sessions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio processing)
- Virtual environment (recommended)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

## Installation

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Create necessary directories:**
```bash
mkdir -p assets/music/{familiar,soothing,uplifting,generated}
mkdir -p logs
mkdir -p data
mkdir -p temp
```

## Configuration

### Essential Environment Variables

Edit your `.env` file with the following required settings:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=generate_a_secure_random_key

# Server Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
MCP_SERVER_PORT=8001

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### Generating a Secure JWT Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Running the Server

### Standard Backend Server

```bash
python main.py
```

The server will be available at `http://localhost:8000`

### MCP Server

```bash
python mcp_server.py
```

The MCP server will be available at `http://localhost:8001`

### Running Both Servers

```bash
# In one terminal
python main.py

# In another terminal
python mcp_server.py
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## MCP Server Usage

### Available Tools

The MCP server provides the following tools for AI assistants:

1. **start_session**: Begin a new therapy session
2. **end_session**: End an active session
3. **generate_music**: Create AI-powered therapeutic music
4. **select_music**: Choose music from the library
5. **log_response**: Record patient responses
6. **get_suggestions**: Get AI-powered suggestions
7. **analyze_session**: Analyze session data
8. **get_patient_profile**: Retrieve patient information
9. **update_patient_profile**: Update patient preferences
10. **get_session_history**: View past sessions

### WebSocket Connection

Connect to the MCP server via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onopen = () => {
  // Send tool call
  ws.send(JSON.stringify({
    type: 'tool_call',
    data: {
      tool: 'start_session',
      parameters: {
        patient_id: 'patient_001',
        initial_emotion: 'calm'
      }
    }
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Tool response:', response);
};
```

### REST API Usage

```python
import requests

# Execute a tool via REST API
response = requests.post('http://localhost:8001/api/tool', json={
  'tool': 'generate_music',
  'parameters': {
    'emotion': 'calm',
    'prompt': 'Peaceful piano music',
    'duration': 120
  }
})

result = response.json()
```

## Project Structure

```
backend/
├── main.py                 # Main FastAPI server
├── mcp_server.py          # MCP protocol server
├── gpt_client.py          # OpenAI GPT integration
├── audio_generator.py     # Music generation module
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── assets/
│   └── music/            # Music library
│       ├── familiar/     # Familiar songs
│       ├── soothing/     # Calming music
│       ├── uplifting/    # Energizing music
│       └── generated/    # AI-generated tracks
├── logs/                  # Application logs
├── data/                  # Session data storage
└── temp/                  # Temporary files
```

## Testing

### Run Tests

```bash
pytest tests/
```

### Test Coverage

```bash
pytest --cov=. tests/
```

### Test MCP Server

```bash
# Test WebSocket connection
python -m pytest tests/test_mcp_server.py

# Test individual tools
python tests/test_tools.py
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
```

2. **FFmpeg Not Found**
- Ensure FFmpeg is installed and in your PATH
- Test with: `ffmpeg -version`

3. **OpenAI API Errors**
- Verify your API key is correct
- Check API rate limits
- Ensure you have credits in your OpenAI account

4. **WebSocket Connection Failed**
- Check CORS settings in `.env`
- Ensure frontend URL is correctly configured
- Verify firewall settings

### Debug Mode

Enable debug mode in `.env`:
```env
DEV_MODE=true
LOG_LEVEL=DEBUG
DEBUG_SQL=true
```

## Development

### Code Style

```bash
# Format code with black
black .

# Check with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Deployment

### Production Checklist

- [ ] Set `BACKEND_ENV=production` in `.env`
- [ ] Use strong JWT secret key
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (nginx/Apache)
- [ ] Set up process manager (systemd/supervisor)
- [ ] Configure logging and monitoring
- [ ] Set up database backups (if using)
- [ ] Review security settings

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t musicalzheimer-backend .
docker run -p 8000:8000 --env-file .env musicalzheimer-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For issues or questions:
- Check the [documentation](../README.md)
- Open an issue on GitHub
- Contact the development team

## License

Copyright © 2024 MusicAlzheimer Team. All rights reserved.