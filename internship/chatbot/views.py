from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .forms import FileUploadForm, FileQuestionForm
from .embedding import *
from .extracting_data import *
from .models import UploadedFile, FileQuestion
from django.contrib.auth.models import User  # Import the User model
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
# Function to get or compute document embeddings and data frame
def get_or_compute_data(file_path):
    document_embeddings = cache.get('document_embeddings')
    df = cache.get('data_frame')

    if document_embeddings is None or df is None:
        # Process the uploaded PDF file and update the data frame
        df = process_pdf(file_path)
        print(df)

        # Compute document embeddings
        document_embeddings = compute_doc_embeddings(df, EMBEDDING_MODEL)

        # Store the computed data in the cache for future use
        cache.set('document_embeddings', document_embeddings)
        cache.set('data_frame', df)

    return document_embeddings, df
# Global variable to store the document embeddings and data frame
document_embeddings = None
df = None
@login_required(login_url='app1:login')
def chat_view(request):
    global document_embeddings, df

    upload_form = FileUploadForm()
    question_form = FileQuestionForm()

    # Initialize the uploaded_file_obj variable with None
    uploaded_file_obj = None
    file_path = None
    # Check if a user with ID 1 exists
    try:
        default_user = User.objects.get(id=1)
    except User.DoesNotExist:
        # If a user with ID 1 does not exist, you can create one manually or skip this block
        print("User with ID 1 does not exist.")
        # You can create a user with ID 1 using the following code:
        # default_user = User.objects.create_user(id=1, username='default_user', password='password1')
        # Replace 'default_user' and 'password1' with your desired username and password

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        # If a file has been uploaded, process the file and compute document embeddings
        if uploaded_file:
            print("File name:", uploaded_file.name)
            print("File size:", uploaded_file.size)

            # Set the path to the "uploads" folder in the "media" directory
            uploads_folder = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)

            # Create the "uploads" folder if it doesn't exist

            # Save the uploaded file in the "uploads" folder
            file_path = os.path.join(uploads_folder, uploaded_file.name)
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Save the uploaded file's metadata in the database
            uploaded_file_obj = UploadedFile.objects.create(file=file_path, uploaded_by=default_user)

            # Process the uploaded PDF file and update the data frame
            df = process_pdf(file_path)
            print(df)

            # Compute document embeddings
            document_embeddings = compute_doc_embeddings(df, EMBEDDING_MODEL)

            # Render the template with the uploaded file and the forms
            return render(request, 'chatbot/new_chat.html', {'file': uploaded_file_obj, 'upload_form': upload_form, 'question_form': question_form})
        # ... (rest of the code)
        else:
             question_form = FileQuestionForm(request.POST)
             if question_form.is_valid():
            # Get the user's query from the form
                    query = question_form.cleaned_data.get('question_text')

                    print("Received query:", query)

            # Check if document_embeddings and data frame are available
                    if document_embeddings is not None:
                    # Get the chatbot's response based on the user's query only
                          response, _ = answer_with_gpt_4(query, df, document_embeddings)
                          response_data = {
                        'response': response,
                          }
                          print(response)  # Make sure the chatbot's response is printed here
                    else:
                          response_data = {
                        'response': "Please upload a file first to enable document embeddings.",
                          }

                # Save the question in the database with the uploaded file object and asked_by=default_user
                    if uploaded_file_obj is not None:
                         FileQuestion.objects.create(file_id=uploaded_file_obj.id, question_text=query, asked_by=default_user)

                # Return the chatbot's response as a JSON
                    return JsonResponse(response_data)

    # Render the template with the forms
    return render(request, 'chatbot/new_chat.html', {'upload_form': upload_form, 'question_form': question_form})