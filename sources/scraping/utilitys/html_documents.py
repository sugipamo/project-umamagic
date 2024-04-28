from django.db import models

class HtmlDocuments(models.Model):
    title = models.CharField(max_length=255, default='')
    url = models.URLField()
    html = models.TextField()
    parsed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
