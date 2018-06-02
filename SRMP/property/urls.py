from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('create_encumbrance/', views.create_encumbrance, name='create_encumbrance'),
    path('encumbrances/', views.encumbrances, name='encumbrances'),
    path('encumbrance/', views.encumbrance, name='encumbrance'),
    path('profile/', views.profile, name='profile'),
    path('modify_encumbrance/', views.modify_encumbrance, name='modify_encumbrance'),
    path('create_debtor/', views.create_debtor, name='create_debtor'),
    path('create_prosecutor/', views.create_prosecutor, name='create_prosecutor'),
    path('prosecutors/', views.prosecutors, name='prosecutors'),
    path('delete_prosecutor/', views.delete_prosecutor, name='delete_prosecutor'),
    path('debtors/', views.debtors, name='debtors'),
    path('delete_debtor/', views.delete_debtor, name='delete_debtor'),
]
