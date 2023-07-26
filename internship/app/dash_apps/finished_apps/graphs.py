from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import base64
from dash.exceptions import PreventUpdate
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('graphs', external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Charts'),
    
    dcc.Upload(
        id='upload-data',  # This ID will be used in the callback to retrieve the uploaded file
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),

    html.Div(id='charts-container'),
    html.Div(id='dummy-input', children='dummy')
])

# Your Django view URL
url = 'http://localhost:8000/upload_datasets/'

def fetch_json_data(url, files):
    # Make the POST request with the files
    response = requests.post(url, files=files)

    if response.status_code == 200:
        try:
            # Parse the JSON data from the response
            processed_data = response.json()

            # If the processed_data is a list, assume the first element contains the relevant data
            if isinstance(processed_data, list):
                processed_data = processed_data[0]

            return processed_data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
            return None
    else:
        print(f"Error: Failed to upload and process data. Status code: {response.status_code}")
        return None



def generate_chart(chart_data):
    charts = chart_data.get('charts', [])
    chart_divs = []  # Store chart divs in a list
    print('salam')
    for chart in charts:
        chart_type = chart.get('chartType', None)
        if chart_type != 'pie':
            x_axis = chart['xAxis']
            y_axis = chart['yAxis']

        if chart_type == 'bar':
            plot = dcc.Graph(
                figure={
                    'data': [go.Bar(x=x_axis['categories'], y=y_axis['values'])],
                    'layout': go.Layout(title=f"{x_axis['label']} vs {y_axis['label']}")
                }
            )
        elif chart_type == 'line':
            plot = dcc.Graph(
                figure={
                    'data': [go.Scatter(x=x_axis['categories'], y=y_axis['values'], mode='lines')],
                    'layout': go.Layout(title=f"{x_axis['label']} vs {y_axis['label']}")
                }
            )
        elif chart_type == 'pie':
            plot = dcc.Graph(
                figure={
                    'data': [go.Pie(labels=chart['labels'], values=chart['values'])],
                    'layout': go.Layout(title=f"{x_axis['label']} Distribution")
                }
            )
        elif chart_type == 'scatter':
            plot = dcc.Graph(
                figure={
                    'data': [go.Scatter(x=x_axis['values'], y=y_axis['values'], mode='markers')],
                    'layout': go.Layout(title=f"{x_axis['label']} vs {y_axis['label']}")
                }
            )
        else:
            continue

        chart_divs.append(html.Div(plot))  # Append each chart div to the list
        print('salam2')
    return chart_divs

# ... (existing code)



@app.callback(
    Output('charts-container', 'children'),
    [Input('upload-data', 'contents'), Input('upload-data', 'filename')]  # Use the uploaded file contents and filename as inputs
)
def update_charts(contents, filenames):
    print("Callback triggered.")

    if contents is None:
        raise PreventUpdate

    for content, filename in zip(contents, filenames):
        # Assuming you have a single file upload, use index 0
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            # Save the file temporarily on the server-side
            temp_dir = '/path/to/temp/'  # Update this with the desired temporary directory
            os.makedirs(temp_dir, exist_ok=True)  # Create the temporary directory if it doesn't exist

            temp_filepath = os.path.join(temp_dir, filename)  # Full path to the temporary file
            with open(temp_filepath, 'wb') as f:
                f.write(decoded)

            # The file is directly received as a parameter in the callback function
            files = {'dataset_files': open(temp_filepath, 'rb')}
            
            # Fetch the processed JSON data from the Django view
            data = fetch_json_data(url, files)

            try:
                data_dict = json.loads(data)  # Convert the JSON string to a dictionary
            except json.JSONDecodeError:
                return html.Div("Error: Failed to parse JSON data")

            if data_dict:
                # Generate charts using the fetched JSON data
                return generate_chart(data_dict)
            else:
                return html.Div("Error: Failed to fetch JSON data")

        except Exception as e:
            print(f"Error during file processing: {e}")

    # If there's no uploaded file or an error occurred during processing
    return html.Div("Error: Please upload a file and try again.")

if __name__ == '__main__':
    print("Starting the server...")
    app.run_server(debug=True)
