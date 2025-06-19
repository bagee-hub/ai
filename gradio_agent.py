import gradio as gr
from langchain.llms import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


llm = Ollama(model="qwen3")


conversation = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)


def chat(message):
    response = conversation.run(input=message)
    return response


iface = gr.Interface(
    fn=chat,
    inputs="text",
    outputs="text",
    title="Chat",
    description="A simple chat application"
)

# Launch the interface
iface.launch()
