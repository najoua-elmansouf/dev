from django.db import models

# Create your models here.

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
class FileQuestion(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    question_text = models.TextField()
    asked_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    asked_at = models.DateTimeField(auto_now_add=True)