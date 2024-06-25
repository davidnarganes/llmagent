import pandas as pd
import streamlit as st
import logging
import io
from datetime import datetime
from dotenv import load_dotenv
from llmagent.agent.agent import TargetDiscoveryAgent


log_buffer = io.StringIO()

class StreamlitLogger(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.write(log_entry + '\n')

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'logs/{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'),
        logging.StreamHandler(),
        StreamlitLogger()
    ]
)

load_dotenv()

st.set_page_config(page_title="Target Discovery")

st.markdown("""
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 450px;
        max-width: 450px;
    }
    </style>
""", unsafe_allow_html=True)

def on_model_change():
    model_name = st.session_state.get('model_name')
    st.session_state['agent'] = TargetDiscoveryAgent(
        provider='openai',
        model_name=model_name,
        max_iterations=3,
        verbose=True
    )

def execute_prompt(agent, prompt):
    if any(entry['user'] == prompt for entry in st.session_state['conversation']):
        return  # Prompt already processed, avoid duplication

    st.chat_message("user").write(prompt)
    try:
        response = agent.run(prompt)
        st.chat_message("assistant").write(response)
        st.session_state['conversation'].append({'user': prompt, 'assistant': response})
        
    except Exception as e:
        st.chat_message("assistant").write(f"Error: {str(e)}")

# Initialize session state for conversation
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# List of some available models
models = [
    'gpt-4-turbo',
    'gpt-3.5-turbo',
    'gpt-base'
]

if 'agent' not in st.session_state:
    st.session_state['agent'] = TargetDiscoveryAgent(
        provider='openai',
        model_name='gpt-4-turbo', # Default
        max_iterations=3,
        verbose=True
    )

pre_prompts = [
    'What 2 roles does gene APP play in Alzheimer\'s disease? Are there any 2 therapeutic targets in those pathways?',
    'Identify 3 pathways associated with Parkinson\'s disease and potential drug targets in these pathways',
    'Find 3 downstream effects of TP53 mutations in colorectal cancer.',
    'Determine 3 potential drug targets for type 2 diabetes mellitus.'
]

with st.sidebar:
    st.markdown('## Which model?')
    model_name = st.selectbox('Select a model from https://platform.openai.com/docs/models', models, key='model_name', on_change=on_model_change)

    st.markdown('## What can I ask?')
    st.markdown('Anything but some examples here:')
    for prompt in pre_prompts:
        st.button(prompt, on_click=lambda p=prompt: execute_prompt(st.session_state['agent'], p))

    st.markdown('---')

    tools = st.session_state['agent'].tools
    tool_list = pd.Series({f"✅ {name}": tool["description"] for name, tool in tools.items()}).reset_index()
    tool_list.columns = ['Tool', 'Description']

    st.markdown(f"# {len(tool_list)} available tools")
    st.dataframe(tool_list, use_container_width=True, hide_index=True, height=200)

if user_input := st.chat_input():
    execute_prompt(st.session_state['agent'], user_input)

# Display the conversation history
for entry in st.session_state['conversation']:
    st.chat_message("user").write(entry['user'])
    st.chat_message("assistant").write(entry['assistant'])

# Display log messages
st.sidebar.markdown('## Logs')
log_content = log_buffer.getvalue()
st.sidebar.text_area('Log Output', log_content, height=200)