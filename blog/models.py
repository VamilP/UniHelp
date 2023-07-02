from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    unique_number = models.IntegerField(unique=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate a unique number for new posts
            # Generate a unique number
            max_number = Post.objects.all().aggregate(models.Max('unique_number'))['unique_number__max']
            self.unique_number = max_number + 1 if max_number else 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
        # return reverse('blog-home')

    def has_submitted_form(self):
        if self.author.is_authenticated:
            return AppliedSubmission.objects.filter(author=self.author, post=self).exists()
        return False

class ContactSubmission(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog-home')

class AppliedSubmission(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    skills = models.TextField()
    address = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog-home')
    
    def get_post_unique_number(self):
        return self.post.unique_number
