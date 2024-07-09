from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.CharField(max_length=140)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def __str__(self):
        return f"{self.user} is following {self.user_follower}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    def __str__(self):
        return f"{self.user} liked {self.post}"
