from django import forms
from .models import Notes, Tag, Comment
from django.contrib.auth.models import User


class NotesForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Tags'
    )
    access_level = forms.ChoiceField(
        choices=Notes.ACCESS_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'rounded-lg border-gray-300 text-sm text-gray-700 focus:border-indigo-500 focus:ring-indigo-500',
        }),
        label='Access Level'
    )

    class Meta:
        model = Notes
        fields = ['title', 'text', 'category', 'shared_with', 'tags', 'access_level']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500 placeholder-gray-400',
                'placeholder': 'Enter title here...',
            }),
            'text': forms.Textarea(attrs={
                'class': 'w-full rounded-lg text-sm min-h-[300px] focus:ring-0 placeholder-gray-400',
                'placeholder': 'Write your thoughts here...',
                'rows': '12',
            }),
            'category': forms.Select(attrs={
                'class': 'rounded-lg border-gray-300 text-sm text-gray-700 focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'shared_with': forms.SelectMultiple(attrs={
                'class': 'rounded-lg border-gray-300 text-sm text-gray-700 focus:border-indigo-500 focus:ring-indigo-500',
                'size': '3',
            }),
        }
        labels = {
            'title': 'Title',
            'text': 'Write your thoughts here:',
            'category': 'Category',
            'shared_with': 'Share with',
            'tags': 'Tags',
            'access_level': 'Access Level'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=user.pk)
            
        # Set initial category if needed
        self.fields['category'].initial = 'Personal'
        
        # Add help text for shared_with
        self.fields['shared_with'].help_text = 'Hold Ctrl (Cmd on Mac) to select multiple users'
        
        # Initialize access_level field
        self.fields['access_level'].initial = 'read-only'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'w-full rounded-lg text-sm min-h-[100px] focus:ring-0 placeholder-gray-400',
                'placeholder': 'Write your comment here...',
                'rows': '4',
            }),
        }
        labels = {
            'text': 'Comment',
        }
