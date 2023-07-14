import openai
import requests
import json
import os
import pytz
from datetime import datetime
from functionclassifier import FunctionClassifier
OPENAI_API_KEY = os.environ.get("SECRET_KEY")
def get_batch_progress(query):

    #Assume this process is connecting to API and getting json data
    with open('summaryAPI.json') as file:
        data = json.load(file)

    #call the function that summarizes the data
    result = get_summary(data, query)
    return result

def get_summary(json_data, query):
    # Get the current time
    current_time = datetime.now()

    # Convert the current time to a specific timezone
    timezone = pytz.timezone('US/Eastern')  # Example: US Eastern Time (EST)
    current_time = current_time.astimezone(timezone)

    # Format the time as hour:minutes AM/PM
    time_format = "%I:%M%p"  # 12-hour format with leading zero, e.g., 07:30AM
    formatted_time = current_time.strftime(time_format)


    prompt = f"Given this Json data: {json_data}/n Give a summary of this data based on this query: {query} \
        for example, if the query is : tell me the progress of batch data/n, your answer should be the summary \
        of this json file provided. summarize it as sentences. start the sentence by saying 'As of {formatted_time} EST here is the summary \
        of wealth management batch'. if the query is about a specific area, e.g if the query is tell me \
        about the progress of mainframe batch or mainframe batch jobs, your answer should be the summary of only mainframe data."
    
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    payload= {
      "model":"text-davinci-003",
      "prompt": prompt,
      "max_tokens" : 1024,
      "temperature" : 0
    }

    try:
        result = requests.post("https://api.openai.com/v1/completions", headers=headers, data=json.dumps(payload))
    except Exception as e:
        return {'status': -1, 'error': 'Error occured' + str(e)}
    
    return {'status':0, 'result': result.text}

def main_function_call(query):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content":query}]

    function = FunctionClassifier()
    function = function.retrieve_function(query)

    payload = {"model" : "gpt-3.5-turbo-0613",
               "messages" : messages,
               "functions" : function,
               "function_call" : "auto",
               "temperature" : 0.0,
               "top_p" : 1.0,
               "frequency_penalty": 0.0,
               "presence_penalty" : 0.0,
               "max_tokens" : 1000
    }

    data = json.dumps(payload).encode('utf-8')
    resp = requests.post(url, headers=headers, data=data)
    resp_json = json.loads(resp.text)

    return resp_json


query_str = input("What would you like to know about the TEREO Batch Jobs? \n> ")

function_call_output = main_function_call(query_str)

#pass argument to function
function_name = eval(function_call_output['choices'][0]['message']['function_call']['name'])
function_argument = json.loads(function_call_output['choices'][0]['message']['function_call']['arguments'])

result = json.loads(function_name(**function_argument).get("result", 'error'))
# a = get_data(query_str)
# print(a)
resp = result['choices'][0]['text']
print(resp)

    

