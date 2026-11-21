from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from zone.models import Zone
from .forms import InterventionForm
from .models import Intervention

# Detected problem -> suggested robot, base time (h), suggested resources
ADVICE = {
    "Fire risk": ('firefighter', 4, "Water / retardant, extinguishers"),
    "Drought": ('irrigation', 6, "Water reserve, irrigation hoses"),
    "Low oxygen": ('oxygenation', 3, "Oxygen tanks, fans"),
    "Air pollution": ('filtration', 5, "CO2 filters, sensors"),
    "Poor harvest": ('farming', 8, "Seeds, harvesting tools"),
    "Needs fertilizer": ('farming', 3, "Natural fertilizer / compost"),
    "Poor catch": ('aquaculture', 6, "Nets, sonar sensors"),
    "Needs restocking": ('aquaculture', 5, "Fry, transport tanks"),
}


def suggestion(alerts):
    """Pre-fills the form based on the latest measurement's problems."""
    advice = [ADVICE[a] for a in alerts if a in ADVICE]
    if not advice:
        return {'robot_type': 'multipurpose', 'estimated_hours': 2, 'robot_count': 1}
    if len(advice) == 1:
        robot, hours, resources = advice[0]
        return {'robot_type': robot, 'estimated_hours': hours, 'resources': resources, 'robot_count': 1, 'worker_count': 2}
    return {
        'robot_type': 'multipurpose',
        'estimated_hours': sum(a[1] for a in advice),
        'resources': "\n".join(a[2] for a in advice),
        'robot_count': len(advice),
        'worker_count': 2 * len(advice),
    }


@login_required
def zone_treatment(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    latest = zone.measurements.first() if hasattr(zone, 'measurements') else None
    alerts = latest.alerts() if latest else []
    farm_alerts = latest.farm_alerts() if latest else []

    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.zone = zone
            intervention.author = request.user
            intervention.save()
            messages.success(request, "Intervention planned.")
            return redirect('zone-treatment', pk=zone.pk)
    else:
        form = InterventionForm(initial=suggestion(alerts + [a for a, _ in farm_alerts]))

    return render(request, 'treatment/zone_treatment.html', {
        'title': 'Treatment',
        'zone': zone,
        'latest': latest,
        'alerts': alerts,
        'farm_alerts': farm_alerts,
        'form': form,
        'interventions': zone.interventions.all(),
    })


@login_required
@require_POST
def intervention_advance(request, pk):
    """Planned -> In progress -> Done."""
    intervention = get_object_or_404(Intervention, pk=pk)
    if intervention.status == 'planned':
        intervention.status = 'in_progress'
    elif intervention.status == 'in_progress':
        intervention.status = 'done'
        intervention.ended_at = timezone.now()
    intervention.save()
    return redirect('zone-treatment', pk=intervention.zone.pk)


@login_required
@require_POST
def intervention_delete(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)
    zone_pk = intervention.zone.pk
    if request.user == intervention.author:
        intervention.delete()
        messages.success(request, "Intervention deleted.")
    return redirect('zone-treatment', pk=zone_pk)
