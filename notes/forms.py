from django import forms

from .models import Notes
from django.contrib.auth.models import User

class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'text', 'category', 'shared_with']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'mt-1 w-full border-none p-0 focus:border-transparent focus:outline-none focus:ring-0 sm:text-sm'}),
            'text' : forms.Textarea(attrs={'class':'w-full resize-none border-none align-top focus:ring-0 sm:text-sm'}),
            'category' : forms.Select(attrs={'class':'mt-1.5 w-full rounded-lg border-gray-300 text-gray-700 sm:text-sm'}),
            'shared_with' : forms.SelectMultiple(attrs={'class': 'mt-1.5 w-full rounded-lg border-gray-300 text-gray-700 sm:text-sm'}),
        }
        labels = {
            'text' : 'Write your thoughts here:',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(NotesForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=user.pk)

    

    # def clean_title(self):
    #     title = self.cleaned_data['title']
    #     if 'Perfect' not in title:
    #         raise forms.ValidationError('Title must contain Perfect')
    #     return title


    