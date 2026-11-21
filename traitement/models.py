from django.db import models
from django.contrib.auth.models import User
from zone.models import Zone


class Intervention(models.Model):
    TYPES_ROBOT = [
        ('pompier', "Robot pompier (incendie)"),
        ('irrigation', "Robot d'irrigation (sécheresse)"),
        ('oxygenation', "Robot d'oxygénation (manque d'oxygène)"),
        ('filtration', "Robot de filtration (pollution)"),
        ('polyvalent', "Robot polyvalent"),
    ]
    STATUTS = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ]

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='interventions')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    type_robot = models.CharField("Type de robot", max_length=20, choices=TYPES_ROBOT)
    nb_robots = models.PositiveIntegerField("Nombre de robots", default=1)
    nb_ouvriers = models.PositiveIntegerField("Nombre d'ouvriers", default=0)
    ressources = models.TextField("Ressources nécessaires", blank=True,
                                  help_text="Ex : 2000 L d'eau, 3 filtres, 1 générateur…")
    temps_estime = models.FloatField("Temps estimé (heures)")
    commentaire = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifiee')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.get_type_robot_display()} - {self.zone.name_zone}"

    @property
    def badge_statut(self):
        return {'planifiee': 'secondary', 'en_cours': 'warning', 'terminee': 'success'}.get(self.statut, 'secondary')
