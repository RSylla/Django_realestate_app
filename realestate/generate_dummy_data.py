import os
import django
from faker import Faker
from random import choice, randint, uniform
from django.utils import timezone
from datetime import timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realestate.settings')
django.setup()

from statistics_app.models import Maakond, Linn, Kinnisvara, Klient, Maakler, Tehing

fake = Faker('et_EE')

def random_date_within_5_years():
    """Generate a random date within the last 5 years."""
    today = timezone.now()
    days_in_5_years = 5 * 365  # Approximate days in 5 years
    random_days = random.randint(0, days_in_5_years)
    return today - timedelta(days=random_days)

def create_maakond():
    maakonnad = [
    "Harjumaa", "Hiiumaa", "Ida-Virumaa", "Jõgevamaa", "Järvamaa", 
    "Läänemaa", "Lääne-Virumaa", "Põlvamaa", "Pärnumaa", 
    "Raplamaa", "Saaremaa", "Tartumaa", "Valgamaa", "Viljandimaa", "Võrumaa"
    ]
    for nimi in maakonnad:
        maakond = Maakond.objects.create(nimi=nimi)
        maakond.loomise_kuupäev = timezone.now() - timedelta(days=(5 * 365))
        maakond.save()
    print('Finished populating "Maakonnad"')

def create_linnad():
    maakonnad = Maakond.objects.all()
    for maakond in maakonnad:
        eesti_linnad = {
                'Harjumaa': ['Tallinn', 'Keila', 'Maardu', 'Saue', 'Paldiski'],
                'Hiiumaa': ['Kärdla'],
                'Ida-Virumaa': ['Narva', 'Narva-Jõesuu', 'Kohtla-Järve', 'Jõhvi', 'Sillamäe'],
                'Jõgevamaa': ['Jõgeva', 'Mustvee', 'Põltsamaa'],
                'Järvamaa': ['Paide', 'Türi'],
                'Läänemaa': ['Haapsalu'],
                'Lääne-Virumaa': ['Rakvere', 'Tapa', 'Kunda'],
                'Põlvamaa': ['Põlva', 'Kanepi', 'Värska'],
                'Pärnumaa': ['Pärnu', 'Kilingi-Nõmme', 'Sauga', 'Vändra'],
                'Raplamaa': ['Rapla', 'Kohila', 'Märjamaa'],
                'Saaremaa': ['Kuressaare'],
                'Tartumaa': ['Tartu', 'Elva', 'Kallaste'],
                'Valgamaa': ['Valga', 'Otepää', 'Tõrva'],
                'Viljandimaa': ['Viljandi', 'Abja-Paluoja', 'Mõisaküla'],
                'Võrumaa': ['Võru', 'Antsla', 'Rõuge']
                }
        linnad = eesti_linnad.get(maakond.nimi, [])
        for linn in linnad:
            linn_obj = Linn.objects.create(nimi=linn, maakond=maakond)
            linn_obj.loomise_kuupäev = timezone.now() - timedelta(days=(5 * 365))
            linn_obj.save()
    print('Finished populating "Linnad"')

def create_kinnisvara():
    linnad = Linn.objects.all()
    property_types = ['Korter', 'Maja', 'Äripind']
    building_types = ['Kivimaja', 'Puumaja', 'Paneelmaja']
    ownership_types = ['Eraomand', 'Munitsipaalomand', 'Riigiomand']
    condition_types = ['Elamiskõlbmatu', 'Vajab remonti', 'Keskmine', 
                       'Remonditud', 'Renoveeritud', 'Uus']

    # Define ranges for square meters based on the number of rooms
    size_ranges = {
        1: (16, 45),
        2: (40, 60),
        3: (50, 100),
        4: (75, 150),
        5: (120, 250)
    }

    for _ in range(30000):
        tube = randint(1, 5)
        min_size, max_size = size_ranges[tube]
        pindala = round(uniform(min_size, max_size), 2)

        tüüp = choice(property_types)
        seisukord = choice(condition_types)
        ehitusaasta = randint(1950, 2023) if seisukord != 'Uus' else 2024

        kinnisvara = Kinnisvara.objects.create(
            aadress=fake.address(),
            tüüp=tüüp,
            ehitise_tüüp=choice(building_types),
            pindala=pindala,
            tube=tube,
            korrus=randint(1, 10),
            ehitusaasta=ehitusaasta,
            linn=choice(linnad),
            omandi_vorm=choice(ownership_types),
            seisukord=seisukord,
            kirjeldus=fake.text(max_nb_chars=150)
        )
        kinnisvara.loomise_kuupäev = timezone.now() - timedelta(days=(5 * 365))
        kinnisvara.save()
    print('Finished populating "Kinnisvara"')

