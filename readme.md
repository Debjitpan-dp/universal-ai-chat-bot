> **⚠️ Note:** This project is intended for beginners and users who want to quickly explore Large Language Models (LLMs) with minimal setup. It is not designed for enterprise or production use, but is freely available for learning and experimentation.

> ⭐️ If you find this project helpful, please consider leaving a star on GitHub!

# Universal AI Chat Application

A powerful, modern chat application that allows you to interact with multiple AI models (ChatGPT, Claude, Llama3) through both Streamlit and HTML interfaces.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your system
- API keys for the AI services you want to use:
  - OpenAI API key for ChatGPT
  - Anthropic API key for Claude
  - Llama3 runs locally via Ollama (optional)

### Easy Setup with Docker

1. **Clone or download the project files**
2. **Navigate to the project directory**
3. **Start the application:**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications:**
   - **Streamlit Interface:** http://localhost:8501
   - **HTML Interface:** http://localhost:8000
   - **API Documentation:** http://localhost:8000/docs

That's it! Your Universal AI Chat is now running.

## 🎯 Features

### 🤖 Multi-AI Support
- **ChatGPT** - OpenAI's powerful language model
- **Claude** - Anthropic's advanced AI assistant
- **Llama3** - Meta's open-source model (via Ollama)

### 💬 Chat Features
- **Conversation History** - All your chats are saved and accessible
- **Context Memory** - AI remembers previous messages in the conversation
- **System Prompts** - Customize AI behavior with custom instructions
- **Web Search** - Get real-time information from the internet
- **Website Scraping** - Ask questions about specific web pages

### 🎨 Two Frontend Options
- **Streamlit** - Feature-rich, Python-based interface
- **HTML** - Lightweight, modern web interface

## 📱 How to Use

### Getting Your API Keys

#### For ChatGPT:
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account and generate an API key
3. Copy the key (starts with `sk-`)

#### For Claude:
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account and generate an API key
3. Copy the key

#### For Llama3:
1. Install [Ollama](https://ollama.com/) on your system
2. Run: `ollama pull llama3`
3. No API key needed - runs locally!

### Using the Application

1. **Select Your AI Model** from the dropdown
2. **Enter Your API Key** for the chosen model
3. **Optional Settings:**
   - Add a system prompt to customize AI behavior
   - Enable web search for current information
   - Provide a website URL to analyze
4. **Start Chatting!** Type your message and press Enter

### Tips for Better Results

- **System Prompts:** Use prompts like "You are a helpful coding assistant" or "Answer in a friendly, casual tone"
- **Web Search:** Enable when asking about current events or recent information
- **Website Analysis:** Provide URLs when you want to discuss specific web content
- **Context:** Keep enabled for natural conversations, disable for independent questions

## 🛠️ Troubleshooting

### Common Issues

**"Error connecting to API"**
- Make sure Docker containers are running: `docker-compose ps`
- Check if ports 8000 and 8501 are available
- Restart the services: `docker-compose restart`

**"API Error: Invalid API key"**
- Verify your API key is correct and active
- Check if you have sufficient credits/usage limits

**"Llama3 not working"**
- Make sure Ollama is installed and running
- Pull the model: `ollama pull llama3`
- Check if Ollama is accessible on port 11434

### Getting Help

1. Check the logs: `docker-compose logs`
2. Restart services: `docker-compose restart`
3. Full reset: `docker-compose down && docker-compose up -d`

## 🔧 Customization

### Changing Default Settings
Edit the `docker-compose.yml` file to modify:
- Port numbers
- Environment variables
- Volume mounts

### Adding New AI Models
The application is designed to be extensible. See the developer README for technical details.

## 📊 System Requirements

- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 1GB free space
- **Network:** Internet connection for AI APIs and web search
- **Docker:** Version 20.10 or later

## 🔒 Privacy & Security

- **API Keys:** Stored temporarily in memory, not saved to disk
- **Conversations:** Stored locally in Docker volumes
- **Data:** No data sent to third parties except chosen AI providers

## 📞 Support

- Check the logs for error messages
- Verify API keys and internet connection
- Ensure Docker containers are healthy
- Restart services if needed

Enjoy chatting with multiple AI models! 🚀

## 🤝 Contributing

I welcome contributions from the community! If you'd like to add features, fix bugs, or improve documentation, please open an issue or submit a pull request. See our guidelines in the repository for more details.

## 📝 License

This project is open source and available under the MIT License. See the LICENSE file for details.