conversation_memory = []

def add_memory(q):
    conversation_memory.append(q)

def get_context():
    return "\n".join(conversation_memory[-5:])