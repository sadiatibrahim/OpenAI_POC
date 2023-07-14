import json
import requests
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
import re
import os

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
    
    def retrieve_function(self, query):
        function_desc = self.get_function_descriptions()
        prompt = PromptTemplate(
            input_variables=['function_desc', 'query'],
            template= """
            Provided this list of function definitions Definitions :{function_desc} , take this query Query : {query} and match the query
                         with a single function's description. if it is found that the query does not match a single function's description,
                         return -1. Otherwise, ensure that the query matches the first of the query that you as an AI can 
                         generate a classification for which query matches the definition. If a match is found, return the index of the function description from the list.Make sure to process\
                         each decription carefully when classifying which description matches the query""",
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(function_desc= str(self.get_function_descriptions()), query=query)
        print(result)
        # The string containing the index value
        index_string = "index = match_query(Definitions, Query)\nprint(index)  # Output: 0"

        # Extract the value using regular expressions
        match = re.search(r'Output:\s*(\d+)', index_string)

        if match:
            output_value = match.group(1)


        
        return [(self.data[int(output_value)])]
    

