from django import forms
from django.forms import ModelForm, Textarea
from .models import Post

class NewPostForm(ModelForm):
    
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': Textarea(attrs={'class': 'newpost form-control', 'cols': 40, 'rows': 4}),
        }

