from config import KEEP_CHAT_SESSIONS

class History:
    def __init__(self):
        self.chat_sessions = {}

    def addMessage(self, session_id: str, role: str, content: str):
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = []
            
        self.chat_sessions[session_id].append({"role": role, "content": content})
        self.chat_sessions[session_id] = (self.chat_sessions[session_id][-KEEP_CHAT_SESSIONS:])

    def getHistory(self, session_id: str):
        return self.chat_sessions.get(session_id,[])

    def buildConversationString(self, session_id: str):
        history = self.getHistory(session_id)
        if not history:
            return ""
        
        lines = []
        for msg in history:
            role = msg["role"].upper()
            lines.append(f"{role}: {msg['content']}")
            
        return "\n".join(lines)