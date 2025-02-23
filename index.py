import ollama
from langchain_community.tools import DuckDuckGoSearchResults

llm = "llama3.2"

stream = ollama.generate(
    model = llm, 
    prompt = "What is the meaning of life?",
    stream = True
)






def search_yf(query: str) -> str:
  engine = DuckDuckGoSearchResults(backend="news")
  return engine.run(f"site:finance.yahoo.com {query}")

def search_web(query: str) -> str:
  engine = DuckDuckGoSearchResults(backend="news")
  return engine.run(f"{query}")

tool_search_web = {'type':'function', 'function':{
  'name': 'search_web',
  'description': 'Search the web',
  'parameters': {'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type':'str', 'description':'the topic or subject to search on the web'},
}}}}

tool_search_yf = {'type':'function', 'function':{
  'name': 'search_yf',
  'description': 'Search for specific financial news',
  'parameters': {'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type':'str', 'description':'the financial topic or subject to search'},
}}}}


prompt = '''You are an assistant with access to tools, you must decide when to use tools to answer user message.'''
messages = [{"role": "system", "content": prompt}]

while True:
    ##INPUT
    try:
        q = input('🙂 >')
    except EOFError:
        break
    if q == 'quit':
        break
    if(q.strip() == ""):
        continue
    messages.append({"role": "user", "content": q})
    
    ##MODEL
    agent_res = ollama.chat(
        model = llm, 
        messages = messages,
        tools = [tool_search_web, tool_search_yf]
    )
    dic_tools = {'search_web':search_web, 'search_yf':search_yf}

    if "tool_calls" in agent_res["message"]:
        for tool in agent_res["message"]["tool_calls"]:
            t_name, t_inputs = tool["function"]["name"], tool["function"]["arguments"]
            if f := dic_tools.get(t_name):
                ### calling tool
                print('🔧 >', f"\x1b[1;31m{t_name} -> Inputs: {t_inputs}\x1b[0m")
                messages.append( {"role":"user", "content":"use tool '"+t_name+"' with inputs: "+str(t_inputs)} )
                ### tool output
                t_output = f(**tool["function"]["arguments"])
                print(t_output)
                ### final res
                p = f'''Summarize this to answer user question, be as concise as possible: {t_output}'''
                res = ollama.generate(model=llm, prompt=q+". "+p)["response"]
            else:
                print('🤬 >', f"\x1b[1;31m{t_name} -> NotFound\x1b[0m")
 
    if agent_res['message']['content'] != '':
        res = agent_res["message"]["content"]
     
    print("👽 >", f"\x1b[1;30m{res}\x1b[0m")
    messages.append( {"role":"assistant", "content":res} )
