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
        return notary

    def create_encumbrance(self, encumbrance, ob, reason_doc):
        # encumbrance
        d_string = encumbrance['date'].split("-")
        d_string = [int(ds) for ds in d_string]
        d = date(d_string[0], d_string[1], d_string[2])
        d_string = encumbrance['deadline'].split("-")
        d_string = [int(ds) for ds in d_string]
        dd = date(d_string[0], d_string[1], d_string[2])
        prosecutor = self.read_prosecutors(encumbrance['prosecutor_id'])
        debtor = self.read_debtors(encumbrance['debtor_id'])

        reason_document_date_string = reason_doc['date'].split("-")
        reason_document_date_string = [int(rdds) for rdds in reason_document_date_string]
        reason_document_date = date(reason_document_date_string[0], reason_document_date_string[1], reason_document_date_string[2])
        reason_document = ReasonDocument(name=reason_doc['name'], description=reason_doc['description'],
                                         date=reason_document_date)
        reason_document.save()

        obj = Object(serial_number=ob['serial_number'], description=ob['description'])
        obj.save()

        notary = self.read_notaries(encumbrance['notary_id'])
        enc = Encumbrance(date=d, prosecutor_id=prosecutor,
                          debtor_id=debtor, notary_id=notary,
                          reason_document=reason_document, encumbrance_kind=encumbrance['encumbrance_kind'],
                          encumbrance_type=encumbrance['encumbrance_type'], debt_amount=encumbrance['debt_amount'],
                          deadline=dd, object_id=obj, checked=False, hashcode="",)
        enc.save()
        enc_id = enc.id
        enc.hashcode = hashlib.sha256(SALT.encode() + str(enc_id).encode()).hexdigest()
        enc.save()
        return enc_id

    def read_encumbrances(self, query=None, detailed_info=False):
        if query:
            try:
                query = int(query)
            except:
                pass

            if isinstance(query, int):
                if query > 0 and detailed_info:
                    enc = Encumbrance.objects.filter(id=query).values()
                    enc = enc[0]
                    prosecutor = enc['prosecutor_id_id']
                    prosecutor = self.read_prosecutors(prosecutor)
                    prosecutor_addr = prosecutor.address_id
                    debtor = enc['debtor_id_id']
                    debtor = self.read_debtors(debtor)
                    debtor_addr = debtor.address_id
                    notary = enc['notary_id_id']
                    notary = self.read_notaries(notary)
                    reason_document = enc['reason_document_id']
                    reason_document = self.read_reason_documents(reason_document)
                    obj = enc['object_id_id']
                    obj = self.read_objects(obj)
                    if enc['checked']:
                        return {
                            "encumbrance": enc,
                            "prosecutor": prosecutor,
                            "prosecutor_addr": prosecutor_addr,
                            "debtor": debtor,
                            "debtor_addr": debtor_addr,
                            "notary": notary,
                            "reason_document": reason_document,
                            "object": obj,
                        }
                    else:
                        return None
                elif query > 0 and not detailed_info:
                    return Encumbrance.objects.filter(id=query).values()
                else:
                    return None
            elif not detailed_info:
                return Encumbrance.objects.filter(encumbrance_type=query).values()
            else:
                return None
        elif not detailed_info:
            return Encumbrance.objects.values('id', 'encumbrance_type', 'encumbrance_kind',
                                              'date', 'notary_id__full_name')
        else:
            return None

    def read_prosecutors(self, id=None):
        if id:
            return Prosecutor.objects.get(id=id)
        else:
            return Prosecutor.objects.values('id', 'code')

    def read_debtors(self, id=None):
        if id:
            return Debtor.objects.get(id=id)
        else:
            return Debtor.objects.values('id', 'code')

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

    def read_addresses(self, id=None):
        if id:
            return Address.objects.get(id=id)
        else:
            # TODO
            return None

    def read_encumbrances_by_notary(self, notary_id):
        return Encumbrance.objects.filter(notary_id=notary_id).values()

    def read_encumbrance_for_modifying(self, enc_id):
            try:
                enc_id = int(enc_id)
            except:
                enc_id = -1
                return None
            if enc_id > 0:
                enc = Encumbrance.objects.filter(id=enc_id).values()
                return enc
            else:
                return None

    def modify_encumbrance(self, enc_id, new_values_enc, new_values_obj, new_values_rd):
        try:
            enc = Encumbrance.objects.filter(id=enc_id).get()
        except:
            return None

        # prosecutor
        prosecutor = self.read_prosecutors(new_values_enc['prosecutor_id'])
        enc.prosecutor_id = prosecutor

        # debtor
        debtor = self.read_debtors(new_values_enc['debtor_id'])
        enc.debtor_id = debtor

        # reason document
        enc.reason_document.name = new_values_rd['name']
        enc.reason_document.description = new_values_rd['description']
        enc.reason_document.save()

        enc.encumbrance_kind = new_values_enc['encumbrance_kind']
        enc.encumbrance_type = new_values_enc['encumbrance_type']
        enc.debt_amount = new_values_enc['debt_amount']
        enc.deadline = new_values_enc['deadline']

        # object
        enc.object_id.serial_number = new_values_obj['serial_number']
        enc.object_id.description = new_values_obj['description']
        enc.object_id.save()

        enc.save()

    def create_debtor(self, debt, addr):
        address = Address(index=addr['index'], city=addr['city'],
                          country=addr['country'], street=addr['street'])
        address.save()

        debtor = Debtor(full_name=debt['full_name'], code=debt['code'],
                        options=debt['options'], address_id=address)
        debtor.save()

    def create_prosecutor(self, pros, addr):
        address = Address(index=addr['index'], city=addr['city'],
                          country=addr['country'], street=addr['street'])
        address.save()

        prosecutor = Prosecutor(full_name=pros['full_name'], code=pros['code'],
                                options=pros['options'], address_id=address)
        prosecutor.save()
