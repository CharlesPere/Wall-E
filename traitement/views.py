from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from zone.models import Zone
from .forms import InterventionForm
from .models import Intervention

# Problème détecté -> robot conseillé, temps de base (h), ressources conseillées
CONSEILS = {
    "Risque incendie": ('pompier', 4, "Eau / retardant, extincteurs"),
    "Sécheresse": ('irrigation', 6, "Réserve d'eau, tuyaux d'irrigation"),
    "Manque d'oxygène": ('oxygenation', 3, "Bouteilles d'oxygène, ventilateurs"),
    "Pollution atmosphérique": ('filtration', 5, "Filtres à CO2, capteurs"),
}


def suggestion(alertes):
    """Pré-remplit le formulaire selon les problèmes de la dernière mesure."""
    conseils = [CONSEILS[a] for a in alertes if a in CONSEILS]
    if not conseils:
        return {'type_robot': 'polyvalent', 'temps_estime': 2, 'nb_robots': 1}
    if len(conseils) == 1:
        robot, temps, ressources = conseils[0]
        return {'type_robot': robot, 'temps_estime': temps, 'ressources': ressources, 'nb_robots': 1, 'nb_ouvriers': 2}
    return {
        'type_robot': 'polyvalent',
        'temps_estime': sum(c[1] for c in conseils),
        'ressources': "\n".join(c[2] for c in conseils),
        'nb_robots': len(conseils),
        'nb_ouvriers': 2 * len(conseils),
    }


@login_required
def zone_traitement(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    derniere = zone.mesures.first() if hasattr(zone, 'mesures') else None
    alertes = derniere.alertes() if derniere else []

    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.zone = zone
            intervention.auteur = request.user
            intervention.save()
            messages.success(request, "Intervention planifiée.")
            return redirect('zone-traitement', pk=zone.pk)
    else:
        form = InterventionForm(initial=suggestion(alertes))

    return render(request, 'traitement/zone_traitement.html', {
        'title': 'Traitement',
        'zone': zone,
        'derniere': derniere,
        'alertes': alertes,
        'form': form,
        'interventions': zone.interventions.all(),
    })


@login_required
@require_POST
def intervention_avancer(request, pk):
    """Planifiée -> En cours -> Terminée."""
    intervention = get_object_or_404(Intervention, pk=pk)
    if intervention.statut == 'planifiee':
        intervention.statut = 'en_cours'
    elif intervention.statut == 'en_cours':
        intervention.statut = 'terminee'
        intervention.date_fin = timezone.now()
    intervention.save()
    return redirect('zone-traitement', pk=intervention.zone.pk)


@login_required
@require_POST
def intervention_supprimer(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)
    zone_pk = intervention.zone.pk
    if request.user == intervention.auteur:
        intervention.delete()
        messages.success(request, "Intervention supprimée.")
    return redirect('zone-traitement', pk=zone_pk)
