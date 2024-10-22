from django.views import View
from .forms import TransactionQueryForm
from statistics_app.models import Tehing, Linn
from django.http import JsonResponse
from .forms import TransactionQueryForm, MaakondForm, LinnForm, KinnisvaraForm, \
KlientForm, MaaklerForm, TehingForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from .models import Maakond, Linn, Kinnisvara, Klient, Maakler, Tehing
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Max, Min, Avg
from collections import defaultdict


def index(request):
    # Get table information
    tables = {
        'Maakond': Maakond.objects.count(),
        'Linn': Linn.objects.count(),
        'Kinnisvara': Kinnisvara.objects.count(),
        'Klient': Klient.objects.count(),
        'Maakler': Maakler.objects.count(),
        'Tehing': Tehing.objects.count(),
    }

    # Calculate Kinnisvara price statistics
    kinnisvara_prices = Tehing.objects.aggregate(
        max_price=Max('hind'),
        min_price=Min('hind'),
        avg_price=Avg('hind')
    )

    # Find the maakler with the most tehingud (transactions)
    top_maakler = Maakler.objects.annotate(tehing_count=Count('tehing')).order_by('-tehing_count').first()

    # Find the city with the most tehingud
    top_city = Linn.objects.annotate(tehing_count=Count('kinnisvara__tehing')).order_by('-tehing_count').first()

    # Count of tehingud by year with additional statistics
    tehingud_by_year_data = Tehing.objects.values('kuupäev__year', 'kinnisvara__tüüp').annotate(
        total_transactions=Count('id'),
        avg_ruutmeetrihind=Avg('ruutmeetrihind'),
        avg_price=Avg('hind')
    )

    tehingud_by_year = defaultdict(lambda: {
        'total_transactions': 0,
        'avg_ruutmeetrihind': 0,
        'avg_prices_by_type': dict(defaultdict(float))
    })

    # Organize the data by year
    for entry in tehingud_by_year_data:
        year = entry['kuupäev__year']
        property_type = entry['kinnisvara__tüüp']
        tehingud_by_year[year]['total_transactions'] += entry['total_transactions']
        tehingud_by_year[year]['avg_ruutmeetrihind'] = entry['avg_ruutmeetrihind']
        tehingud_by_year[year]['avg_prices_by_type'][property_type] = entry['avg_price']

    # Convert defaultdict to a normal dict for template compatibility
    tehingud_by_year = dict(tehingud_by_year)
    context = {
        'tables': tables,
        'kinnisvara_prices': kinnisvara_prices,
        'top_maakler': top_maakler,
        'top_city': top_city,
        'tehingud_by_year': tehingud_by_year.items(),  # Pass as items to iterate in the template
    }

    return render(request, 'index.html', context)


def load_cities(request):
    maakond_id = request.GET.get('maakond')
    cities = Linn.objects.filter(maakond_id=maakond_id).order_by('nimi')
    return JsonResponse(list(cities.values('id', 'nimi')), safe=False)

# View for table selection after login
class TableSelectionView(LoginRequiredMixin, View):
    template_name = 'table_selection.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(csrf_exempt, name='dispatch')
class ManageModelView(LoginRequiredMixin, View):
    template_name = 'manage_model.html'
    model_class = None
    form_class = None

    paginate_by = 20    

    def get(self, request):
        search_query = request.GET.get('search', '')
        objects = self.model_class.objects.all()

        if search_query:
            # Dynamic search logic as in the previous example
            query = Q()
            for field in self.model_class._meta.fields:
                # Check if the field is a CharField or a TextField for partial matching
                if field.get_internal_type() in ['CharField', 'TextField']:
                    query |= Q(**{f"{field.name}__icontains": search_query})
                # Check for numeric fields and try to convert the search term
                elif field.get_internal_type() in ['IntegerField', 'DecimalField', 'FloatField']:
                    try:
                        # Attempt to convert the search query to a number
                        num_value = float(search_query)
                        query |= Q(**{f"{field.name}": num_value})
                    except ValueError:
                        # If conversion fails, skip this field for this query
                        pass

            # Handle ForeignKey relationships (e.g., Linn, Maakond)
            # Example: if the field is a ForeignKey, search in the related model's `nimi` field
            for field in self.model_class._meta.fields:
                if field.is_relation and field.many_to_one:
                    related_model_name = field.related_model._meta.model_name
                    # Assuming we want to search by the related model's 'nimi' field
                    query |= Q(**{f"{field.name}__nimi__icontains": search_query})

            # Apply the combined Q object to filter the results
            objects = objects.filter(query).distinct()

        # Implement pagination
        paginator = Paginator(objects, self.paginate_by)
        page_number = request.GET.get('page')
        try:
            objects = paginator.page(page_number)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)

        # Pass paginated objects and form to the template as context
        return render(request, self.template_name, {
            'objects': objects,
            'model_name': self.model_class._meta.verbose_name.title(),
            'fields': self.model_class._meta.fields,
            'form': self.form_class(),
            'paginator': paginator,
            'is_paginated': objects.has_other_pages(),
        })
        

    def post(self, request):
        # Handle adding a new entry
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()

        # Handle deletions if 'delete_<model_name>' is present in the POST data
        for key in request.POST:
            if key.startswith('delete_'):
                obj_id = request.POST.get(key)
                obj = get_object_or_404(self.model_class, id=obj_id)
                obj.delete()

        return redirect(request.path)


