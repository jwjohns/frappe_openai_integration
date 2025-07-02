# 🧠 LLM Integration for Frappe

A powerful custom Frappe app that integrates Large Language Models (LLMs) like those from OpenAI (e.g., ChatGPT) or locally run models via Ollama into your ERP system. This tool enables users to interact with LLM APIs directly from the Frappe interface, submit prompts, and view generated responses with a seamless, user-friendly UI.

---

## 🌟 Features

- ✍️ Prompt Submission Interface (Chat-style)
- 📬 View LLM-generated responses in real-time
- 🧾 Prompt history tracking
- ⚙️ Configurable LLM Providers:
    - **Ollama**: Connect to a locally running Ollama instance.
    - **OpenAI**: Use OpenAI's API with your key.
- 📊 Dashboard showing prompt stats (total prompts, settings, etc.)
- 🔐 Role-based access control for using AI features
- 💬 Multi-message threads or single prompts

---

## 🖼️ UI Screenshots

1. **Prompt Input Interface**
![chat_assistant](.github/chat_assistant.png)
   - Input your question to the configured LLM
   - Get immediate response via API
   - Save history for reference
2. **Prompt History Listing**
![prompt_log](.github/prompt_log.png)
   - View all past queries and responses
   - Filter by user/date/type

3. **OpenAI Settings**
![settings](.github/settings.png)
   - Configure API keys
   - Toggle model options (e.g., `gpt-3.5`, `gpt-4`)

4. **Dashboard**
![dashboard](.github/dashboard.png)
   - Shows:
     - OpenAI Settings
     - Total prompts
     - Chat Assistant

---

## 🛠️ Installation

Make sure you have Frappe set up.

```bash
# Get the app
$ bench get-app https://github.com/manavmandli/frappe_openai_integration.git

# Install on your site
$ bench --site yoursite install-app frappe_openai_integration

# Install required Python libraries
$ bench pip install openai ollama

---

## ⚙️ Configuration

After installation, navigate to "Home > Integrations > LLM Integration Settings" in your Frappe desk.

1.  **Choose your LLM Provider**:
    *   `ollama`: For using a local Ollama instance.
    *   `openai`: For using the OpenAI API.

2.  **Configure Provider-Specific Settings**:
    *   If **Ollama** is selected:
        *   **Ollama API URL**: Enter the URL of your Ollama service.
            *   If Ollama is running on the same machine as your Frappe development server (not in Docker), this is typically `http://localhost:11434`.
            *   If Frappe/ERPNext is running inside a Docker container and Ollama is running on the host machine, use `http://host.docker.internal:11434` to allow the container to access the host.
            *   Ensure the Ollama service is accessible from your Frappe environment and that the selected model (e.g., `llama2`, `mistral`) is downloaded and available in Ollama (`ollama pull llama2`).
    *   If **OpenAI** is selected:
        *   **OpenAI API Key**: Enter your secret API key from OpenAI.

3.  **Select Model**:
    *   Choose a model from the dropdown. The available models will be a mix of common OpenAI and Ollama models. Ensure the selected model is compatible with your chosen provider. "Auto" will select a default model for the chosen provider.

4.  Save the settings.

Now you can access the "Frappe Chat Assistant" page from your desk and start interacting with the configured LLM.
