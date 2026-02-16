from django.db import models
import re
import markdown
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Notes(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    shared_with = models.ManyToManyField(User, related_name='shared_notes', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)

    def __str__(self):
        return self.title

    @property
    def rendered_text(self):
        if not self.text:
            return ""
        if re.search(r"</?[a-z][\s\S]*>", self.text):
            return self.text
        return markdown.markdown(self.text, extensions=["fenced_code", "tables", "sane_lists"])

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
