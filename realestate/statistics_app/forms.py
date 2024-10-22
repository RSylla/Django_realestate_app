
from django import forms
from statistics_app.models import Maakond, Linn, Maakler
from .models import Maakond, Linn, Kinnisvara, Klient, Maakler, Tehing

class MaakondForm(forms.ModelForm):
    class Meta:
        model = Maakond
        fields = ['nimi']

class LinnForm(forms.ModelForm):
    class Meta:
        model = Linn
        fields = ['nimi', 'maakond']

class KinnisvaraForm(forms.ModelForm):
    class Meta:
        model = Kinnisvara
        fields = ['aadress', 'tüüp', 'ehitise_tüüp', 'seisukord', 'pindala', 'tube', 'korrus', 'ehitusaasta', 'linn', 'omandi_vorm', 'kirjeldus']

class KlientForm(forms.ModelForm):
    class Meta:
        model = Klient
        fields = ['eesnimi', 'perekonnanimi', 'firma_nimi', 'klient_tüüp', 'isikukood', 'telefon', 'email']

class MaaklerForm(forms.ModelForm):
    class Meta:
        model = Maakler
        fields = ['eesnimi', 'perekonnanimi', 'telefon', 'email', 'büroo_nimi', 'maakond']

class TehingForm(forms.ModelForm):
    class Meta:
        model = Tehing
        fields = ['kinnisvara', 'tehingu_tüüp', 'kuupäev', 'hind', 'ruutmeetrihind', 'maakler', 'olek']


class TransactionQueryForm(forms.Form):
    maakond = forms.ModelChoiceField(
        label='Maakond',
        queryset=Maakond.objects.all(),
        required=False,
        empty_label='Vali maakond'  # Means "Select county" in Estonian
    )
    linn = forms.ModelChoiceField(
        label='Linn',
        queryset=Linn.objects.none(),
        required=False,
        empty_label='Vali linn'  # Means "Select city" in Estonian
    )
    maakler = forms.ModelChoiceField(
        label='Maakler',
        queryset=Maakler.objects.all(),
        required=False,
        empty_label='Vali maakler'
    )
    start_date = forms.DateField(
        label='Kuupäev alates',
        required=False,
        widget=forms.TextInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label='Kuupäev kuni',
        required=False,
        widget=forms.TextInput(attrs={'type': 'date'})
    )
    property_type = forms.ChoiceField(
        label='Kinnisvara tüüp',
        choices=[('Korter', 'Korter'), ('Maja', 'Maja'), ('Äripind', 'Äripind')],
        required=False
    )
    min_price = forms.IntegerField(
        label='Hind alates',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter minimum price...'})
    )
    max_price = forms.IntegerField(
        label='Hind kuni',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter maximum price...'})
    )
    min_pindala = forms.DecimalField(
        label='Pindala alates (m²)',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter minimum area...'})
    )
    max_pindala = forms.DecimalField(
        label='Pindala kuni (m²)',
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter maximum area...'})
    )
    seisukord = forms.ChoiceField(
        label='Seisukord',
        choices=[('', ''),
                 ('Elamiskõlbmatu', 'Elamiskõlbmatu'), 
                 ('Vajab remonti', 'Vajab remonti'), 
                 ('keskmine', 'keskmine'), 
                 ('remonditud', 'remonditud'), 
                 ('Renoveeritud', 'Renoveeritud'), 
                 ('Uus', 'Uus')],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If a maakond is preselected, filter the linn queryset to include only cities in that county
        if 'maakond' in self.data:
            try:
                maakond_id = int(self.data.get('maakond'))
                self.fields['linn'].queryset = Linn.objects.filter(maakond_id=maakond_id).order_by('nimi')
            except (ValueError, TypeError):
                pass
        elif self.initial.get('maakond'):
            self.fields['linn'].queryset = Linn.objects.filter(maakond=self.initial['maakond']).order_by('nimi')
