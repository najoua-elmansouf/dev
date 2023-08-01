from django.shortcuts import render
import openai
import pandas as pd
import json
from django.views.decorators.csrf import csrf_exempt
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
    # Define the conversation template as a regular Python string
    conversation_template = '''{
    "filters": {
        "name": [PLACEHOLDER_NAME],
        "age": [PLACEHOLDER_AGE],
        "salary": [PLACEHOLDER_SALARY]
    },
    "KPIs": {
        "Average Age": [PLACEHOLDER_AVERAGE_AGE],
        "Maximum Salary": [PLACEHOLDER_MAXIMUM_SALARY],
        "Minimum Salary": [PLACEHOLDER_MINIMUM_SALARY]
    },
    "charts": [
        {
            "chartType": "bar",
            "xAxis": {
                "label": [PLACEHOLDER_X_AXIS_LABEL],
                "categories": [PLACEHOLDER_X_AXIS_CATEGORIES]
            },
            "yAxis": {
                "label": [PLACEHOLDER_Y_AXIS_LABEL],
                "values": [PLACEHOLDER_Y_AXIS_VALUES]
            }
        },
        {
            "chartType": "line",
            "xAxis": {
                "label": [PLACEHOLDER_X_AXIS_LABEL],
                "categories": [PLACEHOLDER_X_AXIS_CATEGORIES]
            },
            "yAxis": {
                "label": [PLACEHOLDER_Y_AXIS_LABEL],
                "values": [PLACEHOLDER_Y_AXIS_VALUES]
            }
        },
        {
            "chartType": "pie",
            "labels": [PLACEHOLDER_X_AXIS_LABEL],
            "values": [PLACEHOLDER_Y_AXIS_VALUES]
        },
        {
            "chartType": "scatter",
            "xAxis": {
                "label": [PLACEHOLDER_X_AXIS_LABEL],
                "values": [PLACEHOLDER_X_AXIS_CATEGORIES]
            },
            "yAxis": {
                "label": [PLACEHOLDER_Y_AXIS_LABEL],
                "values": [PLACEHOLDER_Y_AXIS_VALUES]
            }
        }
    ]
}'''

# In your conversation, replace the placeholders with actual data when needed
    conversation = [
    {"role": "system", "content": "You are an AI assistant that generates data visualizations."},
    {"role": "user", "content": f"Given the following dataset:\n{sample_dataset}\nPlease generate the following charts:"},
    {"role": "assistant", "content": "1. A bar chart with the 'xAxis' representing categories and 'yAxis' representing values."},
    {"role": "user", "content": "2. A pie chart with 'labels' representing categories and 'values' representing the corresponding percentages."},
    {"role": "assistant", "content": "3. A line chart with 'xAxis' representing time periods and 'yAxis' representing values."},
    {"role": "user", "content": "4. A scatter plot with 'xAxis' representing one variable and 'yAxis' representing another variable."},
    {"role": "assistant", "content": "5. Calculate the average, maximum, and minimum for all variables."},
    {"role": "user", "content": "6. Provide filters for all variables to explore the data."},
    {"role": "assistant", "content": f"Generate JSON response with filters, KPIs, and charts in this format using this template \n{conversation_template}\n and replacing the placeholders with the corresponding values from the dataset please "}
    
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
    processed_outputs = []
    try:
        # Assuming you are using an Excel file, specify the engine as 'openpyxl'
        df = pd.read_excel(file, engine='openpyxl')
        sample_dataset = df.to_string(index=False)  # Convert DataFrame to string directly
        response = gpt_processing('gpt-3.5-turbo-16k', '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', sample_dataset)
        response_dict = response['choices'][0]['message']['content']
        processed_outputs.append(response_dict)
    except Exception as e:
        # Handle any errors that may occur during the process
        print(f"Error processing uploaded dataset: {str(e)}")
    return processed_outputs



@csrf_exempt
def upload_datasets(request):
    if request.method == 'POST':
        # Handle the uploaded datasets and process them using GPT-3.5 Turbo or other logic
        # Return the processed data as a JSON response
        processed_data = []
        for uploaded_file in request.FILES.getlist('dataset_files'):  # Update the key name here
            processed_data.extend(process_uploaded_datasets(uploaded_file))
        return JsonResponse(processed_data, safe=False)
    else:
        # Return a 400 Bad Request response if the request method is not POST
        return JsonResponse({"error": "Invalid request method"}, status=400)



