import openai
import requests
import json
import os
import pytz
from datetime import datetime, timedelta
from functionclassifier import FunctionClassifier

OPENAI_API_KEY = os.environ.get("SECRET_KEY")

date = datetime.now().date()
previous_date = date - timedelta(days=1)

def get_batch_progress(query):
    #make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/batch-summary?date={previous_date}"
    # data = requests.get(url)


    #Assume this process is connecting to API and getting json data
    with open(r'OpenAI_POC\summaryAPI.json') as file:
        data = json.load(file)

    #call the function that summarizes the data
    result = get_summary_batch_progress(data, query)
    return result

def get_summary_batch_progress(json_data, query):
    # Get the current time
    current_time = datetime.now()

    # Convert the current time to a specific timezone
    timezone = pytz.timezone('US/Eastern')  # Example: US Eastern Time (EST)
    current_time = current_time.astimezone(timezone)

    # Format the time as hour:minutes AM/PM
    time_format = "%I:%M%p"  # 12-hour format with leading zero, e.g., 07:30AM
    formatted_time = current_time.strftime(time_format)


    prompt = f"Given this Json data: {json_data}/n, Use bullet points  and a TABLE to give an executive summary of this data based on this query: {query} \
        for example, if the query is : tell me the progress of batch data/n, your answer should be the summary \
        of this json file provided. summarize it as sentences. start the sentence by saying 'As of {formatted_time} EST here is the summary \
        of wealth management batch'. Also replace all actual figures by calculating the percentage that figure represents. DO NOT INCLUDE THE ACTUAL TOTAL NUMBER OF JOBS, TOTAL NUMBER OF MILESTONES, ONLY SHOW THE PERCENTAGE OF COMPLETED JOBS.\
        for example, you can say the Mainframe critical path is 40 % complete and it is currently tracked AMBER (status) and is expected to be completed by XXX(ETA). in your summary for each critical path, mention if there are delayed milestones in the critical path, you DONT NEED TO LIST THE MILESTONE JOB NAME, DESCRIPTION, AND FUNCTIONAL IMPACT IN THE SUMMARY, ONLY TALK ABOUT IT IN THE TABLE. if there is a delayed milestone job in each critical path, you should create a TABLE and list the delayed job names in a TABLE. The table should\
        consist of 3 columns which is the Milestone Job name, description (which is the milestone_description in the json), and Functional Impact (which is the business functions impacted)." 
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content": prompt}]
    payload= {
      "model":"gpt-3.5-turbo-0613",
      "messages": messages,
      "max_tokens" : 1024,
      "temperature" : 0
    }

    try:
        result = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
    except Exception as e:
        return {'status': -1, 'error': 'Error occured' + str(e)}
    
    return {'status':0, 'result': result.text}


def get_business_function(job_name):

    # #make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/business-functions?date={previous_date}&job={job_name}"
    # data = requests.get(url)

    #Assume this process is connecting to API and getting json data
    with open(r'OpenAI_POC\businessfunctionsAPI.json') as file:
        data = json.load(file)

    #call the function that summarizes the data
    result = get_summary_business_functions(data, job_name)
    return result


def get_summary_business_functions(json_data, job_name):
    prompt = f"given this json data: {json_data}, write a summary of this json data in sentences. you can start your sentence by saying\
          'The business functions that are impacted because {job_name} is delayed are'. when you are done reading\
          the business functions, continue your sentence with 'and application impacted are'\
            then summarize the applicationsImpacted data list in the json.\
            your summary should be concise and formal."
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content": prompt}]

    payload = {"model" : "gpt-3.5-turbo-0613",
               "messages" : messages,
               "temperature" : 0.0,
               "top_p" : 1.0,
               "frequency_penalty": 0.0,
               "presence_penalty" : 0.0,
               "max_tokens" : 1000
    }
    data = json.dumps(payload).encode('utf-8')
    try:
        result = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
    except Exception as e:
        return {'status': -1, 'error': 'Error occured' + str(e)}
    
    return {'status':0, 'result': result.text}
    # result = requests.post(url, headers=headers, data=data)
    # return result.text


def get_failed_jobs(job_name):

    # #Make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/failure-analysis?date={previous_date}&job={job_name}"
    # data = requests.get(url)

    #Assume this process is connecting to API and getting json data
    with open(r'OpenAI_POC\failedjobs.json') as file:
        data = json.load(file)

    result = get_critical_job_failure(data, job_name)
    return result

    
def get_critical_job_failure(json_data, job_name):
    prompt = f"write an executive summary using This json data:{json_data}. do not make statements like 'According to the JSON DATA' in your sentence, it should not be known in your summary that you used a JSON data to get the summary. the json data contains the information of a failed job that caused this milestone job {job_name} to be delayed.\
        the failed job from the json data is a critical job and predecessor to this milestone job {job_name}. so if the predecessor job failed, then the milestone job will be delayed. make sure to Mention The name of the failed job. You can get the name of the failed job from the json data.\
        Note: the name of the job that failed in the json data is a critical job and a  predecessor to this milestone job {job_name}' make a reference to that in your sentence.\
        your response should be concise and formal."
    
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content": prompt}]

    payload = {"model" : "gpt-3.5-turbo-0613",
               "messages" : messages,
               "temperature" : 0.0,
               "top_p" : 1.0,
               "frequency_penalty": 0.0,
               "presence_penalty" : 0.0,
               "max_tokens" : 1000
    }
    data = json.dumps(payload).encode('utf-8')
    try:
        result = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
    except Exception as e:
        return {'status': -1, 'error': 'Error occured' + str(e)}
    
    return {'status':0, 'result': result.text}


def get_reason(job_name):

    #Make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/impact-analysis?date={previous_date}&job={job_name}"
    # data = requests.get(url)

    #Assume this process is connecting to API and getting json data

    with open(r'OpenAI_POC\reason_failed_job.json') as file:
        data = json.load(file)

    result = get_reason_summary(data, job_name)
    return result



def get_reason_summary(json_data, job_name):

    prompt = f"Using this json data: {json_data}/n tell me the reason why this job: {job_name}failed. your sentence should be concise and formal."
    
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content": prompt}]

    payload = {"model" : "gpt-3.5-turbo-0613",
               "messages" : messages,
               "temperature" : 0.0,
               "top_p" : 1.0,
               "frequency_penalty": 0.0,
               "presence_penalty" : 0.0,
               "max_tokens" : 1000
    }
    data = json.dumps(payload).encode('utf-8')
    try:
        result = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
    except Exception as e:
        return {'status': -1, 'error': 'Error occured' + str(e)}
    
    return {'status':0, 'result': result.text}


def get_delayed_milestones(query):

    #make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/delayed-milestones?date={previous_date}"
    # data = requests.get(url)

    with open(r'OpenAI_POC\delayedmilestones.json') as file:
        data = json.load(file)

    result = get_delayed_milestones_summary(data, query)
    return result

    
def get_delayed_milestones_summary(json_data, query):
    prompt = f"Give a summary of this json data {json_data}\n\
        your answer should be a sentence, and it should be concise and formal. you can use this query: {query} as a reference for your sentence."
    
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    messages = [{"role": "user", "content": prompt}]

    payload = {"model" : "gpt-3.5-turbo-0613",
               "messages" : messages,
               "temperature" : 0.0,
               "top_p" : 1.0,
               "frequency_penalty": 0.0,
               "presence_penalty" : 0.0,
               "max_tokens" : 1000
    }
    data = json.dumps(payload).encode('utf-8')
    try:
        result = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(payload))
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
resp = result['choices'][0]['message']['content']
print(resp)

    

