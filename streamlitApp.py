import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configure page
st.set_page_config(
    page_title="Universal AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_BASE_URL = "http://localhost:8000"
LLM_OPTIONS = ["ChatGPT", "Claude", "Llama3"]

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Utility functions
def load_conversations():
    """Load conversation history from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/conversations")
        if response.status_code == 200:
            st.session_state.conversations = response.json()
    except Exception as e:
        st.error(f"Error loading conversations: {e}")

def send_message(message, llm_type, api_key, system_prompt=None, use_context=True, use_websearch=False, website_url=None):
    """Send message to API"""
    try:
        payload = {
            "message": message,
            "conversation_id": st.session_state.conversation_id,
            "llm_type": llm_type.lower(),
            "api_key": api_key,
            "system_prompt": system_prompt,
            "use_context": use_context,
            "use_websearch": use_websearch,
            "website_url": website_url
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.conversation_id = result["conversation_id"]
            return result["response"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None

def load_conversation(conv_id):
    """Load specific conversation"""
    try:
        response = requests.get(f"{API_BASE_URL}/conversations/{conv_id}")
        if response.status_code == 200:
            conv_data = response.json()
            st.session_state.conversation_id = conv_id
            st.session_state.messages = conv_data["messages"]
            st.rerun()
    except Exception as e:
        st.error(f"Error loading conversation: {e}")

def delete_conversation(conv_id):
    """Delete conversation"""
    try:
        response = requests.delete(f"{API_BASE_URL}/conversations/{conv_id}")
        if response.status_code == 200:
            load_conversations()
            if st.session_state.conversation_id == conv_id:
                st.session_state.conversation_id = None
                st.session_state.messages = []
            st.rerun()
    except Exception as e:
        st.error(f"Error deleting conversation: {e}")

# Sidebar
with st.sidebar:
    st.title("🤖 Universal AI Chat")
    
    # LLM Selection
    st.subheader("Model Settings")
    selected_llm = st.selectbox("Select LLM", LLM_OPTIONS, index=0)
    
    # API Key input
    api_key = st.text_input(
        f"{selected_llm} API Key", 
        type="password", 
        help=f"Enter your {selected_llm} API key"
    )
    
    # System Prompt
    st.subheader("System Prompt")
    system_prompt = st.text_area(
        "System Prompt (Optional)",
        placeholder="Enter system prompt to control AI behavior...",
        height=100
    )
    
    # Chat Options
    st.subheader("Chat Options")
    use_context = st.checkbox("Use Conversation Context", value=True)
    use_websearch = st.checkbox("Enable Web Search", value=False)
    
    # Website URL for scraping
    website_url = st.text_input(
        "Website URL (Optional)",
        placeholder="https://example.com",
        help="Provide a URL to scrape and ask questions about"
    )
    
    st.divider()
    
    # New Chat Button
    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    # Conversation History
    st.subheader("📜 Chat History")
    
    # Load conversations button
    if st.button("🔄 Refresh History"):
        load_conversations()
    
    # Display conversations
    if st.session_state.conversations:
        for conv in reversed(st.session_state.conversations):
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(
                    conv["title"][:30] + "...",
                    key=f"conv_{conv['conversation_id']}",
                    use_container_width=True
                ):
                    load_conversation(conv["conversation_id"])
            with col2:
                if st.button("🗑️", key=f"del_{conv['conversation_id']}"):
                    delete_conversation(conv["conversation_id"])
    else:
        st.info("No conversations yet")

# Main chat interface
st.title("💬 Universal AI Chat")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(f"*{message.get('timestamp', '')}*")

# Chat input
if prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error(f"Please provide your {selected_llm} API key in the sidebar.")
    else:
        # Add user message to chat
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"*{user_message['timestamp']}*")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(f"Getting response from {selected_llm}..."):
                response = send_message(
                    prompt,
                    selected_llm,
                    api_key,
                    system_prompt if system_prompt else None,
                    use_context,
                    use_websearch,
                    website_url if website_url else None
                )
                
                if response:
                    st.write(response)
                    
                    # Add assistant response to chat
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.messages.append(assistant_message)
                    st.caption(f"*{assistant_message['timestamp']}*")
                    
                    # Rerun to update the interface
                    st.rerun()

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.info("💡 **Tip**: Use system prompts to customize AI behavior")
with col2:
    st.info("🔍 **Feature**: Enable web search for current information")
with col3:
    st.info("🌐 **Feature**: Provide URLs to analyze web content")

# Load conversations on startup
if not st.session_state.conversations:
    load_conversations()