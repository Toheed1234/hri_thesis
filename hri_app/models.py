from django.db import models

class Feedback(models.Model):
    user_name = models.CharField(max_length=100)
    animation_type = models.CharField(max_length=50)
    rating = models.IntegerField()  # Example: 1-5 scale

    def __str__(self):
        return f"{self.user_name} - {self.animation_type}"