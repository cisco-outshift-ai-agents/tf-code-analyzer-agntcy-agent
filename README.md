# Terraform Code Analyzer AI Agent
[![Release](https://img.shields.io/github/v/release/cisco-ai-agents/tf-code-analyzer-agntcy-agent?display_name=tag)](CHANGELOG.md)
[![Contributor-Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-fbab2c.svg)](CODE_OF_CONDUCT.md)

## **📌 About the Project**
This repository contains a **Terraform Code Analyzer AI Agent Protocol** built with FastAPI. It includes:
- JSON-based logging
- CORS configuration
- Route tagging

---

## **📋 Prerequisites**
Before installation, ensure you have:
- **Python 3.12+** installed
- A **virtual environment** (recommended for dependency isolation)

---

## **⚙️ Installation Steps**

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/cisco-ai-agents/tf-code-analyzer-agntcy-agent
cd tf-code-reviewer-agntcy-agent
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3️⃣ Install Required Executables**

Before using this package, ensure the following tools are installed on your system:

- **Terraform** → [Installation Guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- **TFLint** → [Installation Guide](https://github.com/terraform-linters/tflint)

---

## 🚀 **Required Environment Variables**

Before running the application, ensure you have the following environment variables set in your `.env` file or in your system environment.

---

## **🔹 OpenAI API Configuration**

If configuring your AI agent to use OpenAI as its LLM provider, set these variables:

```dotenv
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL_NAME=gpt-4o  # Specify the model name
OPENAI_TEMPERATURE=0.7    # Adjust temperature for response randomness
```

---

## **🔹 Azure OpenAI API Configuration**

If configuring your AI agent to use Azure OpenAI as its LLM provider, set these variables:

```dotenv
# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name  # Deployment name in Azure
AZURE_OPENAI_API_VERSION=your-azure-openai-api-version  # API version
OPENAI_TEMPERATURE=0.7 # Adjust temperature for response randomness
```

---

## **🔹 GitHub Configuration (For Client Application)**

If running the client, set these variables to interact with GitHub:

```dotenv
# GitHub Repository Configuration
GITHUB_REPO_URL=https://your-github-url  # The repository to analyze
GITHUB_BRANCH=main  # The branch containing the code to be analyzed

# Optional GitHub Authentication
GITHUB_TOKEN=your-github-token  # (Optional) Provide a token for private repos
```

🔹 **Note:** If analyzing a **public repository**, `GITHUB_TOKEN` is **optional**.

---

✅ **Now you're ready to run the application!**
### Server

You can run the application by executing:

```bash
python -m app.main
```
---

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

---

### Client

Change to `client` folder

```bash
python -m client.stateless_client
```

On a successful remote graph run you should see logs in your terminal similar to the snippet below:

```bash
{"timestamp": "2025-03-11 13:26:29,622", "level": "ERROR", "message": "{'event': 'final_result', 'result': {'github': {'repo_url': '<your_repo_url>', 'github_token': '<your_token>', 'branch': '<your_branch>'}, 'static_analyzer_output': '<analyzer_output>'}}", "module": "stateless_client", "function": "<module>", "line": 174, "logger": "__main__", "pid": 7529}
```

---

## Logging

- **Format**: The application is configured to use JSON logging by default. Each log line provides a timestamp, log level, module name, and the message.
- **Location**: Logs typically go to stdout when running locally. If you configure a file handler or direct logs to a centralized logging solution, they can be written to a file (e.g., `logs/app.log`) or shipped to another service.
- **Customization**: You can change the log level (`info`, `debug`, etc.) or format by modifying environment variables or the logger configuration in your code. If you run in Docker or Kubernetes, ensure the logs are captured properly and aggregated where needed.

---
## API Endpoints

By default, the API documentation is available at:

```bash
http://0.0.0.0:8133/docs
```

(Adjust the host and port if you override them via environment variables.)

---
## Running as a LangGraph Studio

You need to install Rust: <https://www.rust-lang.org/tools/install>

Run the server

```bash
langgraph dev
```

Populate the Github input field with: 
```json
{
   "repo_url": "https://<your_repo_url>",
   "github_token": "<your_github_token>",
   "branch": "<your_github_branch>"
}
```

Upon successful execution, you should see:

![Langgraph Studio](./docs/imgs/studio.png "Studio")

---
## Roadmap

See the [open issues](https://github.com/cisco-ai-agents/tf-code-analyzer-agntcy-agent/issues) for a list
of proposed features (and known issues).
---
## Contributing

Contributions are what make the open source community such an amazing place to
learn, inspire, and create. Any contributions you make are **greatly
appreciated**. For detailed contributing guidelines, please see
[CONTRIBUTING.md](CONTRIBUTING.md)
---
## License

Distributed under the Apache-2.0 License. See [LICENSE](LICENSE) for more
information.
---
## Contact

Aditi Gupta  - [@therealaditigupta](https://github.com/therealaditigupta) - aditigu2@cisco.com

Project Link:
[https://github.com/cisco-ai-agents/tf-code-analyzer-agntcy-agent](https://github.com/cisco-ai-agents/tf-code-analyzer-agntcy-agent)
---
## Acknowledgements

This template was adapted from
[https://github.com/othneildrew/Best-README-Template](https://github.com/othneildrew/Best-README-Template).