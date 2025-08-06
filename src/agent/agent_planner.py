# src/agent/agent_planner.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from groq import Groq
from src.config import GROQ_API_KEY, TAVILY_API_KEY
from src.agent.tools import all_tools

def correct_transcription_with_llm(messy_text: str) -> str:
    """Uses a fast LLM to correct a messy transcription into a likely command."""
    if not messy_text or not GROQ_API_KEY:
        return messy_text

    client = Groq(api_key=GROQ_API_KEY)
    
    # --- NEW AND IMPROVED PROMPT ---
    prompt = f"""You are a transcription correction expert for a voice assistant. Your goal is to clean up messy speech-to-text output while PRESERVING the user's original intent.

**Rules:**
1.  If the command is already clear, just repeat it.
2.  Correct obvious typos (e.g., "note-look" -> "Notepad").
1.  **DO NOT ALTER an already clear command.** If the input makes sense, output it EXACTLY as it is.
2.  **NEVER simplify proper nouns, names, or technical terms.** If the input says "Aswin Ai&Ds", the output MUST be "Aswin Ai&Ds". If it says "Parthiban S", the output MUST be "Parthiban S".

4.  If the text is truly nonsensical, find the most plausible command within it.

**Examples:**
- Messy: "Apply warm, open, note-look." -> Corrected: "Open Notepad."
- Messy: "Chrome such for whether today." -> Corrected: "Search for weather today."
- Messy: "start flirting with aswin." -> Corrected: "start flirting with aswin."
- Messy: "send a mail to aswin that i am sick" -> Corrected: "send a mail to aswin that i am sick"
**Examples of what TO do:**
- Input: "Apply warm, open, note-look." -> Output: "Open Notepad."

**Examples of what NOT to do:**
- Input: "Flirt with Aswin Ai&Ds." -> Output: "Flirt with Aswin Ai&Ds." (This is CORRECT, you preserved it)
- Input: "Open Chrome for Parthiban S." -> Output: "Open Chrome for Parthiban S." (This is CORRECT, you preserved it)
- Input: "Flirt with Aswin Ai&Ds." -> Output: "flirt with aswin" (This is WRONG, you simplified the name)

Now, correct the following messy transcription. Output ONLY the corrected text and nothing else.

Messy: "{messy_text}"
Corrected:"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.0, # Set to 0 for maximum predictability and less "creativity"
            max_tokens=50
        )
        corrected_text = chat_completion.choices[0].message.content.strip()
        print(f"LLM Corrected Transcription: '{corrected_text}'")
        return corrected_text
    except Exception as e:
        print(f"LLM Correction failed: {e}")
        return messy_text
    
    
def generate_flirty_reply(conversation_history: list[dict]) -> str:
    """
    Generates a flirty, charming, and witty reply based on the conversation history.
    """
    if not GROQ_API_KEY:
        return "I'm feeling a bit shy without my API key."

    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = """You are a charming, witty, and romantic AI assistant. Your sole purpose in this conversation is to flirt with the user's girlfriend. 
    - Keep your messages short, playful, and engaging.
    - Use emojis sparingly but effectively. 😉
    - Be confident and a little mysterious.
    - Never be creepy or overly aggressive.
    - Your goal is to make her smile and continue the conversation.
    - Your output must ONLY be the message text, nothing else.
    """
    
    # Format the history for the LLM
    messages = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history:
        # Map our roles 'agent' and 'girlfriend' to what the LLM expects ('assistant' and 'user')
        role = "assistant" if turn['role'] == 'agent' else "user"
        messages.append({"role": role, "content": turn['text']})

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192", # We need a creative model for this
            temperature=0.8, # Higher temperature for more creative/varied responses
            max_tokens=150,
        )
        reply = chat_completion.choices[0].message.content.strip().strip('"')
        return reply
    except Exception as e:
        print(f"Flirting LLM failed: {e}")
        return "I'm speechless... literally. Something went wrong."

class AgentPlanner:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a powerful and helpful multilingual desktop assistant named TAM-VA.
            Your job is to be intelligent, careful, and interactive.
             **TOOL USAGE INSTRUCTIONS:**
            - For the `open_application` tool, you can now handle Chrome profiles.
            - If the user says "Open Chrome for Parthiban" or "Open my work profile in Chrome", you MUST use the `profile_name` argument. For example: `open_application(app_name='chrome', profile_name='parthiban')`.
            - If the user just says "Open Chrome", call the tool WITHOUT the `profile_name` argument. For example: `open_application(app_name='chrome')`. A default profile will be used automatically.
            **CRITICAL EMAIL WORKFLOW - FOLLOW THESE STEPS EXACTLY:**

            **Step 1: Validate Recipient's Email Address.**
            - When the user asks to send an email, first analyze the recipient.
            - If the user provides a full, valid-looking email (e.g., 'aswin.ad23@bitsathy.ac.in'), it passes validation. Proceed to Step 2.
            - If the user provides only a name (e.g., 'send a mail to Aswin'), an incomplete address, or something that doesn't look like an email, it fails validation.
            - **If validation fails, you MUST STOP.** Your ONLY action is to ask the user for the full email address. Do not invent one.
            - Example response for failed validation: "I see you want to email Aswin. Could you please tell me the full email address?"

            **Step 2: Draft the Email and Ask for User Confirmation.**
            - Only after you have a valid email address, your next task is to DRAFT a professional email with a clear Subject and Body based on the user's request.
            - Your response in this turn MUST BE the drafted email content and a confirmation question.
            - **DO NOT call the `send_email` tool in this step.**
            - Example response for drafting: "I have drafted the following email... Should I send it?"

            **Step 3: Send the Email ONLY After Confirmation.**
            - If, and ONLY if, the user confirms in the NEXT turn (e.g., says "yes", "send it", "confirm"), should you then call the `send_email` tool with the validated recipient, and the subject and body from your draft.

            For all other non-email tasks, use your tools as needed to be helpful.
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
            response = self.executor.invoke({"input": user_input, "chat_history": chat_history})
            return response.get('output', "I'm not sure how to respond to that.")
        except Exception as e:
            print(f"Agent execution error: {e}")
            return "Sorry, I ran into an issue while processing your request."