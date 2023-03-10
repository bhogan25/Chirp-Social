from django.forms import ModelForm, Textarea
from .models import Post

class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': Textarea(attrs={'cols': 40, 'rows': 4}),
        }

