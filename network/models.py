from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils.timezone import make_aware
import uuid


def now():
    return make_aware(datetime.datetime.now())


# Models
class User(AbstractUser):
    pass


class Follow(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey('User', on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.user} FOLLOWING {self.followed}"


class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name="+")
    content = models.TextField(max_length=280, verbose_name='')
    datetime = models.DateTimeField(auto_now_add=True)


    def likable(self, user_obj):                                        # Not Needed anymore
        return not bool(Like.objects.filter(user=user_obj, post=self))

    def likes(self):
        return self.like_objs.count()

    def users_liked(self):
        users = [like_obj.user for like_obj in self.like_objs.all()]
        return users

    def __str__(self):
            return f"POST: [{self.content[:25]}...] BY [{self.author}]"


class Like(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="liked_by")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="like_objs")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_like')
        ]

    def likable(user_obj, self):
        return self.object.get(user=user_obj).count()

    def __str__(self):
        return f"{self.user.username} likes POST: [{self.post.content[:10]}] BY [{self.post.author}]"
