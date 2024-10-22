from django.db import models
from django.utils import timezone
# Create your models here.

# Model for Maakond (County)
class Maakond(models.Model):
    nimi = models.CharField(max_length=100)  # e.g., "Harjumaa"
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nimi


# Model for Linn/Asula (City/Town)
class Linn(models.Model):
    nimi = models.CharField(max_length=100)  # e.g., "Tallinn"
    maakond = models.ForeignKey(Maakond, on_delete=models.CASCADE)
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nimi}-{self.maakond}"


# Model for Kinnisvara (Property)
class Kinnisvara(models.Model):
    aadress = models.CharField(max_length=255)  # Property address
    tüüp = models.CharField(max_length=50, choices=[('Korter', 'Korter'), 
                                                    ('Maja', 'Maja'), 
                                                    ('Äripind', 'Äripind')])
    ehitise_tüüp = models.CharField(max_length=50, choices=[('Kivimaja', 'Kivimaja'), 
                                                            ('Puumaja', 'Puumaja'), 
                                                            ('Paneelmaja', 'Paneelmaja')])
    seisukord = models.CharField(max_length=50, choices=[('Elamiskõlbmatu', 'Elamiskõlbmatu'), 
                                                         ('Vajab remonti', 'Vajab remonti'), 
                                                         ('Keskmine', 'keskmine'), 
                                                         ('remonditud', 'remonditud'), 
                                                         ('Renoveeritud', 'Renoveeritud'),
                                                         ('Uus', 'Uus')])
    pindala = models.FloatField() # Area in square meters
    tube = models.IntegerField()  # Number of rooms
    korrus = models.IntegerField()  # Floor number
    ehitusaasta = models.IntegerField()  # Year of construction
    linn = models.ForeignKey(Linn, on_delete=models.CASCADE)
    omandi_vorm = models.CharField(max_length=50, choices=[('Eraomand', 'Eraomand'), ('Korteriomand', 'Korteriomand')])
    kirjeldus = models.TextField()
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tüüp}-{self.tube}-{self.pindala}-{self.linn}"


# Model for Klient (Client)
class Klient(models.Model):
    Eraisik = 'Eraisik'
    Juriidiline_isik = 'Juriidiline isik'
    Munitsipaal = 'Munitsipaal'
    Välismaalane = 'Välismaalane'

    KLIENT_TÜÜP_CHOICES = [
        (Eraisik, 'Eraisik'),
        (Juriidiline_isik, 'Juriidiline isik'),
        (Munitsipaal, 'Munitsipaal'),
        (Välismaalane, 'Välismaalane'),
    ]

    eesnimi = models.CharField(max_length=150, blank=True, null=True)
    perekonnanimi = models.CharField(max_length=150, blank=True, null=True)
    firma_nimi = models.CharField(max_length=255, blank=True, null=True)  # For legal entities
    klient_tüüp = models.CharField(max_length=100, choices=KLIENT_TÜÜP_CHOICES)
    isikukood = models.CharField(max_length=100)
    telefon = models.CharField(max_length=100)
    email = models.EmailField()
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.klient_tüüp == self.Juriidiline_isik:
            return self.firma_nimi or "Juriidiline isik"
        return f"{self.eesnimi} {self.perekonnanimi}"


# Model for Maakler (Real Estate Agent)
class Maakler(models.Model):
    eesnimi = models.CharField(max_length=100)
    perekonnanimi = models.CharField(max_length=100)
    telefon = models.CharField(max_length=50)
    email = models.EmailField()
    büroo_nimi = models.CharField(max_length=255)
    maakond = models.ForeignKey(Maakond, on_delete=models.CASCADE)
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.eesnimi} {self.perekonnanimi} - {self.büroo_nimi}"


# Model for Tehing (Transaction)
class Tehing(models.Model):
    kinnisvara = models.ForeignKey(Kinnisvara, on_delete=models.CASCADE)
    tehingu_tüüp = models.CharField(max_length=20, choices=[('Müük', 'Müük'), ('Üür', 'Üür')])
    kuupäev = models.DateField()
    hind = models.IntegerField()
    ruutmeetrihind = models.FloatField()
    ostjad = models.ManyToManyField(Klient, related_name='ostja_tehingud')
    müüjad = models.ManyToManyField(Klient, related_name='müüja_tehingud')
    maakler = models.ForeignKey(Maakler, on_delete=models.CASCADE)
    olek = models.CharField(max_length=20, choices=[('Kinnitatud', 'Kinnitatud'), ('Ootel', 'Ootel')])
    loomise_kuupäev = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tehingu_tüüp} - {self.kinnisvara.aadress} on {self.kuupäev}"
