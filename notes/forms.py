from django import forms

from .models import Notes

class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'text', 'category', 'shared_with']
        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control my-5'}),
            'text' : forms.Textarea(attrs={'class':'form-control my-5'}),
            'category' : forms.Select(attrs={'class':'form-control my-5'}),
        }
        labels = {
            'text' : 'Write your thoughts here:',
        }

    # def clean_title(self):
    #     title = self.cleaned_data['title']
    #     if 'Perfect' not in title:
    #         raise forms.ValidationError('Title must contain Perfect')
    #     return title