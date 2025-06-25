import asyncio
from langchain_ollama import ChatOllama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import gradio as gr


llm = ChatOllama(model="qwen3", temperature=0, seed=3)


async def main(json_message: str):
    print(llm)
    server_params = StdioServerParameters(
        command="/Users/b0n00pr/.local/bin/uvx",
        args=[
            "mcp-neo4j-cypher",
            "--db-url",
            "bolt://localhost",
            "--username",
            "neo4j",
            "--password",
            "password",
        ],
    )

    prompt = f"""
Insert into neo4j the following json entity with insert timestamp
{json_message}
"""
    print(prompt)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            msg = {"messages": prompt}
            result = await agent.ainvoke(msg)
            # Collect pretty-printed outputs
            outputs = []
            for m in result["messages"]:
                # Try to get pretty-printed string, fallback to str(m)
                if hasattr(m, "pretty_print"):
                    try:
                        outputs.append(m.pretty_print(as_string=True))
                    except TypeError:
                        # If pretty_print doesn't support as_string, fallback
                        from io import StringIO
                        import sys
                        buf = StringIO()
                        sys_stdout = sys.stdout
                        sys.stdout = buf
                        m.pretty_print()
                        sys.stdout = sys_stdout
                        outputs.append(buf.getvalue())
                else:
                    outputs.append(str(m))
            return "\n".join(outputs)


""" if __name__ == "__main__":
    print("1. Main starting...")
    asyncio.run(main())
    print("12. The end.") """


with gr.Blocks() as demo:
    gr.Markdown("## Simple LLM Chat Interface (Streaming Output)")
    with gr.Row():
        with gr.Column():
            input_box = gr.Textbox(label="Input", placeholder="Type your message here...")
            submit_btn = gr.Button("Submit")
        with gr.Column():
            output_box = gr.Textbox(label="Output", lines=8, interactive=False)

    submit_btn.click(
        main,  # Pass the async function directly
        inputs=input_box,
        outputs=output_box,
        api_name="chat"
    )

demo.launch()



"""


Insert or update with the id in neo4j and add an audit attribute which is of list type with the summary of what changed.

 Given a JSON, parse and identifiy the Nodes and insert or update it in neo4j. Also add a new audit entry with one line summary of significant attributes. 


 
You are a Neo4j data integration assistant. Your task is to:

Parse the provided JSON input .
Identify entities (Nodes) based on the JSON structure and content.
Connect to a Neo4j database and:
Check if the Node already exists , using a unique identifier (e.g., id, or any other relevant key).
If it exists , update its properties including setting the updated_at timestamp.
If it does not exist , create the Node with all current properties and set the created_at and updated_at timestamps.
For each operation (create or update), generate a one-line summary of the event using significant attributes like: id, status, location, item, quantity, etc.
Append this summary to a list property called audit on the Node.
If the JSON contains new attributes not previously present , add them to the existing Node in Neo4j.
Ensure that your logic is robust to handle varying JSON structures and gracefully extend the schema as needed.
Return a confirmation of the operation(s) performed, including what was created/updated and how the audit trail was extended.  

{"containerTrackingId" : "abcd1234-1",  "location":"door101", "item":334343,"quantity":5, "status":"AVAILABLE"}

{"containerTrackingId" : "abcd1234-1", "sorter":"fid-lower-001", "lane": 34}

{"containerTrackingId" : "abcd1234-1", "status":"PICKED"}
"""
