from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Zone


def home(request):
    context = {
        'zones': Zone.objects.all()
    }
    return render(request, 'zone/home.html', context)


class ZoneListView(LoginRequiredMixin, ListView):
    model = Zone
    template_name = 'zone/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'zones'
    ordering = ['-date_creation']

    def get_queryset(self):
        # only the logged-in user's zones
        return Zone.objects.filter(user=self.request.user).order_by('-date_creation')


class ZoneDetailView(DetailView):
    model = Zone


class ZoneCreateView(LoginRequiredMixin, CreateView):
    model = Zone
    fields = [
        'name_zone', 
        'description',
        'localisation', 
        'size_zone',
        'statut',
        'type_area'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ZoneUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Zone
    fields = [
        'name_zone', 
        'description',
        'localisation', 
        'size_zone',
        'statut',
        'type_area'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        zone = self.get_object()
        if self.request.user == zone.user:
            return True
        return False


class ZoneDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Zone
    success_url = '/'

    def test_func(self):
        zone = self.get_object()
        if self.request.user == zone.user:
            return True
        return False


def about(request):
    return render(request, 'zone/about.html', {'title': 'About'})

