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
        d_string = [int(ds) for ds in d_string]
        d = date(d_string[0], d_string[1], d_string[2])
        d_string = encumbrance['deadline'].split("-")
        d_string = [int(ds) for ds in d_string]
        dd = date(d_string[0], d_string[1], d_string[2])
        prosecutor = self.read_prosecutors(encumbrance['prosecutor_id'])
        debtor = self.read_debtors(encumbrance['debtor_id'])
        rd = self.read_reason_documents(encumbrance['reason_document_id'])
        obj = self.read_objects(encumbrance['object_id'])
        print(encumbrance['notary_id'])
        notary = self.read_notaries(encumbrance['notary_id'])
        enc = Encumbrance(date=d, prosecutor_id=prosecutor,
                          debtor_id=debtor, notary_id=notary,
                          reason_document=rd, encumbrance_kind=encumbrance['encumbrance_kind'],
                          encumbrance_type=encumbrance['encumbrance_type'], debt_amount=encumbrance['debt_amount'],
                          deadline=dd, object_id=obj, hashcode="",)
        enc.save()
        enc_id = enc.id
        enc.hashcode = hashlib.sha256(SALT.encode() + str(enc_id).encode()).hexdigest()
        enc.save()
        return enc_id

    def read_encumbrances(self, query=None, single=False):
        if query:
            try:
                query = int(query)
            except:
                pass

            if isinstance(query, int):
                if query > 0:
                    return Encumbrance.objects.filter(id=query).values()
                else:
                    return None
            elif not single:
                return Encumbrance.objects.filter(encumbrance_type=query).values()
            else:
                return None
        elif not single:
            return Encumbrance.objects.values('id', 'encumbrance_type', 'encumbrance_kind',
                                              'date', 'notary_id__full_name')
        else:
            return None

    def read_prosecutors(self, id=None):
        if id:
            return Prosecutor.objects.get(id=id)
        else:
            return Prosecutor.objects.values('id', 'full_name')

    def read_debtors(self, id=None):
        if id:
            return Debtor.objects.get(id=id)
        else:
            return Debtor.objects.values('id', 'full_name')

    def read_reason_documents(self, id=None):
        if id:
            return ReasonDocument.objects.get(id=id)
        else:
            return ReasonDocument.objects.values('id', 'name')

    def read_objects(self, id=None):
        if id:
            return Object.objects.get(id=id)
        else:
            return Object.objects.values('id', 'serial_number')

    def read_notaries(self, id=None):
        if id:
            return Notary.objects.get(id_id=id)
        else:
            # TODO
            return None

    def read_encumbrances_by_notary(self, notary_id):
        return Encumbrance.objects.filter(notary_id=notary_id).values()
