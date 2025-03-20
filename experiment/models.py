# experiment/models.py
from django.db import models

class Experiment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    data_file = models.FileField(upload_to='experiments/', blank=True, null=True)

    def __str__(self):
        return self.name

class Signal(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    pattern = models.JSONField()
    signal_file = models.FileField(upload_to='signals/', blank=True, null=True)
    generation = models.IntegerField(default=0, help_text='Generation number for evolved signals')

    def __str__(self):
        return f"{self.name} - {self.experiment.name}"

class Demographics(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say')
    ]
    
    AGE_RANGE_CHOICES = [
        ('18-24', '18-24'),
        ('25-34', '25-34'),
        ('35-44', '35-44'),
        ('45-54', '45-54'),
        ('55+', '55 and above')
    ]
    
    EDUCATION_CHOICES = [
        ('HS', 'High School'),
        ('BD', "Bachelor's Degree"),
        ('MD', "Master's Degree"),
        ('PHD', 'Doctorate'),
        ('O', 'Other')
    ]
    
    ROBOT_EXPERIENCE_CHOICES = [
        ('none', 'No Experience'),
        ('basic', 'Basic Experience'),
        ('intermediate', 'Intermediate Experience'),
        ('advanced', 'Advanced Experience')
    ]
    
    NATIONALITY_CHOICES = [
        ('AF', 'Afghanistan'),
        ('AL', 'Albania'),
        ('DZ', 'Algeria'),
        ('AD', 'Andorra'),
        ('AO', 'Angola'),
        ('AG', 'Antigua and Barbuda'),
        ('AR', 'Argentina'),
        ('AM', 'Armenia'),
        ('AU', 'Australia'),
        ('AT', 'Austria'),
        ('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),
        ('BH', 'Bahrain'),
        ('BD', 'Bangladesh'),
        ('BB', 'Barbados'),
        ('BY', 'Belarus'),
        ('BE', 'Belgium'),
        ('BZ', 'Belize'),
        ('BJ', 'Benin'),
        ('BT', 'Bhutan'),
        ('BO', 'Bolivia'),
        ('BA', 'Bosnia and Herzegovina'),
        ('BW', 'Botswana'),
        ('BR', 'Brazil'),
        ('BN', 'Brunei'),
        ('BG', 'Bulgaria'),
        ('BF', 'Burkina Faso'),
        ('BI', 'Burundi'),
        ('CV', 'Cabo Verde'),
        ('KH', 'Cambodia'),
        ('CM', 'Cameroon'),
        ('CA', 'Canada'),
        ('CF', 'Central African Republic'),
        ('TD', 'Chad'),
        ('CL', 'Chile'),
        ('CN', 'China'),
        ('CO', 'Colombia'),
        ('KM', 'Comoros'),
        ('CG', 'Congo'),
        ('CD', 'Congo (Democratic Republic)'),
        ('CR', 'Costa Rica'),
        ('CI', 'Côte d\'Ivoire'),
        ('HR', 'Croatia'),
        ('CU', 'Cuba'),
        ('CY', 'Cyprus'),
        ('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),
        ('DJ', 'Djibouti'),
        ('DM', 'Dominica'),
        ('DO', 'Dominican Republic'),
        ('EC', 'Ecuador'),
        ('EG', 'Egypt'),
        ('SV', 'El Salvador'),
        ('GQ', 'Equatorial Guinea'),
        ('ER', 'Eritrea'),
        ('EE', 'Estonia'),
        ('SZ', 'Eswatini'),
        ('ET', 'Ethiopia'),
        ('FJ', 'Fiji'),
        ('FI', 'Finland'),
        ('FR', 'France'),
        ('GA', 'Gabon'),
        ('GM', 'Gambia'),
        ('GE', 'Georgia'),
        ('DE', 'Germany'),
        ('GH', 'Ghana'),
        ('GR', 'Greece'),
        ('GD', 'Grenada'),
        ('GT', 'Guatemala'),
        ('GN', 'Guinea'),
        ('GW', 'Guinea-Bissau'),
        ('GY', 'Guyana'),
        ('HT', 'Haiti'),
        ('HN', 'Honduras'),
        ('HU', 'Hungary'),
        ('IS', 'Iceland'),
        ('IN', 'India'),
        ('ID', 'Indonesia'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('IE', 'Ireland'),
        ('IL', 'Israel'),
        ('IT', 'Italy'),
        ('JM', 'Jamaica'),
        ('JP', 'Japan'),
        ('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),
        ('KE', 'Kenya'),
        ('KI', 'Kiribati'),
        ('KP', 'Korea (North)'),
        ('KR', 'Korea (South)'),
        ('KW', 'Kuwait'),
        ('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),
        ('LV', 'Latvia'),
        ('LB', 'Lebanon'),
        ('LS', 'Lesotho'),
        ('LR', 'Liberia'),
        ('LY', 'Libya'),
        ('LI', 'Liechtenstein'),
        ('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MG', 'Madagascar'),
        ('MW', 'Malawi'),
        ('MY', 'Malaysia'),
        ('MV', 'Maldives'),
        ('ML', 'Mali'),
        ('MT', 'Malta'),
        ('MH', 'Marshall Islands'),
        ('MR', 'Mauritania'),
        ('MU', 'Mauritius'),
        ('MX', 'Mexico'),
        ('FM', 'Micronesia'),
        ('MD', 'Moldova'),
        ('MC', 'Monaco'),
        ('MN', 'Mongolia'),
        ('ME', 'Montenegro'),
        ('MA', 'Morocco'),
        ('MZ', 'Mozambique'),
        ('MM', 'Myanmar'),
        ('NA', 'Namibia'),
        ('NR', 'Nauru'),
        ('NP', 'Nepal'),
        ('NL', 'Netherlands'),
        ('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),
        ('NE', 'Niger'),
        ('NG', 'Nigeria'),
        ('MK', 'North Macedonia'),
        ('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),
        ('PW', 'Palau'),
        ('PS', 'Palestine'),
        ('PA', 'Panama'),
        ('PG', 'Papua New Guinea'),
        ('PY', 'Paraguay'),
        ('PE', 'Peru'),
        ('PH', 'Philippines'),
        ('PL', 'Poland'),
        ('PT', 'Portugal'),
        ('QA', 'Qatar'),
        ('RO', 'Romania'),
        ('RU', 'Russia'),
        ('RW', 'Rwanda'),
        ('KN', 'Saint Kitts and Nevis'),
        ('LC', 'Saint Lucia'),
        ('VC', 'Saint Vincent and the Grenadines'),
        ('WS', 'Samoa'),
        ('SM', 'San Marino'),
        ('ST', 'Sao Tome and Principe'),
        ('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),
        ('RS', 'Serbia'),
        ('SC', 'Seychelles'),
        ('SL', 'Sierra Leone'),
        ('SG', 'Singapore'),
        ('SK', 'Slovakia'),
        ('SI', 'Slovenia'),
        ('SB', 'Solomon Islands'),
        ('SO', 'Somalia'),
        ('ZA', 'South Africa'),
        ('SS', 'South Sudan'),
        ('ES', 'Spain'),
        ('LK', 'Sri Lanka'),
        ('SD', 'Sudan'),
        ('SR', 'Suriname'),
        ('SE', 'Sweden'),
        ('CH', 'Switzerland'),
        ('SY', 'Syria'),
        ('TW', 'Taiwan'),
        ('TJ', 'Tajikistan'),
        ('TZ', 'Tanzania'),
        ('TH', 'Thailand'),
        ('TL', 'Timor-Leste'),
        ('TG', 'Togo'),
        ('TO', 'Tonga'),
        ('TT', 'Trinidad and Tobago'),
        ('TN', 'Tunisia'),
        ('TR', 'Turkey'),
        ('TM', 'Turkmenistan'),
        ('TV', 'Tuvalu'),
        ('UG', 'Uganda'),
        ('UA', 'Ukraine'),
        ('AE', 'United Arab Emirates'),
        ('GB', 'United Kingdom'),
        ('US', 'United States'),
        ('UY', 'Uruguay'),
        ('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),
        ('VA', 'Vatican City'),
        ('VE', 'Venezuela'),
        ('VN', 'Vietnam'),
        ('YE', 'Yemen'),
        ('ZM', 'Zambia'),
        ('ZW', 'Zimbabwe'),
        ('OT', 'Other')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age_range = models.CharField(max_length=10, choices=AGE_RANGE_CHOICES)
    education = models.CharField(max_length=3, choices=EDUCATION_CHOICES)
    robot_experience = models.CharField(max_length=12, choices=ROBOT_EXPERIENCE_CHOICES)
    nationality = models.CharField(max_length=2, choices=NATIONALITY_CHOICES, default='OT')
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='participants')

    def __str__(self):
        return f"Participant {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name_plural = "Demographics"

class LEDPattern(models.Model):
    PATTERN_TYPES = [
        ('blink', 'Blinking'),
        ('fade', 'Fading'),
        ('wave', 'Wave'),
        ('pulse', 'Pulsing'),
        ('rainbow', 'Rainbow'),
        ('solid', 'Solid Color')
    ]

    name = models.CharField(max_length=100)
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPES)
    parameters = models.JSONField(help_text='Pattern-specific parameters (colors, speed, intensity, etc.)')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.pattern_type})"

    class Meta:
        ordering = ['-created_at']

class EmotionFeedback(models.Model):
    demographics = models.ForeignKey(Demographics, on_delete=models.CASCADE, related_name='emotion_feedbacks')
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE, related_name='emotion_feedbacks')
    valence = models.FloatField(help_text='Emotional valence value (-1 to 1)')
    arousal = models.FloatField(help_text='Emotional arousal value (-1 to 1)')
    timestamp = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True, help_text='When the animation was first shown')
    end_time = models.DateTimeField(null=True, blank=True, help_text='When feedback was submitted or skipped')
    response_time_ms = models.IntegerField(null=True, blank=True, help_text='Response time in milliseconds')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes or observations')

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = "Emotion Feedback"

    def __str__(self):
        return f"Feedback from {self.demographics} for {self.signal}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not -1 <= self.valence <= 1:
            raise ValidationError({'valence': 'Valence must be between -1 and 1'})
        if not -1 <= self.arousal <= 1:
            raise ValidationError({'arousal': 'Arousal must be between -1 and 1'})
