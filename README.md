# tf-code-analyzer-agntcy-agent
Terraform Code Analyzer AI Agent

## Overview

This repository contains a Terraform Code Analyzer AI Agent Protocol FastAPI application. It also includes examples of JSON-based logging, CORS configuration, and route tagging.

## Requirements

- Python 3.12+
- A virtual environment is recommended for isolating dependencies.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/cisco-ai-agents/tf-code-analyzer-agntcy-agent
   cd tf-code-reviewer-agntcy-agent
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Required Environment Variables
Before running the application, ensure you have the following environment variables set in your .env file or in your environment:

LLM_PROVIDER: The language model provider (e.g., azure or openai).
OPENAI_TEMPERATURE: The temperature setting for the language model (e.g., 0.7).
AZURE_OPENAI_ENDPOINT: The endpoint URL for Azure OpenAI (required if using azure as LLM_PROVIDER).
AZURE_OPENAI_API_KEY: Your Azure OpenAI API key (required if using azure as LLM_PROVIDER).
AZURE_OPENAI_API_VERSION: The API version for Azure OpenAI (required if using azure as LLM_PROVIDER).
OPENAI_API_KEY: Your OpenAI API key (required if using openai as LLM_PROVIDER).
OPENAI_API_VERSION: The model version for OpenAI (default is usually set to gpt-4o or similar).
Make sure your .env file includes these keys with the appropriate values. For example:

```dotenv
LLM_PROVIDER=azure
OPENAI_TEMPERATURE=0.7
OPENAI_API_VERSION=gpt-4o
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_API_VERSION=2023-03-15-preview
# For OpenAI (if used)
OPENAI_API_KEY=your-openai-api-key
```

If you are running the client, make sure to add relevant Github environment variables.

GITHUB_REPO_URL: The Github repository URL on which to run the code analyzer.
GITHUB_TOKEN: Your Github Authentication Token.
GITHUB_BRANCH: The branch that contains the code you want analyzed.

```dotenv
GITHUB_REPO_URL=https://your-github-url
GITHUB_TOKEN=your-github-token
GITHUB_BRANCH=main
```

### Server

You can run the application by executing:

```bash
python -m app.main
```

### Expected Console Output

On a successful run, you should see logs in your terminal similar to the snippet below. The exact timestamps, process IDs, and file paths will vary:

```bash
python -m app.main
{"timestamp": "2025-03-11 13:24:36,754", "level": "INFO", "message": "Logging is initialized. This should appear in the log file.", "module": "logging_config", "function": "configure_logging", "line": 142, "logger": "app", "pid": 5004}
{"timestamp": "2025-03-11 13:24:36,754", "level": "INFO", "message": "Starting FastAPI application...", "module": "main", "function": "main", "line": 155, "logger": "app", "pid": 5004}
{"timestamp": "2025-03-11 13:24:36,758", "level": "INFO", "message": ".env file loaded from <your_cloned_repo_path>/.env", "module": "utils", "function": "load_environment_variables", "line": 64, "logger": "root", "pid": 5004}
INFO:     Started server process [5004]
INFO:     Waiting for application startup.
{"timestamp": "2025-03-11 13:24:36,864", "level": "INFO", "message": "Starting Terraform Code Analyzer Agent", "module": "main", "function": "lifespan", "line": 39, "logger": "root", "pid": 5004}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8133 (Press CTRL+C to quit)
```

This output confirms that:

1. Logging is properly initialized.
2. The server is listening on `0.0.0.0:8133`.
3. Your environment variables (like `.env file loaded`) are read.

### Client

Change to `client` folder

```bash
python -m client.stateless_client
```

On a successful remote graph run you should see logs in your terminal similar to the snippet below:

```bash
{"timestamp": "2025-03-11 13:26:29,622", "level": "ERROR", "message": "{'event': 'final_result', 'result': {'github': {'repo_url': '<your_repo_url>', 'github_token': '<your_token>', 'branch': '<your_branch>'}, 'static_analyzer_output': '<analyzer_output>'}}", "module": "stateless_client", "function": "<module>", "line": 174, "logger": "__main__", "pid": 7529}
```

## Logging

- **Format**: The application is configured to use JSON logging by default. Each log line provides a timestamp, log level, module name, and the message.
- **Location**: Logs typically go to stdout when running locally. If you configure a file handler or direct logs to a centralized logging solution, they can be written to a file (e.g., `logs/app.log`) or shipped to another service.
- **Customization**: You can change the log level (`info`, `debug`, etc.) or format by modifying environment variables or the logger configuration in your code. If you run in Docker or Kubernetes, ensure the logs are captured properly and aggregated where needed.

## API Endpoints

By default, the API documentation is available at:

```bash
http://0.0.0.0:8133/docs
```

(Adjust the host and port if you override them via environment variables.)

## Running as a LangGraph Studio

You need to install Rust: <https://www.rust-lang.org/tools/install>

Run the server

Change to `client` folder

```bash
langgraph dev
```

![Langgraph Studio](./docs/imgs/studio.png "Studio")

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and ensure tests pass.
4. Submit a pull request.