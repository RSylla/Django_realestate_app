"""
URL configuration for realestate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from statistics_app.views import TransactionQueryView, load_cities, index, \
TableSelectionView, ManageModelView, EditModelView
from django.contrib.auth import views as auth_views
from statistics_app.models import Maakond, Linn, Kinnisvara, Klient, Maakler, Tehing
from statistics_app.forms import MaakondForm, LinnForm, KinnisvaraForm, KlientForm, MaaklerForm, TehingForm


urlpatterns = [
    path('', index, name='index'),
    path('transaction-query/', TransactionQueryView.as_view(), name='transaction_query'),
    path('admin/', admin.site.urls),
    path('ajax/load-cities/', load_cities, name='ajax_load_cities'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('select-table/', TableSelectionView.as_view(), name='select_table'),
    path('manage-maakond/', ManageModelView.as_view(model_class=Maakond, form_class=MaakondForm), name='manage_maakond'),
    path('manage-linn/', ManageModelView.as_view(model_class=Linn, form_class=LinnForm), name='manage_linn'),
    path('manage-kinnisvara/', ManageModelView.as_view(model_class=Kinnisvara, form_class=KinnisvaraForm), name='manage_kinnisvara'),
    path('manage-klient/', ManageModelView.as_view(model_class=Klient, form_class=KlientForm), name='manage_klient'),
    path('manage-maakler/', ManageModelView.as_view(model_class=Maakler, form_class=MaaklerForm), name='manage_maakler'),
    path('manage-tehing/', ManageModelView.as_view(model_class=Tehing, form_class=TehingForm), name='manage_tehing'),
    path('edit/<str:model_name>/<int:pk>/', EditModelView.as_view(), name='edit_entry'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
