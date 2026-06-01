from app.rag.rag_chain import ask


question = "What is the pit lane speed limit?"

response = ask(question)

print("\nANSWER:\n")

print(response)