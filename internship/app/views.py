from django.shortcuts import render
import openai
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import tiktoken
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog
from django.contrib.auth.decorators import login_required

ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")
MAX_TOKEN = 14000

# Create your views here.
@login_required(login_url='login')
def myview(request):
    return render(request, "app/graph.html")

def chunk_dataframe(df, max_token_limit):
    current_chunk = pd.DataFrame()
    current_token_count = 0
    chunks = []

    for index, row in df.iterrows():
        # Convert the row to string
        row_string = row.to_string(index=False)
        # Get the token count for the current row
        row_token_count = num_tokens_from_string(row_string)

        # Check if adding the current row would exceed the token limit for the chunk
        if current_token_count + row_token_count > max_token_limit:
            # Add the current chunk to the list of chunks
            chunks.append(current_chunk)
            # Reset variables for the next chunk
            current_chunk = pd.DataFrame()
            current_token_count = 0

        # Add the current row to the current chunk
        current_chunk = current_chunk._append(row, ignore_index=True)  # Append the row as a DataFrame
        current_token_count += row_token_count

    # Add the last chunk to the list of chunks
    if not current_chunk.empty:
        chunks.append(current_chunk)

    return chunks


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def gpt_processing(model,key,sample_dataset): 
    """process data of files by gpt"""
    # key for each user
    # Configuration of the API key
    openai.api_key = key
    #gpt's context
    # Define the conversation template as a regular Python string
    conversation_template = '''{
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
            "label": [PLACEHOLDER_COLUMN_NAME],
            "values": {
                 "labels":[PLACEHOLDER_COLUMN_VALUES],
                 "percentage" :[PLACEHOLDER_LABELS_PERCENTAGE]
            },
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
    {"role": "system", "content": "You are an AI assistant that generates json data to utilize to plot charts, you need to analyse the dataset's columns to see wich plots are the most convenient based on the table ."},
    {"role": "user", "content": f"Given the following dataset:\n{sample_dataset}\nPlease generate json data for the following charts:"},
    {"role": "user", "content": "1. A bar chart with the 'xAxis' representing categories and replace the placeholder of its label with the name of the column used ,'yAxis' representing values and replace the placeholder of its label with the name of the column used."},
    {"role": "assistant", "content": "2. A pie chart with 'labels' representing categories and replace the placeholder of the label with the name of the column used ,and 'percentage' representing the corresponding percentages of labels."},
    {"role": "user", "content": "3. A line chart with 'xAxis' representing continuous data or time periods and replace the placeholder of its label with the name of the column used ,and 'yAxis' representing either continuous or discrete data and replace the placeholder of its label with the name of the column used."},
    {"role": "assistant", "content": "4. A scatter plot with 'xAxis' representing one variable and replace the placeholder of its label with the name of the column used ,do the same for the yAxis"},
    {"role": "user", "content": f"Generate JSON response charts in this format using this template \n{conversation_template}\n and replacing the placeholders with the corresponding values from the dataset please "},

    
    
]

    response = openai.ChatCompletion.create(
    model=model,
    messages=conversation,
    max_tokens=4096,
    n=1,
    stop=None,
    temperature = 0.5
    )
    return response 

def process_uploaded_datasets(file):
    processed_outputs = []
    try:
        # Assuming you are using an Excel file, specify the engine as 'openpyxl'
        df = pd.read_excel(file, engine='openpyxl')
        sample_dataset = df.to_string(index=False)  # Convert DataFrame to string directly
        tokens = num_tokens_from_string(sample_dataset)
        if tokens > 14000 :
            chunks = chunk_dataframe(df,MAX_TOKEN)
            root = tk.Tk()
            root.withdraw()
            # Prompt the user to select the output folder using a pop-up window
            output_folder = filedialog.askdirectory(title="Select the folder where you want to save the Excel files")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            for i, chunk in enumerate(chunks, start=1):
                file_name = filedialog.asksaveasfilename(
            initialdir=output_folder,
            initialfile=f"chunk_{i}.xlsx",
            title=f"Save Chunk {i} as Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
                if not file_name:
                    print(f"User canceled saving Chunk {i}.")
                    continue
                try:
                    with pd.ExcelWriter(file_name) as writer:
                        chunk.to_excel(writer, index=False, sheet_name='Sheet1')
                    print(f"Chunk {i} saved as Excel.")
                except Exception as e:
                    print(f"Error saving Chunk {i} as Excel: {e}")

            
        else :   
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



