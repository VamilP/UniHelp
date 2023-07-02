from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, ContactSubmission, AppliedSubmission
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib import messages


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.profile.role == 'Student':
            submitted_posts = AppliedSubmission.objects.filter(author=self.request.user).values_list('post_id', flat=True)
            context['submitted_posts'] = submitted_posts
        return context

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 6

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        user = self.request.user

        # Check if the user has submitted the form for this post
        has_submitted_form = AppliedSubmission.objects.filter(post=post, author=user).exists()
        context['user'] = user
        context['has_submitted_form'] = has_submitted_form
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

def solutionFinder(request):
    return render(request, 'blog/solutionFinder.html', {'title': 'Home'})

def event(request):
    return render(request, 'blog/event.html', {'title': 'Event'})

def resource(request):
    return render(request, 'blog/resource.html', {'title': 'Resource'})

class ContactView(LoginRequiredMixin, CreateView):
    model = ContactSubmission
    fields = ['name', 'email', 'message']
    # template_name = 'contact_form.html'
    # success_url = '/contact/success/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class AppliedView(LoginRequiredMixin, CreateView):
    model = AppliedSubmission
    fields = ['name', 'email', 'phone', 'skills', 'address']
    success_url = reverse_lazy('form-success')  # Redirect to the success page
    template_name = 'blog/applied_form.html'  # Assuming you have a template for the form

    def form_valid(self, form):
        # Check if the user has already submitted the form for the post
        post = Post.objects.get(pk=self.kwargs['pk'])
        if AppliedSubmission.objects.filter(author=self.request.user, post=post).exists():
            messages.error(self.request, 'You have already submitted the form for this post.')
            return redirect(self.success_url)

        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)
    
class FormSuccessView(TemplateView):
    template_name = 'blog/form_success.html'