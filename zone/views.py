from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
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
        # seulement les éléments de l'utilisateur connecté
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


@login_required
def zone_analyse(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    return render(request, 'zone/zone_analyse.html', {'zone': zone, 'title': 'Analyse'})


@login_required
def zone_traitement(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    return render(request, 'zone/zone_traitement.html', {'zone': zone, 'title': 'Traitement'})