class TransactionQueryView(View):
    template_name = 'transaction_query.html'

    def get(self, request):
        form = TransactionQueryForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TransactionQueryForm(request.POST)
        transactions = Tehing.objects.all()

        if form.is_valid():
            # Filter by maakond (county)
            if form.cleaned_data['maakond']:
                transactions = transactions.filter(
                    kinnisvara__linn__maakond=form.cleaned_data['maakond']
                )
                form.fields['linn'].queryset = Linn.objects.filter(
                    maakond=form.cleaned_data['maakond']
                ).order_by('nimi')

            # Filter by linn (city)
            if form.cleaned_data['linn']:
                transactions = transactions.filter(
                    kinnisvara__linn=form.cleaned_data['linn']
                )

            # Filter by maakler (broker)
            if form.cleaned_data['maakler']:
                transactions = transactions.filter(
                    maakler=form.cleaned_data['maakler']
                )

            # Filter by date range
            if form.cleaned_data['start_date']:
                transactions = transactions.filter(
                    kuupäev__gte=form.cleaned_data['start_date']
                )
            if form.cleaned_data['end_date']:
                transactions = transactions.filter(
                    kuupäev__lte=form.cleaned_data['end_date']
                )

            # Filter by property type
            if form.cleaned_data['property_type']:
                transactions = transactions.filter(
                    kinnisvara__tüüp=form.cleaned_data['property_type']
                )

            # Filter by price range
            if form.cleaned_data['min_price']:
                transactions = transactions.filter(
                    hind__gte=form.cleaned_data['min_price']
                )
            if form.cleaned_data['max_price']:
                transactions = transactions.filter(
                    hind__lte=form.cleaned_data['max_price']
                )

            # Filter by area (pindala)
            if form.cleaned_data['min_pindala']:
                transactions = transactions.filter(
                    kinnisvara__pindala__gte=form.cleaned_data['min_pindala']
                )
            if form.cleaned_data['max_pindala']:
                transactions = transactions.filter(
                    kinnisvara__pindala__lte=form.cleaned_data['max_pindala']
                )

            # Filter by property condition (seisukord)
            if form.cleaned_data['seisukord']:
                transactions = transactions.filter(
                    kinnisvara__seisukord=form.cleaned_data['seisukord']
                )

        return render(request, self.template_name, {
            'form': form,
            'transactions': transactions
        })
    

from django.apps import apps

# Map of model names to form classes
FORM_CLASSES = {
    'maakond': MaakondForm,
    'linn': LinnForm,
    'kinnisvara': KinnisvaraForm,
    'klient': KlientForm,
    'maakler': MaaklerForm,
    'tehing': TehingForm,
}

@method_decorator(csrf_exempt, name='dispatch')
class EditModelView(LoginRequiredMixin, View):
    template_name = 'edit_model.html'

    def get_model_class(self, model_name):
        """Retrieve the model class based on model_name."""
        try:
            # Normalize the model name to lowercase for lookup
            return apps.get_model('statistics_app', model_name.lower())
        except LookupError:
            return None

    def get_form_class(self, model_name):
        """Retrieve the form class based on model_name."""
        return FORM_CLASSES.get(model_name.lower())

    def get(self, request, model_name, pk):
        # Retrieve the model class and object to edit
        model_class = self.get_model_class(model_name)
        form_class = self.get_form_class(model_name)

        if not model_class or not form_class:
            return redirect('select_table')  # Redirect to a selection page if model is invalid

        obj = get_object_or_404(model_class, pk=pk)
        form = form_class(instance=obj)
        return render(request, self.template_name, {
            'form': form,
            'object': obj,
            'model_name': model_class._meta.verbose_name.title(),
        })

    def post(self, request, model_name, pk):
        # Handle form submission for editing
        model_class = self.get_model_class(model_name)
        form_class = self.get_form_class(model_name)

        if not model_class or not form_class:
            return redirect('select_table')  # Redirect to a selection page if model is invalid

        obj = get_object_or_404(model_class, pk=pk)
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('manage_' + model_class._meta.model_name)  # Redirect back to the management view
        return render(request, self.template_name, {
            'form': form,
            'object': obj,
            'model_name': model_class._meta.verbose_name.title(),
        })
