import uuid
import hashlib

from .models import *
from django.apps import apps
from django.contrib.auth.models import User
from datetime import date

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
        # TODO
        # encumbrance
        d_string = encumbrance['date'].split("-")
        d = date(d_string[0], d_string[1], d_string[2])
        d_string = encumbrance['deadline'].split("-")
        dd = date(d_string[0], d_string[1], d_string[2])
        enc = Encumbrance(date=d, prosecutor_id=encumbrance['prosecutor_id'],
                          debtor_id=encumbrance['debtor_id'], notary_id=encumbrance['notary_id'],
                          reason_document=encumbrance['reason_document_id'], encumbrance_kind=encumbrance['encumbrance_kind'],
                          encumbrance_type=encumbrance['encumbrance_type'], debt_amount=encumbrance['debt_amount'],
                          deadline=dd, object_id=encumbrance['object_id'], hashcode="",)
        enc.save()
        enc_id = enc.id
        enc.hashcode = hashlib.sha256(SALT.encode() + str(enc_id).encode()).hexdigest() + ':' + SALT
        enc.save()
        return enc_id

    def read_encumbrances(self, query=None, single=False):
        # JOIN example:
        # .values_list(..., 'notary_id__full_name', ...)
        if query:
            try:
                query = int(query)
            except:
                pass

            if isinstance(query, int):
                if query > 0:
                    return Encumbrance.objects.filter(id=query).values_list()
                else:
                    return None
            elif not single:
                return Encumbrance.objects.filter(encumbrance_type=query).values_list()
            else:
                return None
        elif not single:
            return Encumbrance.objects.values_list()
        else:
            return None

    def read_encumbrances_by_notary(self, notary_id):
        return Encumbrance.objects.filter(notary_id=notary_id).values_list()
