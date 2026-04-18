import streamlit as st 
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


#************************* utility functions **********************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, "New Chat")
    st.session_state['message_history'] = []

def add_thread(thread_id, name="New Chat"):
    if not any(t["id"] == thread_id for t in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({
            "id": thread_id,
            "name": name
        })

def load_conversation(thread_id):
    state = chatbot.get_state(config ={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

# Initialize session state
# ***********************************session setup *******************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'], "New Chat")

#*********************************** Sidebar UI **********************************************

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')



for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread["name"],key = thread["id"]):
        st.session_state['thread_id'] = thread["id"]
        messages = load_conversation(thread["id"])
        
        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'  
            temp_messages.append({'role':role,'content':msg.content})       
        
        st.session_state['message_history'] = temp_messages

#******************************************************************************

# Display chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# User input
user_input = st.chat_input('Type here')

if user_input:
    
    # If it's first message → set thread name
    for thread in st.session_state['chat_threads']:
        if thread["id"] == st.session_state['thread_id'] and thread["name"] == "New Chat":
            thread["name"] = user_input[:30]   # first 30 chars

    # Store user message
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message('assistant'):
       
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode = 'messages'
             )
        )
    # Store assistant message
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message}
    )
 