from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import PromptTemplate
from src.utils import State
from sklearn.metrics import cohen_kappa_score
import time
import re

MAX_RETRIES = 3

class CoderAssistant:
    def __init__(self, llm, categories: dict[str, str], train_data: list[str], training_data_tags: list[str], data_to_classify: list[str]):
        self.llm = llm
        self.categories = categories
        self.train_data = train_data
        self.training_data_tags = training_data_tags
        self.auto_classify_data = data_to_classify
    
    def generate_nodes(self):
        def training_phase(state: State):
            '''
            This node will use the training data to train the AI model to categorize reviews. It will use the LLM model to generate responses for each review in the training data. 
            AI responses contain the AI's reasoning, and the category assigned by the AI.

            Also, this node could include previous lessons learned that can be taken into account before categorizing the review, if applicable.
            '''
            if "lessons_learned" in state["keys"]:
                lessons_learned = state["keys"]["lessons_learned"]
                prompt_template = PromptTemplate(
                    template="""You are a world class AI assistant that can help categorize reviews. Your task is to categorize the following review: 
                    {review}
                    Please reason about the review and select the appropriate category from the following list:
                    {categories}
                    Your response must be in the following format: '<reason>reason</reason> <category>category</category>' including in any case the xml tags. So your response should look like this: '<reason>It is a great product</reason> <category>Praise</category>
                    Category must be only the name of the category, not the number and not the description. If you are unsure about the category, you must choose the most appropriate one. Good luck!
                    
                    Previous lessons learned that can be taken into account before categorizing the review, if applicable:
                    {lessons_learned}
                    """,
                input_variables=["review", "categories", "lessons_learned"],
                )
            
            else:
                prompt_template = PromptTemplate(
                    template="""You are a world class AI assistant that can help categorize reviews. Your task is to categorize the following review: 
                    {review}
                    Please reason about the review and select the appropriate category from the following list:
                    {categories}
                    Your response must be in the following format: '<reason>reason</reason> <category>category</category>' including in any case the xml tags. So your response should look like this: '<reason>It is a great product</reason> <category>Praise</category>
                    Category must be only the name of the category, not the number and not the description. If you are unsure about the category, you must choose the most appropriate one. Good luck!
                    """,
                input_variables=["review", "categories"],
                )
                lessons_learned = None
            
            chain = prompt_template | self.llm
            categories_str = "\n".join([f"{key}: {value}" for key, value in self.categories.items()])
            ai_responses = []
            for review in self.train_data:
                tries = 0
                while tries < MAX_RETRIES:
                    try:
                        if lessons_learned:
                            response = chain.invoke({
                                "review": review,
                                "categories": categories_str,
                                "lessons_learned": lessons_learned
                            }).content
                        else:
                            response = chain.invoke({
                                "review": review,
                                "categories": categories_str
                            }).content
                        category = re.search(r"<category>(.*)</category>", response).group(1)
                        reason = re.search(r"<reason>(.*)</reason>", response).group(1)
                        ai_responses.append({
                            "review": review,
                            "ai_reason": reason,
                            "ai_category": category
                        })
                        time.sleep(1)
                        break
                    except Exception as e:
                        tries += 1
                        time.sleep(5)
            return {
                "keys": {
                    "responses": ai_responses,
                    "lessons_learned": lessons_learned
                }
            }
        def cohen_kappa_eval(state: State):
            '''
            This node will evaluate the AI's responses using the Cohen's Kappa coefficient. If the coefficient is greater than 0.6, the AI's responses are considered acceptable. Otherwise, the AI's responses are considered conflictive and the node will return the conflictive responses for further analysis.
            '''
            ai_responses = state["keys"]["responses"]
            lessons_learned = state["keys"]["lessons_learned"]

            tags_list=[response["ai_category"] for response in ai_responses]

            kappa_cohens = cohen_kappa_score(tags_list, self.training_data_tags)

            if kappa_cohens > 0.6:
                return {
                    "keys": {
                        "conflictive_responses": [],
                        "lessons_learned": lessons_learned
                    }
                }
            else:
                conflictive_responses = []
                for i in range(len(ai_responses)):
                    if tags_list[i] != self.training_data_tags[i]:
                        conflictive_responses.append({
                            "review": ai_responses[i]["review"],
                            "ai_reason": ai_responses[i]["ai_reason"],
                            "ai_category": ai_responses[i]["ai_category"],
                            "user_category": self.training_data_tags[i]
                        })
                return {
                    "keys": {
                        "conflictive_responses": conflictive_responses,
                        "lessons_learned": lessons_learned
                    }
                }
        def human_feedback(state: State):
            '''
            This node will analyze the conflictive responses and extract lessons learned from the misclassified data with user feedback. The user will provide reasoning for the correct category and the AI's reasoning for the misclassification. The node will return the lessons learned based on the user feedback.
            '''
            conflictive_responses = state["keys"]["conflictive_responses"]
            lessons_learned = state["keys"]["lessons_learned"]
            
            conflictive_responses_text = ""
            for response in conflictive_responses:
                conflictive_responses_text += f"Review: {response['review']}\n"
                conflictive_responses_text += f"AI Category: {response['ai_category']}\n"
                conflictive_responses_text += f"AI Reason: {response['ai_reason']}\n"
                conflictive_responses_text += f"Previous expected category: {response['user_category']}\n"
                conflictive_responses_text += "Why do you think the AI is wrong and what is your reasoning for the correct category?\n"
                conflictive_responses_text += f"User Response: {response['user_response']}\n"
                conflictive_responses_text += "\n\n"
            
            if lessons_learned:
                prompt = PromptTemplate(
                    template="""Extract lessons learned from misclassified data with user feedback. Analyze the feedback and the misclassification to derive generalizable knowledge for improving future classifications. Do not reference specific reviews or include introductory phrases. If user feedback indicates the classification was correct, no lessons should be recorded. Focus solely on abstracting the reasons for the failure and providing actionable insights.
                    Misclassified data is organized as follows:
                    1. Review: The review that was misclassified
                    2. AI Category: The category that the AI assigned to the review
                    3. AI Reason: The reason that the AI assigned to the review
                    4. Previous expected category: The category that the user expected the review to be classified as
                    5. User Response: The user's response to the AI's classification
                    {conflictive_responses}

                    Previous lessons learned to take into account before categorizing the review. You have to include or modify the previous lessons learned with the new lessons learned.
                    {lessons_learned}
    """,
                    input_variables=["conflictive_responses", "lessons_learned"],
                )
                chain = prompt | self.llm
                response = chain.invoke({
                    "conflictive_responses": conflictive_responses_text,
                    "lessons_learned": lessons_learned
                }).content
            else:
                prompt = PromptTemplate(
                    template="""Extract brief and actionable lessons from misclassified data and user feedback. Analyze the feedback and misclassification to derive generalizable insights for future classifications. Do not reference specific reviews or use introductory phrases. If feedback indicates the classification was correct, no lessons should be recorded. Focus on abstracting reasons for failure and providing concise, actionable insights.

Misclassified data includes:

Review: Misclassified review
AI Category: Assigned category
AI Reason: AI’s reasoning
Expected Category: User’s expected category
User Response: User feedback
                    {conflictive_responses}

    """,
                    input_variables=["conflictive_responses"],
                )
                chain = prompt | self.llm
                response = chain.invoke({
                    "conflictive_responses": conflictive_responses_text
                }).content
            
            return {
                "keys": {
                    "lessons_learned": response
                }
            }
        def auto_classify(state: State):
            '''
            This node will use the AI model to categorize reviews in the auto-classify data. It will generate responses for each review in the auto-classify data.
            '''
            if "lessons_learned" in state["keys"] and state["keys"]["lessons_learned"]:
                lessons_learned = state["keys"]["lessons_learned"]
                lessons_learned = "Previous lessons learned that can be taken into account before categorizing the review, if applicable:\n" + lessons_learned
            else:
                lessons_learned = ""
            
            categories_str = "\n".join([f"{key}: {value}" for key, value in self.categories.items()])
            prompt_template = PromptTemplate(
                    template="""You are a world class AI assistant that can help categorize reviews. Your task is to categorize the following review: 
                    {review}
                    Please reason about the review and select the appropriate category from the following list:
                    {categories}
                    Your response must be in the following format: '<reason>reason</reason> <category>category</category>' including in any case the xml tags. So your response should look like this: '<reason>It is a great product</reason> <category>Praise</category>
                    Category must be only the name of the category, not the number and not the description. If you are unsure about the category, you must choose the most appropriate one. Good luck!
                    
                    {lessons_learned}
                    """,
                input_variables=["review", "categories", "lessons_learned"],
                )

            auto_classify_data = self.auto_classify_data
            ai_responses = []
            for review in auto_classify_data:
                tries = 0
                while tries < MAX_RETRIES:
                    try:
                        chain = prompt_template | self.llm
                        
                        response = chain.invoke({
                            "review": review,
                            "categories": categories_str,
                            "lessons_learned": lessons_learned
                        }).content
                    
                        category = re.search(r"<category>(.*)</category>", response).group(1)
                        reason = re.search(r"<reason>(.*)</reason>", response).group(1)
                        ai_responses.append({
                            "review": review,
                            "ai_reason": reason,
                            "ai_category": category
                        })
                        time.sleep(1)
                        break
                    except Exception as e:
                        tries += 1
                        time.sleep(5)
            
            return {
                "keys": {
                    "final_response": ai_responses,
                    "lessons_learned": lessons_learned
                }
            }
        return {
            "training_phase": training_phase,
            "cohen_kappa_eval": cohen_kappa_eval,
            "human_feedback": human_feedback,
            "auto_classify": auto_classify
        }
    
    def generate_edges(self):
        def should_realign(state: State):
            conflictive_responses = state["keys"]["conflictive_responses"]
            if len(conflictive_responses) > 0:
                return "human_feedback"
            else:
                return "auto_classify"
        return {
            "training_phase": should_realign
        }
    
    def compile(self):
        nodes = self.generate_nodes()
        edges = self.generate_edges()
        graph = StateGraph(State)
    


        graph.add_node("training_phase", nodes["training_phase"])
        graph.add_node("cohen_kappa_eval", nodes["cohen_kappa_eval"])
        graph.add_node("human_feedback", nodes["human_feedback"])
        graph.add_node("auto_classify", nodes["auto_classify"])

        graph.set_entry_point("training_phase")
        graph.add_edge("training_phase", "cohen_kappa_eval")
        graph.add_conditional_edges("cohen_kappa_eval",
            edges["training_phase"],
            {
                "human_feedback": "human_feedback",
                "auto_classify": "auto_classify"
            }
        )
        graph.add_edge("human_feedback", "training_phase")
        graph.add_edge("auto_classify", END)

        memory_saver = MemorySaver()
        return graph.compile(checkpointer=memory_saver, interrupt_before=["human_feedback"])

