from django.shortcuts import render
import openai
import pandas as pd
import json
from django.http import JsonResponse

# Create your views here.
def myview(request):
    return render(request, "app/graph.html")


def gpt_processing(model,key,sample_dataset): 
    """process data of files by gpt"""
    # key for each user
    # Configuration of the API key
    openai.api_key = key
    #gpt's context
    conversation = [
    {"role": "system", "content": "You are an AI assistant that generates data visualizations."},
    {"role": "user", "content": f"Given the following dataset:\n{sample_dataset}\nPlease generate the following charts:"},
    {"role": "assistant", "content": "1. A bar chart with the 'x' axis representing categories and the 'y' axis representing values."},
    {"role": "user", "content": "2. A pie chart with 'labels' representing categories and 'values' representing the corresponding percentages."},
    {"role": "assistant", "content": "3. A line chart with 'x' axis representing time periods and 'y' axis representing values."},
    {"role": "user", "content": "4. A scatter plot with 'x' representing one variable and 'y' representing another variable."},
    {"role": "assistant", "content": "5. Calculate the average, maximum, and minimum for all variables."},
    {"role": "user", "content": "6. Provide filters for all variables to explore the data."},
    # Add more instructions for other types of charts you want to include...
    {"role": "assistant", "content": "Generate JSON response with filters, KPIs, and charts in this format"}
    ]
    response = openai.ChatCompletion.create(
    model=model,
    messages=conversation,
    max_tokens=4096,
    n=1,
    stop=None
    )
    return response 


def process_uploaded_datasets(file):
    """Process the uploaded file by gpt and save the output in json format."""
    processed_outputs = []
    df = pd.read_excel(file)
    sample_dataset = df.to_csv(index=False)
    response = gpt_processing('gpt-3.5-turbo-16k', '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', sample_dataset)
    response_dict = json.loads(response['choices'][0]['message']['content'])
    processed_outputs.append(response_dict)  
    return processed_outputs



def upload_datasets(request):
    if request.method == 'POST':
        # Handle the uploaded datasets and process them using GPT-3.5 Turbo or other logic
        # Return the processed data as a JSON response
        processed_data = []
        for uploaded_file in request.FILES.getlist('dataset_files'):  # Update the key name here
            processed_data.extend(process_uploaded_datasets(uploaded_file))
        print(json.dumps(processed_data, indent=4))
        return JsonResponse(processed_data, safe=False)
    else:
        # Return a 400 Bad Request response if the request method is not POST
        return JsonResponse({"error": "Invalid request method"}, status=400)