def create_klient():
    client_types = ['Eraisik', 'Juriidiline isik', 'Munitsipaal', 'Välismaalane']
    for _ in range(100000):
        klient_tüüp = choice(client_types)
        eesnimi = fake.first_name() if klient_tüüp != 'Juriidiline isik' else None
        perekonnanimi = fake.last_name() if klient_tüüp != 'Juriidiline isik' else None
        firma_nimi = fake.company() if klient_tüüp == 'Juriidiline isik' else None
        klient = Klient.objects.create(
            eesnimi=eesnimi,
            perekonnanimi=perekonnanimi,
            firma_nimi=firma_nimi,
            klient_tüüp=klient_tüüp,
            isikukood=fake.ssn(),
            telefon=fake.phone_number(),
            email=fake.email()
        )
        klient.loomise_kuupäev = timezone.now() - timedelta(days=(5 * 365))
        klient.save()
    print('Finished populating "Kliendid"')

def create_maakler():
    maakonnad = Maakond.objects.all()
    for _ in range(30):
        maakler = Maakler.objects.create(
            eesnimi=fake.first_name(),
            perekonnanimi=fake.last_name(),
            telefon=fake.phone_number(),
            email=fake.email(),
            büroo_nimi=fake.company(),
            maakond=choice(maakonnad)
        )
        maakler.loomise_kuupäev = timezone.now() - timedelta(days=(5 * 365))
        maakler.save()
    print('Finished populating "Maaklerid"')

def create_tehing():
    properties = Kinnisvara.objects.all()
    clients = Klient.objects.all()
    agents = Maakler.objects.all()
    transaction_types = ['Müük', 'Üür']

    price_ranges = {
        'Korter': (20_000, 150_000),
        'Maja': (100_000, 400_000),
        'Äripind': (80_000, 300_000)
    }

    # Define price ranges for properties based on size and condition
    for kinnisvara in properties:
        num_transactions = randint(0, 3)  # Each property can have 0 to 3 transactions
        if num_transactions != 0:
            for _ in range(num_transactions):
                # Get the base price range based on the type of property
                base_min_price, base_max_price = price_ranges[kinnisvara.tüüp]

                size_ranges = {
                    1: (16, 45),
                    2: (40, 60),
                    3: (50, 100),
                    4: (75, 150),
                    5: (120, 250)
                }
                _ , max_size = size_ranges[kinnisvara.tube] 
                # Adjust the price based on the size and condition
                size_factor = kinnisvara.pindala / max_size  # Bigger properties should have higher prices
                condition_factor = {
                    'Elamiskõlbmatu': 0.2,
                    'Vajab remonti': 0.6,
                    'Keskmine': 1,
                    'Remonditud': 1.2,
                    'Renoveeritud': 1.5,
                    'Uus': 2
                }[kinnisvara.seisukord]

                # Calculate the price as an integer
                price = int(round(uniform(base_min_price, base_max_price) * size_factor * condition_factor))
                transaction_type = choice(transaction_types)

                hind = price if transaction_type == 'Müük' else (price / 200)

                ruutmeetrihind = round(hind / kinnisvara.pindala, 2)

                date = random_date_within_5_years()
                tehing = Tehing.objects.create(
                    kinnisvara=kinnisvara,
                    tehingu_tüüp=transaction_type,
                    kuupäev=date.date(),
                    hind=hind,
                    ruutmeetrihind=ruutmeetrihind,
                    maakler=choice(agents),
                    olek=choice(['Kinnitatud', 'Ootel'])
                )
                tehing.loomise_kuupäev = date
                tehing.save()

                # Add multiple buyers and sellers to each transaction
                tehing.ostjad.add(*clients.order_by('?')[:randint(1, 2)])
                tehing.müüjad.add(*clients.order_by('?')[:randint(1, 2)])
    print('Finished populating "Tehingud"')

def generate_data():
    create_maakond()
    create_linnad()
    create_kinnisvara()
    create_klient()
    create_maakler()
    create_tehing()
    print("Data generation complete.")

if __name__ == '__main__':
    generate_data()

