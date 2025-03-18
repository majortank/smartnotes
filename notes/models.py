from django.db import models
from django.contrib.auth.models import User
from django_quill.fields import QuillField

CATEGORY_CHOICES = [
    ('Personal', 'Personal'),
    ('Work', 'Work'),
    ('School/Education', 'School/Education'),
    ('Shopping', 'Shopping'),
    ('Travel', 'Travel'),
    ('Recipes', 'Recipes'),
    ('Health/Fitness', 'Health/Fitness'),
    ('Finance', 'Finance'),
    ('Projects', 'Projects'),
    ('Ideas', 'Ideas'),
]

class Category(models.Model):
    name = models.CharField(max_length=20)

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
    ACCESS_LEVEL_CHOICES = [
        ('read-only', 'Read-Only'),
        ('edit', 'Edit'),
    ]

    title = models.CharField(max_length=255)
    text =  QuillField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    shared_with = models.ManyToManyField(User, related_name='shared_notes', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default='Personal', related_name='notes')
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVEL_CHOICES, default='read-only')

    def __str__(self):
        return f"{self.title} ({self.access_level})"

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

class Comment(models.Model):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.note.title}"
