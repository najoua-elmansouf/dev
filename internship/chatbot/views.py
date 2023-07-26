import os
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from .embedding import *
from .extracting_data import *

@csrf_protect
def chat_view(request):
    try:
        if request.method == 'POST':
            # Get the uploaded file from the request
            uploaded_file = request.FILES.get('file')

            if uploaded_file is not None:
                # Save the uploaded file to the "uploads" directory
                file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Extract data from the uploaded PDF file
                grouped_documents = process_pdf(file_path)

                # Compute document embeddings
                document_embeddings = compute_doc_embeddings(grouped_documents)

                # Get user input from the frontend
                user_query = request.POST.get('user_query')

                # Interact with ChatGPT and get the response
                response, _ = answer_with_gpt_4(user_query, grouped_documents, document_embeddings)
                
                print("Server Response:", response)
                
                # Prepare the response to be displayed in the chat window
                chat_messages = [
                    {'role': 'system', 'content': 'You are now chatting with the ChatGPT bot.'},
                    {'role': 'user', 'content': user_query},
                    {'role': 'bot', 'content': response},
                ]

                # Pass the chat messages and other data to the template for rendering
                context = {
                    'chat_messages': chat_messages,
                    'file_path': file_path,
                }

                # Render the chatbot page with the chat messages and other data
                return render(request, 'chatbot/new_chat.html', context)

        # If the request is not a POST or no file was uploaded, render the chatbot page
        return render(request, 'chatbot/new_chat.html')

    except Exception as e:
        # Return a JSON response with the error message
        return JsonResponse({'error': str(e)}, status=500)
