from django import forms

# File Upload Form
class FileUploadForm(forms.Form):
    file = forms.FileField()

# Question-Asking Form
class FileQuestionForm(forms.Form):
    question_text = forms.CharField(max_length=255)
class FileQuestionForm(forms.Form):
    question_text = forms.CharField(widget=forms.Textarea)