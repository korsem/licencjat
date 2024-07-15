from django.utils.translation import gettext as _

MUSCLE_GROUP_CHOICES = [
    ('upper', _('Upper Body')),
    ('lower', _('Lower Body')),
    ('core', _('Core')),
    ('full', _('Full Body')),
    # ('cardio', _('Cardio')), i by sie czy cardio wywalilo, albo na podstawie tego przypisąło
    ('chest', _('Chest')),
    ('back', _('Back')),
    ('shoulders', _('Shoulders')),
    ('biceps', _('Biceps')),
    ('triceps', _('Triceps')),
    ('forearms', _('Forearms')),
    ('quadriceps', _('Quadriceps')),
    ('hamstrings', _('Hamstrings')),
    ('calves', _('Calves')),
    ('glutes', _('Glutes')),
    ('adductors', _('Adductors')),
    ('abductors', _('Abductors')),
    ('obliques', _('Obliques')),
    ('transverse_abdominis', _('Transverse Abdominis')),
]

EQUIPMENT_CHOICES = [
    ('none', _('None')),
    ('dumbbell', _('Dumbbell')),
    ('barbell', _('Barbell')),
    ('machine', _('Machine')),
    ('miniband_lt_5kg', _('Miniband < 5 kg')),
    ('miniband_5_10kg', _('Miniband >= 5 kg and <= 10 kg')),
    ('miniband_gt_10kg', _('Miniband > 10 kg')),
    ('resistance_band_lt_5kg', _('Resistance Band < 5 kg')),
    ('resistance_band_5_10kg', _('Resistance Band >= 5 kg and <= 10 kg')),
    ('resistance_band_gt_10kg', _('Resistance Band > 10 kg')),
    ('gym_ball', _('Gym Ball')),
    ('kettlebell', _('Kettlebell')),
]
# equipment w wersji char choices
# models.CharField(max_length=100, blank=True, choices=EQUIPMENT_CHOICES, default=None)
# dodać choices, if blank - brak sprzętu, będzie można filtrowac po tym

