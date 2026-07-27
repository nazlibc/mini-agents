from src.config import create_llm

llm = create_llm()
reply =llm.invoke("Say hi in exactly 5 words, no more, no less.")
print(reply.content)


# .invoke() sends one message and blocks until the answer arrives; 
# it returns an AIMessage object whose .content is the text. Run it from the repo root: