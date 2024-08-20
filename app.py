import os
from dotenv import load_dotenv
from example_data.utils import categories, training_data_tags
from src.coder_assistant import CoderAssistant
import pandas as pd
from langchain_groq import ChatGroq


load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY") 

# Load the data. Take into account that this is an example. In a real scenario, you would have to load your own data.
# Data is a collection of reviews dowloaded from Kaggle.
reviews = pd.read_csv("example_data/reviews_data.csv")
data_to_classify = reviews["Text"].values.tolist()
# 20% of the data will be used for aligning the AI with the user's categories
training_data = data_to_classify[:int(len(data_to_classify)*0.20)]
# 80% of the data will be used for auto-classification
auto_classify_data = data_to_classify[int(len(data_to_classify)*0.20):]


# Load the model. In this case, we are using the Llama model from ChatGROQ.
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Create the assistant (orchestrator) and compile it.
assistant = CoderAssistant(llm, categories, training_data, training_data_tags, auto_classify_data).compile()

# The following code will generate an image with the graph of the assistant.
base64_graph = assistant.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(base64_graph)


# Prepare the thread for the assistant and invoke it.
thread = {"configurable": {"thread_id": "1"}}
assistant.invoke({"keys": {}}, thread)
state = assistant.get_state(thread).values

# The following loop will allow the user to correct the AI's predictions and let the assistant learn from the user's feedback.
while "final_response" not in state["keys"]:
    conflictive_responses = state["keys"]["conflictive_responses"]
    lessons_learned = state["keys"]["lessons_learned"]
    for response in conflictive_responses:
        review = response["review"]
        ai_category = response["ai_category"]
        ai_reason = response["ai_reason"]
        user_category = response["user_category"]
        print(f"Review: {review}")
        print(f"AI Category: {ai_category}")
        print(f"AI Reason: {ai_reason}")
        print(f"Previous expected category: {user_category}")
        category = input("Why do you think the AI is wrong and what is your reasoning for the correct category? ")
        response["user_response"] = category
        print("\n")

    assistant.update_state(thread, {"keys": {"conflictive_responses": conflictive_responses, "lessons_learned": lessons_learned}})
    response = assistant.invoke(None, thread)
    state = assistant.get_state(thread).values


# At the end, we can get the final response from the assistant. (We could also get the lessons learned in the training process)
final_state = assistant.get_state(thread).values
final_state["keys"]["final_response"]
final_state["keys"]["lessons_learned"]