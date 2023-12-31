import json,requests,re,os
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime, timedelta

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class FunctionClassifier():
    def __init__(self):
        with open('functions.json') as file:
            self.data = json.load(file)
        self.llm = ChatOpenAI(openai_api_key= OPENAI_API_KEY, temperature=0.0)
    
    def get_function_descriptions(self):
        descriptions = []
        for x in self.data:
            descriptions.append(x['description'])
        return descriptions
    
    def retrieve_function(self, query, function_buffer_memory: ConversationBufferMemory):
        print(f'--{datetime.now()}--FunctionClassifier::retrieve_function')
        function_desc = self.get_function_descriptions()
        prompt = PromptTemplate(
            input_variables=['chat_history','function_desc', 'query'],
            template = """
            You are an AI bot, you are communicating with a system which needs you to predict the most relevent function for the user query.
            \nCurrent Converstaion History: 
            {chat_history}

            \nInstruction Set:
            Provided this list of function definitions Definitions :{function_desc} , take this Query : {query} and match the query
            with a single function's description. If it is found that the query does not match a single function's description,return -1. \
            Otherwise, ensure that the query matches the first of the query that you as an AI can generate a classification for which query matches the definition. 
            
            Take Current Converstion Histoy into classification consideration to match follow up questions. If you feel user is asking about a follow up, 
            your classification should inclined towards the function you predicted last time. If user is using words like 'this' and 'that' but not 
            giving any specific information on what he is referring to, always use the last matching index from history.

            Once a match is found, return the index of the function description from function definitions list. Make sure to process\
            each decription carefully when classifying which description matches the query. Print Matching index in last line of your result
            In the second last line print the one line reason for why you chose this function. 
            In the last line print the index digit number only that you found matches best in format MATCHING_INDEX=""",
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(function_desc= str(self.get_function_descriptions()), query=query, chat_history=function_buffer_memory.load_memory_variables({})) 
        trimmed_result = result.split('\n')
        filtered_array = list(filter(lambda item: item != '', trimmed_result))
        
        # last_word = result.split()[-1]
        function_buffer_memory.save_context({"Human":query}, {"AI":str(trimmed_result[-3:])})

        match = re.search(r"\d+", result)        
        if match:
            output_value = match.group()
            

        print(f"--{datetime.now()}--FunctionClassifier::matching_index::", int(output_value))
        return [(self.data[int(output_value)])]