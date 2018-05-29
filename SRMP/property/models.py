from django.db import models
from django.contrib.auth.models import User

# CharField Length
CFLEN = 45

class Notary(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, db_column='id')
    full_name = models.CharField(max_length=CFLEN, blank=True, null=True)
    licensed = models.NullBooleanField(default=False, blank=True, null=True)
    license = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'notaries'

    def __str__(self):
        return "{0}".format(self.full_name)


class ReasonDocument(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=CFLEN, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    notary_id = models.ForeignKey(Notary, models.DO_NOTHING, db_column='notary_id')
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'reason_documents'

    def __str__(self):
        return "{0} (Notary: {1})".format(self.name, self.notary_id)


class Object(models.Model):
    id = models.AutoField(primary_key=True)
    serial_number = models.CharField(max_length=CFLEN, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'objects'

    def __str__(self):
        return "SN: №{0}".format(self.serial_number)


class Address(models.Model):
    id = models.AutoField(primary_key=True)
    index = models.CharField(max_length=CFLEN, blank=True, null=True)
    city = models.CharField(max_length=CFLEN, blank=True, null=True)
    street = models.CharField(max_length=CFLEN, blank=True, null=True)
    country = models.CharField(max_length=CFLEN, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'addresses'

    def __str__(self):
        return "{0}, {1}, {2} №{3}".format(self.country, self.city, self.street, self.index)


class Debtor(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=CFLEN, blank=True, null=True)
    address_id = models.ForeignKey(Address, models.DO_NOTHING, db_column='address_id')
    options = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=CFLEN, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'debtors'

    def __str__(self):
        return "{0} ({1})".format(self.full_name, self.code)


class Prosecutor(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=CFLEN, blank=True, null=True)
    address_id = models.ForeignKey(Address, models.DO_NOTHING, db_column='address_id')
    options = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=CFLEN, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'prosecutors'

    def __str__(self):
        return "{0} ({1})".format(self.full_name, self.code)


class Encumbrance(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    prosecutor_id = models.ForeignKey(Prosecutor, models.DO_NOTHING, db_column='prosecutor_id')
    debtor_id = models.ForeignKey(Debtor, models.DO_NOTHING, db_column='debtor_id')
    notary_id = models.ForeignKey(Notary, models.DO_NOTHING, db_column='notary_id')
    reason_document = models.ForeignKey(ReasonDocument, models.DO_NOTHING, db_column='reason_document')
    encumbrance_kind = models.CharField(max_length=CFLEN, blank=True, null=True)
    encumbrance_type = models.CharField(max_length=CFLEN, blank=True, null=True)
    debt_amount = models.CharField(max_length=CFLEN, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    object_id = models.ForeignKey(Object, models.DO_NOTHING, db_column='object_id')
    hashcode = models.CharField(max_length=100, blank=True, null=True, default="secret")

    class Meta:
        managed = True
        db_table = 'encumbrances'

    def __str__(self):
        return "Kind: {0}, Type: {1}".format(self.encumbrance_kind, self.encumbrance_type)
