from django.contrib import admin
from .models import Post, ContactSubmission, AppliedSubmission

admin.site.register(Post)
admin.site.register(ContactSubmission)
admin.site.register(AppliedSubmission)