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
from treatment.models import Intervention
from .models import FarmMeasurement, Measurement, Report, is_farm

FIELDS = ['temperature', 'humidity', 'oxygen', 'co2']

# Probability of each risk level for an analysis
LEVEL_PROBABILITIES = {'low': 30, 'medium': 30, 'high': 25, 'critical': 15}
# Number of problems per level
PROBLEM_COUNT = {'low': [0], 'medium': [1], 'high': [2], 'critical': [3, 4]}
# Value ranges: (normal, problem)
RANGES = {
    'temperature': ((15, 38), (41, 50)),        # > 40 => fire risk
    'humidity':    ((25, 80), (5, 19)),         # < 20 => drought
    'oxygen':      ((18.5, 21), (14, 17.5)),    # < 18 => low oxygen
    'co2':         ((350, 950), (1050, 1800)),  # > 1000 => air pollution
}

# Farming zones: 25 % chance of a harvest problem, 20 % chance of a natural disaster
FARM_PROBLEM_PROBABILITY = 25
DISASTER_PROBABILITY = 20
DISASTERS = ['flood', 'hail', 'storm', 'insects']


def generate_values():
    level = random.choices(list(LEVEL_PROBABILITIES), weights=list(LEVEL_PROBABILITIES.values()))[0]
    problems = random.sample(FIELDS, random.choice(PROBLEM_COUNT[level]))
    values = {}
    for field in FIELDS:
        normal, problem = RANGES[field]
        low, high = problem if field in problems else normal
        values[field] = round(random.uniform(low, high), 1)
    values['co2'] = round(values['co2'])
    return values


def generate_farm_values():
    values = generate_harvest_values()
    values['disaster'] = ''
    if random.uniform(0, 100) < DISASTER_PROBABILITY:
        # a disaster damages the harvest
        values['disaster'] = random.choice(DISASTERS)
        values['yield_percent'] = round(values['yield_percent'] * 0.6)
        if values['harvest_state'] == 'good':
            values['harvest_state'] = 'average'
    return values


def generate_harvest_values():
    if random.uniform(0, 100) >= FARM_PROBLEM_PROBABILITY:
        return {'yield_percent': round(random.uniform(80, 110)), 'harvest_state': 'good', 'needs_fertilizer': False}
    problem = random.choice(['harvest', 'fertilizer', 'both'])
    if problem == 'harvest':
        return {'yield_percent': round(random.uniform(25, 55)), 'harvest_state': 'poor', 'needs_fertilizer': False}
    if problem == 'fertilizer':
        return {'yield_percent': round(random.uniform(55, 78)), 'harvest_state': 'average', 'needs_fertilizer': True}
    return {'yield_percent': round(random.uniform(15, 45)), 'harvest_state': 'poor', 'needs_fertilizer': True}


# Problem -> measurement field it comes from
PROBLEM_FIELDS = {
    "Fire risk": 'temperature',
    "Drought": 'humidity',
    "Low oxygen": 'oxygen',
    "Air pollution": 'co2',
}
DISASTER_LABELS = dict(FarmMeasurement.DISASTERS)


def normal_value(field):
    low, high = RANGES[field][0]
    value = round(random.uniform(low, high), 1)
    return round(value) if field == 'co2' else value


def heal(values, farm_values, problems):
    """Removes the given problems from generated values (in place)."""
    for problem in problems:
        if problem in PROBLEM_FIELDS:
            values[PROBLEM_FIELDS[problem]] = normal_value(PROBLEM_FIELDS[problem])
    if farm_values is None:
        return
    if farm_values.get('disaster') and DISASTER_LABELS[farm_values['disaster']] in problems:
        farm_values['disaster'] = ''
    if "Needs fertilizer" in problems:
        farm_values['needs_fertilizer'] = False
    if "Poor harvest" in problems and farm_values['harvest_state'] == 'poor':
        farm_values['harvest_state'] = 'average'
        farm_values['yield_percent'] = round(random.uniform(55, 78))
    if (farm_values['harvest_state'] == 'average' and not farm_values['needs_fertilizer']
            and not farm_values.get('disaster')):
        farm_values['harvest_state'] = 'good'
        farm_values['yield_percent'] = round(random.uniform(80, 110))


def immune_problems(zone):
    """Problems recently treated in this zone that cannot come back yet."""
    problems = set()
    for intervention in Intervention.objects.filter(zone=zone, status='done', immunity_runs__gt=0):
        problems.update(intervention.problem_list())
    return problems


def create_treated_measurement(zone, problems):
    """After a finished intervention: copy of the latest measurement without the treated problems."""
    latest = zone.measurements.first()
    if not latest:
        return None
    values = {f: getattr(latest, f) for f in FIELDS}
    old_farm = getattr(latest, 'farm', None)
    farm_values = None
    if old_farm:
        farm_values = {'yield_percent': old_farm.yield_percent, 'harvest_state': old_farm.harvest_state,
                       'needs_fertilizer': old_farm.needs_fertilizer, 'disaster': old_farm.disaster}
    heal(values, farm_values, problems)
    measurement = Measurement.objects.create(zone=zone, **values)
    if farm_values is not None:
        FarmMeasurement.objects.create(measurement=measurement, **farm_values)
    return measurement


