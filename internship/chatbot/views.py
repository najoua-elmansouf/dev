import os
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from .embedding import *
from .extracting_data import *

@csrf_protect
def chat_view(request):
    return render(request, 'chatbot/new_chat.html')


import os

# ...

def pdf_recieve(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        print("File name:", uploaded_file.name)
        print("File size:", uploaded_file.size)

        # Set the path to the "uploads" folder in the "dev" directory
        uploads_folder = os.path.join(settings.BASE_DIR, 'dev', 'uploads')

        # Create the "uploads" folder if it doesn't exist
        if not os.path.exists(uploads_folder):
            os.makedirs(uploads_folder)

        # Save the uploaded file in the "uploads" folder
        file_path = os.path.join(uploads_folder, uploaded_file.name)
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Process the uploaded PDF file
        df = process_pdf(file_path)
        print(df)

        # Compute document embeddings
        document_embeddings = compute_doc_embeddings(df, EMBEDDING_MODEL)

        # Your user's query (example: "What is GDPR?")
        user_query = "Your user's question goes here."

        # Get the chatbot's response based on the user's query and document content
        response, _ = answer_with_gpt_4(user_query, df, document_embeddings)

        # Remove the uploaded file (optional, if needed)
        # os.remove(file_path)

        # Return the chatbot's response as a JSON
        return JsonResponse({'response': response})

    else:
        print("pewpewpewww")
        # Handle the case when there is no file uploaded
        return JsonResponse({'error': 'No file uploaded'})