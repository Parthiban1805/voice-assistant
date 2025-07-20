from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.config import GROQ_API_KEY
from src.agent.tools import all_tools

class AgentPlanner:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")
        
        # This prompt is CRITICAL for Tanglish understanding
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a powerful and helpful multilingual desktop assistant named TAM-VA.
            Your job is to assist the user by executing tasks on their computer.
            You must understand commands in English, Tamil, and Tanglish (a mix of English and romanized Tamil).
            
            Analyze the user's command and use the available tools to perform the requested action.
            
            Tanglish Interpretation Guide:
            - "search pannu" means "search for"
            - "open pannu" means "open"
            - "ennoda" means "my"
            - "oru email anupu" means "send an email"
            - "enna irukku" means "what is there"
            - "news padi" means "read the news"
            
            Think step-by-step and select the best tool for the job. Respond in a concise, friendly, and helpful tone.
            """),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        llm = ChatGroq(model="llama3-70b-8192", temperature=0)
        agent = create_tool_calling_agent(llm, all_tools, prompt)
        self.executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)

    def run_agent(self, user_input, chat_history):
        try:
            response = self.executor.invoke({
                "input": user_input,
                "chat_history": chat_history
            })
            return response.get('output', "I'm not sure how to respond to that.")
        except Exception as e:
            print(f"Agent execution error: {e}")
            return "Sorry, I ran into an issue while processing your request."