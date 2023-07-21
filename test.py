import openai,requests,json,os,pytz
from datetime import datetime, timedelta
from functionclassifier import FunctionClassifier
from query_embeddings import QueryEmbeddedData
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI


OPENAI_API_KEY = "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"
date = datetime.now().date()
previous_date = date - timedelta(days=1)
memory_buffer = ConversationBufferMemory(memory_key="chat_history", return_messages=True)



def get_batch_progress(query):
    #make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/batch-summary?date={previous_date}"
    # data = requests.get(url)

    #Assume this process is connecting to API and getting json data
    with open('summaryAPI.json') as file:
        data = json.load(file)

    result = json.loads(get_summary_batch_progress(data, query).get("result", 'error'))
    resp = result['choices'][0]['message']['content']    
    memory_buffer.save_context({'Human Input':query}, {'AI Response':resp})
    
    return resp

def get_summary_batch_progress(json_data, query):
    print(f'--{datetime.now()}--get_summary_batch_progress')
    # Get the current time
    current_time = datetime.now()

    # Convert the current time to a specific timezone
    timezone = pytz.timezone('US/Eastern')  # Example: US Eastern Time (EST)
    current_time = current_time.astimezone(timezone)

    # Format the time as hour:minutes AM/PM
    time_format = "%I:%M%p"  # 12-hour format with leading zero, e.g., 07:30AM
    formatted_time = current_time.strftime(time_format)
    conversation_histoy = memory_buffer.load_memory_variables({})

    prompt = f"Current Conversation History: {conversation_histoy}\n Given this Json data: {json_data}/n, Use bullet points  and a TABLE to give an executive summary of this data based on this query: {query} \
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

def get_delayed_milestone_reason(job_name):

    # #Make an API call
    # url = f"https://tereoservices.webfarm-dev.ms.com:12660/tereoservices/failure-analysis?date={previous_date}&job={job_name}"
    # data = requests.get(url)

    #Assume this process is connecting to API and getting json data
    with open('failedjobs.json') as file:
        data = json.load(file)

    result = json.loads(get_critical_job_failure(data, job_name).get("result", 'error'))
    resp = result['choices'][0]['message']['content']    
    memory_buffer.save_context({'Human Input':job_name}, {'AI Response':resp})
    
    return resp

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


def main_function_call(query):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {'content-type':'application/json', "Authorization": "Bearer" + " " + OPENAI_API_KEY}
    
    with open('functions.json') as file:
            data = json.load(file)
            
    function = data
    conversation_histoy = memory_buffer.load_memory_variables({})

    prompt = f"You are an AI bot. I am providing you a function description,\
    use that and the user inputted query to return me function_call information.\
    It is also possible that user is asking some follow up question for some AI response you gave last time \
    and some argument for this new function might need to be predicted from \
    last user conversation. Only user history if you think its a follow up,Here is conversation history for your reference: \
    Conversation History: {conversation_histoy}\
    Give your result in the following JSON sequence. ['choices'][0]['message']['function_call']['name'] \
    ['choices'][0]['message']['function_call']['arguments'].\
    Do not send anything in content, always return the function_call key and stop reason should be a function_call.\
    User Query is: {query}"
    
    messages = [{"role": "user", "content":prompt}]
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

def main():
    while True:
        query_str = input("\nWhat would you like to know about the TEREO Batch Jobs: ")
        if(query_str=="q" or query_str=="quit"):
            break
        
        #function calls
        function_call_output = main_function_call(query_str)
        print(function_call_output)

        print('\033[94m')
        print('\n',function_call_output)
        print('\033[0m')
        
        function_name = eval(function_call_output['choices'][0]['message']['function_call']['name'])
        function_argument = json.loads(function_call_output['choices'][0]['message']['function_call']['arguments'])

        print(f"--{datetime.now()}--main::calling the selected function")        
        result = (function_name(**function_argument))
        
        print("\n",result)
    
main()