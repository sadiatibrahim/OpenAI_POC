import json,requests,re,os
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import datetime, timedelta

OPENAI_API_KEY = os.environ.get("SECRET_KEY")

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
        print(f'--{datetime.now()}--FunctionClassifier::chat_history::',function_buffer_memory.load_memory_variables({}))
        function_desc = self.get_function_descriptions()
        prompt = PromptTemplate(
            input_variables=['chat_history','function_desc', 'query'],
            # template= """
            # Current Converstion Histoy:
            # {chat_history}
            # Instruction Set:
            # Provided this list of function definitions Definitions :{function_desc} , take this Query : {query} and match the query
            # with a single function's description. If it is found that the query does not match a single function's description,
            # return -1. Otherwise, ensure that the query matches the first of the query that you as an AI can 
            # generate a classification for which query matches the definition. If a match is found, return the index of the function description from the list. \
            # Take Current Converstion Histoy into classification consideration to match follow up questions. If you feel user is asking about a follow up, 
            # your classification should inclined towards the function you predicted last time.
            # If the question is asking about some standard problem they are facing, or maybe looking for next steps be inclined towards  get_standard_procedure. \
            # if user is asking following up steps for database or command line, their next steps could be available in standard procedure if that is the method\
            # selected last time in the conversation history.
            # Make sure to process each decription carefully when classifying which description matches the query. 
            # Provide me details of how you classified the above question to its corresponding function.
            # In the last line of your result, always return the matching index so i can directly retrieve the matching function from the functions json
            # Index always starts from 0, so if function 1 matches that is 0 index, and so on.""",
            template = """
            You are an AI bot, you are communicating with a system which needs you to predict the most relevent function for the user query.
            \nCurrent Converstaion History: 
            {chat_history}
            \nInstruction Set:
            Provided this list of function definitions Definitions :{function_desc} , take this Query : {query} and match the query
            with a single function's description. If it is found that the query does not match a single function's description,
            return -1. Otherwise, ensure that the query matches the first of the query that you as an AI can 
            generate a classification for which query matches the definition. 
            Take Current Converstion Histoy into classification consideration to match follow up questions. If you feel user is asking about a follow up, 
            your classification should inclined towards the function you predicted last time. If user is using words like 'this' and 'that' but not 
            giving any specific information on what he is referring to, always use the last matching index from history.
            Once a match is found, return the index of the function description from function definitions list. Make sure to process\
            each decription carefully when classifying which description matches the query. Print Matching index in last line of your result""",
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(function_desc= str(self.get_function_descriptions()), query=query, chat_history=function_buffer_memory.load_memory_variables({})) 
        trimmed_result = result.split('\n')
        filtered_array = list(filter(lambda item: item != '', trimmed_result))

        print('FunctionClassifier::Length of Result:',len(filtered_array))
        print('\033[94m')
        print(f'\n\n--{datetime.now()}--' + str(filtered_array[-3:]))
        print('\033[32m')        
        
        last_word = result.split()[-1]
        function_buffer_memory.save_context({"Human":query}, {"AI":str(trimmed_result[-3:])})

        if last_word.endswith('.'):
            last_word = last_word[:-1]

        print(f"\n\n--{datetime.now()}--FunctionClassifier::matching_index::", int(last_word))
        return [(self.data[int(last_word)])]