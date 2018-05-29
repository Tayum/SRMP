import uuid
import hashlib

from .models import *
from django.apps import apps
from django.contrib.auth.models import User

SALT = "SALT"

class PostgresManage:
    def create_notary(self, notary):
        # notary is dict with such keys:
        # * full_name
        # * license
        # * login
        # * pwd
        user = User.objects.create_user(username=notary['login'], password=notary['pwd'])
        notary = Notary(id=user, full_name=notary['full_name'], licensed=False, license=notary['license'])
        notary.save()

    def create_encumbrance(self, encumbrance):
        # encumbrance
        enc = Encumbrance(**encumbrance)
        enc.save()
        enc_id = enc.id
        enc.hashcode = hashlib.sha256(SALT.encode() + str(enc_id).encode()).hexdigest() + ':' + SALT
        enc.save()

    def read_encumbrances(self):
        return Encumbrance.objects.values_list()

    def read_encumbrance(self, id):
        # JOIN example:
        # .values_list(..., 'notary_id__full_name', ...)
        return Encumbrance.objects.filter(id=id).values_list()