@login_required
def zone_analysis(request, pk):
    zone = get_object_or_404(Zone, pk=pk)
    measurements = zone.measurements.select_related('farm')

    stats = {}
    if measurements.exists():
        agg = measurements.aggregate(
            **{f'{f}_avg': Avg(f) for f in FIELDS},
            **{f'{f}_min': Min(f) for f in FIELDS},
            **{f'{f}_max': Max(f) for f in FIELDS},
        )
        stats = {f: {'avg': agg[f'{f}_avg'], 'min': agg[f'{f}_min'], 'max': agg[f'{f}_max']} for f in FIELDS}

    latest = measurements.first()

    farm = is_farm(zone)
    farm_stats = {}
    if farm:
        farm_qs = FarmMeasurement.objects.filter(measurement__zone=zone)
        count = farm_qs.count()
        if count:
            farm_stats = {
                'count': count,
                'avg_yield': farm_qs.aggregate(y=Avg('yield_percent'))['y'],
                'good': farm_qs.filter(harvest_state='good').count(),
                'poor': farm_qs.filter(harvest_state='poor').count(),
                'fertilizer': farm_qs.filter(needs_fertilizer=True).count(),
                'disasters': farm_qs.exclude(disaster='').count(),
            }

    return render(request, 'analysis/zone_analysis.html', {
        'title': 'Analysis',
        'zone': zone,
        'latest': latest,
        'alerts': latest.alerts() if latest else [],
        'farm': farm,
        'latest_farm': getattr(latest, 'farm', None) if latest else None,
        'farm_stats': farm_stats,
        'stats': stats,
        'measurement_count': measurements.count(),
        'measurements': measurements[:15],
        'reports': zone.reports.all(),
        'immune': sorted(immune_problems(zone)),
    })


@login_required
@require_POST
def run_analysis(request, pk):
    """Robot simulation: generates a random measurement."""
    zone = get_object_or_404(Zone, pk=pk)
    values = generate_values()
    farm_values = generate_farm_values() if is_farm(zone) else None

    # recently treated problems cannot come back for a few analyses
    immune = immune_problems(zone)
    heal(values, farm_values, immune)
    for intervention in Intervention.objects.filter(zone=zone, status='done', immunity_runs__gt=0):
        intervention.immunity_runs -= 1
        intervention.save(update_fields=['immunity_runs'])

    measurement = Measurement.objects.create(zone=zone, **values)
    if farm_values is not None:
        FarmMeasurement.objects.create(measurement=measurement, **farm_values)
    messages.success(request, "The robot sent back a new measurement.")
    return redirect('zone-analysis', pk=zone.pk)


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    fields = ['title', 'content', 'risk_level']

    def dispatch(self, request, *args, **kwargs):
        self.zone = get_object_or_404(Zone, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Pre-fills the report from the latest measurement."""
        latest = self.zone.measurements.first()
        if not latest:
            return {'title': f"Report - {self.zone.name_zone}"}
        alerts = latest.alerts()
        lines = [
            f"Measurement of {latest.date:%d/%m/%Y %H:%M}",
            f"Temperature: {latest.temperature} °C",
            f"Humidity: {latest.humidity} %",
            f"Oxygen: {latest.oxygen} %",
            f"CO2: {latest.co2} ppm",
            "",
            "Detected problems: " + (", ".join(alerts) if alerts else "none"),
        ]
        farm = getattr(latest, 'farm', None)
        if farm:
            farm_alerts = [a for a, _ in farm.alerts()]
            lines += [
                "",
                f"Farming zone ({self.zone.get_type_area_display()})",
                f"Yield: {farm.yield_percent:.0f} %",
                f"Harvest state: {farm.get_harvest_state_display()}",
                f"Needs fertilizer: {'yes' if farm.needs_fertilizer else 'no'}",
                f"Natural disaster: {farm.get_disaster_display() if farm.disaster else 'none'}",
                "Farming problems: " + (", ".join(farm_alerts) if farm_alerts else "none"),
            ]
        return {
            'title': f"Report - {self.zone.name_zone} - {latest.date:%d/%m/%Y}",
            'content': "\n".join(lines),
            'risk_level': latest.risk_level(),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone'] = self.zone
        return context

    def form_valid(self, form):
        form.instance.zone = self.zone
        form.instance.author = self.request.user
        messages.success(self.request, "Report created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('zone-analysis', kwargs={'pk': self.zone.pk})


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report


class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    fields = ['title', 'content', 'risk_level']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['zone'] = self.object.zone
        return context

    def test_func(self):
        return self.request.user == self.get_object().author


class ReportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Report

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse('zone-analysis', kwargs={'pk': self.object.zone.pk})
