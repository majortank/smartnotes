from django import forms
from .models import Notes, Tag, Category
from django.contrib.auth.models import User


class NotesForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Tags'
    )

    class Meta:
        model = Notes
        fields = ['title', 'text', 'category', 'shared_with', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500 placeholder-gray-400',
                'placeholder': 'Enter title here...',
            }),
            'text': forms.Textarea(attrs={
                'id': 'tiptap-input',
                'class': 'hidden',
                'rows': '8',
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
            'text': 'Body',
            'category': 'Category',
            'shared_with': 'Share with',
            'tags': 'Tags'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=user.pk)

        self.fields['category'].queryset = Category.objects.order_by('name')
        default_category = Category.objects.filter(name='Personal').first()
        if default_category:
            self.fields['category'].initial = default_category
        
        # Add help text for shared_with
        self.fields['shared_with'].help_text = 'Hold Ctrl (Cmd on Mac) to select multiple users'
