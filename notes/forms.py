from django import forms
from .models import Notes, Tag, Category, Profile
from django.contrib.auth.models import User


class NotesForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Tags'
    )
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Share with'
    )

    class Meta:
        model = Notes
        fields = ['title', 'text', 'category', 'shared_with', 'tags', 'is_public']
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
            'shared_with': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2',
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-slate-300 text-teal-700 focus:ring-teal-500',
            }),
        }
        labels = {
            'title': 'Title',
            'text': 'Body',
            'category': 'Category',
            'shared_with': 'Share with',
            'tags': 'Tags',
            'is_public': 'Make note public'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=user.pk)
        self.fields['shared_with'].initial = []

        self.fields['tags'].queryset = Tag.objects.order_by('name')

        self.fields['category'].queryset = Category.objects.order_by('name')
        default_category = Category.objects.filter(name='Personal').first()
        if default_category:
            self.fields['category'].initial = default_category
        
        # Add help text for shared_with
        self.fields['shared_with'].help_text = 'Hold Ctrl (Cmd on Mac) to select multiple users'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'topics', 'focus_areas']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-200',
                'rows': 4,
                'placeholder': 'Short bio...'
            }),
            'topics': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-200',
                'rows': 3,
                'placeholder': 'Topics you care about...'
            }),
            'focus_areas': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-teal-500 focus:ring-2 focus:ring-teal-200',
                'rows': 3,
                'placeholder': 'Current focus areas...'
            }),
        }
        labels = {
            'bio': 'Bio',
            'topics': 'Topics',
            'focus_areas': 'Focus areas',
        }
