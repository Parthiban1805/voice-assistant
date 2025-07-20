from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.config import GROQ_API_KEY
from src.agent.tools import all_tools
from groq import Groq
from src.config import GROQ_API_KEY

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
def correct_transcription_with_llm(messy_text: str) -> str:
    """Uses a fast LLM to correct a messy transcription into a likely command."""
    if not messy_text:
        return ""

    client = Groq(api_key=GROQ_API_KEY)
    
    prompt = f"""
    You are a transcription correction expert for a voice assistant.
    Your task is to correct the user's raw, often messy, transcription into a clear, actionable command.
    The user is likely to mention applications like Notepad, Chrome, or ask to search the web.
    
    Examples:
    - Messy: "Apply warm, open, note-look." -> Corrected: "Open Notepad."
    - Messy: "Chrome such for whether today." -> Corrected: "Search for weather today."
    - Messy: "Hopen new file." -> Corrected: "Open new file."

    Now, correct the following messy transcription. Output ONLY the corrected text and nothing else.

    Messy: "{messy_text}"
    Corrected:
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", # Use a small, fast model for this
            temperature=0.1,
        )
        corrected_text = chat_completion.choices[0].message.content.strip()
        print(f"LLM Corrected Transcription: '{corrected_text}'")
        return corrected_text
    except Exception as e:
        print(f"LLM Correction failed: {e}")
        return messy_text # Fallback to the original messy text
