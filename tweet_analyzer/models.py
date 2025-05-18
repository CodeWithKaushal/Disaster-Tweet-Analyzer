from django.db import models


class Feedback(models.Model):
    """Model for storing user feedback"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name} on {self.created_at.strftime('%Y-%m-%d')}"
