import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Max, Min
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from zone.models import Zone
from .models import Mesure, Rapport

CHAMPS = ['temperature', 'humidite', 'oxygene', 'co2']


@login_required
def zone_analyse(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    mesures = zone.mesures.all()

    stats = {}
    if mesures.exists():
        agg = mesures.aggregate(
            **{f'{c}_avg': Avg(c) for c in CHAMPS},
            **{f'{c}_min': Min(c) for c in CHAMPS},
            **{f'{c}_max': Max(c) for c in CHAMPS},
        )
        stats = {c: {'avg': agg[f'{c}_avg'], 'min': agg[f'{c}_min'], 'max': agg[f'{c}_max']} for c in CHAMPS}

    derniere = mesures.first()
    return render(request, 'analyse/zone_analyse.html', {
        'title': 'Analyse',
        'zone': zone,
        'derniere': derniere,
        'alertes': derniere.alertes() if derniere else [],
        'stats': stats,
        'nb_mesures': mesures.count(),
        'mesures': mesures[:15],
        'rapports': zone.rapports.all(),
    })


@login_required
@require_POST
def lancer_analyse(request, pk):
    """Simulation du robot : génère une mesure aléatoire."""
    zone = get_object_or_404(Zone, pk=pk)
    Mesure.objects.create(
        zone=zone,
        temperature=round(random.uniform(15, 48), 1),
        humidite=round(random.uniform(5, 80), 1),
        oxygene=round(random.uniform(15, 21), 1),
        co2=round(random.uniform(350, 1600)),
    )
    messages.success(request, "Le robot a remonté une nouvelle mesure.")
    return redirect('zone-analyse', pk=zone.pk)


class RapportCreateView(LoginRequiredMixin, CreateView):
    model = Rapport
    fields = ['titre', 'contenu', 'niveau_risque']

    def dispatch(self, request, *args, **kwargs):
        self.zone = get_object_or_404(Zone, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Pré-remplit le rapport à partir de la dernière mesure."""
        derniere = self.zone.mesures.first()
        if not derniere:
            return {'titre': f"Rapport - {self.zone.name_zone}"}
        alertes = derniere.alertes()
        lignes = [
            f"Mesure du {derniere.date:%d/%m/%Y %H:%M}",
            f"Température : {derniere.temperature} °C",
            f"Humidité : {derniere.humidite} %",
            f"Oxygène : {derniere.oxygene} %",
            f"CO2 : {derniere.co2} ppm",
            "",
            "Problèmes détectés : " + (", ".join(alertes) if alertes else "aucun"),
        ]
        return {
            'titre': f"Rapport - {self.zone.name_zone} - {derniere.date:%d/%m/%Y}",
            'contenu': "\n".join(lignes),
            'niveau_risque': derniere.niveau_risque(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone'] = self.zone
        return context

    def form_valid(self, form):
        form.instance.zone = self.zone
        form.instance.auteur = self.request.user
        messages.success(self.request, "Rapport créé.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('zone-analyse', kwargs={'pk': self.zone.pk})


class RapportDetailView(LoginRequiredMixin, DetailView):
    model = Rapport


class RapportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Rapport
    fields = ['titre', 'contenu', 'niveau_risque']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone'] = self.object.zone
        return context

    def test_func(self):
        return self.request.user == self.get_object().auteur


class RapportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Rapport

    def test_func(self):
        return self.request.user == self.get_object().auteur

    def get_success_url(self):
        return reverse('zone-analyse', kwargs={'pk': self.object.zone.pk})
