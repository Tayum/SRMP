from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


from .postgres_manage import PostgresManage
from .models import Debtor, Prosecutor, Encumbrance

pm = PostgresManage()


# Create your views here.
def index(request):
    return render(request, 'property/index.html')


def signup(request):
    if request.method == "POST":
        # (construct notary dictionary from the values from form)
        notary = dict()
        notary['full_name'] = request.POST.get('name')
        notary['login'] = request.POST.get('login')
        notary['pwd'] = request.POST.get('pwd')
        notary['license'] = request.POST.get('doc')

        notary = pm.create_notary(notary)

        # redirect to profile
        return render(request, 'property/profile.html',
                      {
                            "notary": notary,
                            "encumbrances": None,
                      })
    else:
        return render(request, 'property/signup.html')


@login_required
def create_encumbrance(request):
    if request.method == "POST":
        enc = dict()
        enc['date'] = str(request.POST.get('date', "1900-01-01"))
        enc['prosecutor_id'] = int(request.POST.get('prosecutor_id', -1))
        enc['debtor_id'] = int(request.POST.get('debtor_id', -1))
        enc['notary_id'] = int(request.POST.get('notary', -1))
        # Reason Document
        rd = {
            "name": request.POST.get('reason_document_name', ""),
            "date": str(request.POST.get('reason_document_date', "1900-01-01")),
            "description": request.POST.get('reason_document_description', ""),
        }

        enc['encumbrance_kind'] = request.POST.get('encumbrance_kind', "")
        enc['encumbrance_type'] = request.POST.get('encumbrance_type', "")
        enc['debt_amount'] = request.POST.get('debt_amount', "0")
        enc['deadline'] = str(request.POST.get('deadline', "1900-01-01"))
        # Object
        obj = {
            "serial_number": request.POST.get('object_serial_number', ""),
            "description": request.POST.get('object_description', ""),
        }

        enc_id = pm.create_encumbrance(enc, obj, rd)
        info = pm.read_encumbrances(enc_id, True)
        if info:
            return render(request, 'property/encumbrance.html',
                          {
                              "info": True,
                              "encumbrance": info['encumbrance'],
                              "prosecutor": info['prosecutor'],
                              "prosecutor_addr": info['prosecutor_addr'],
                              "debtor": info['debtor'],
                              "debtor_addr": info['debtor_addr'],
                              "notary": info['notary'],
                              "reason_document": info['reason_document'],
                              "object": info['object'],
                          })
        else:
            return render(request, 'property/encumbrance.html',
                          {
                              "info": False,
                          })
    else:
        if not request.user.is_superuser and request.user.notary.licensed:
            prosecs = pm.read_prosecutors()
            prosecs = [{
                "id": p['id'],
                "code": p['code'],
            } for p in prosecs]
            debts = pm.read_debtors()
            debts = [{
                "id": d['id'],
                "code": d['code'],
            } for d in debts]
            print(debtors)
            return render(request, 'property/create_encumbrance.html', {
                "prosecutors": prosecs,
                "debtors": debts,
            })
        else:
            return render(request, 'property/index.html')


def encumbrances(request):
    try:
        query = request.GET['search']
    except KeyError:
        query = None
    if query is None:
        encs = pm.read_encumbrances()
    else:
        found_encs = pm.read_encumbrances(query)
        encs = found_encs if found_encs else None

    return render(request, 'property/encumbrances.html',
                  {
                      "encumbrances": encs,
                  })


def encumbrance(request):
    id = request.GET.get('id', -1)
    info = pm.read_encumbrances(id, True)
    info = info if info else None
    if info:
        return render(request, 'property/encumbrance.html',
                      {
                          "info": True,
                          "encumbrance": info['encumbrance'],
                          "prosecutor": info['prosecutor'],
                          "prosecutor_addr": info['prosecutor_addr'],
                          "debtor": info['debtor'],
                          "debtor_addr": info['debtor_addr'],
                          "notary": info['notary'],
                          "reason_document": info['reason_document'],
                          "object": info['object'],
                      })
    else:
        return render(request, 'property/encumbrance.html',
                      {
                          "info": False,
                      })


@login_required
def profile(request):
    current_user = request.user
    if current_user.is_superuser:
        return redirect("/admin/")
    else:
        # get encumbrances that are affiliated with this notary
        encs = pm.read_encumbrances_by_notary(current_user.id)
        encs = [{
            "id": e['id'],
            "hashcode": e['hashcode'],
        } for e in encs] if encs else None
        return render(request, 'property/profile.html',
                      {
                            "notary": current_user.notary,
                            "encumbrances": encs,
                      })


@login_required
def modify_encumbrance(request):
    if request.method == "POST":
        if request.user.is_superuser:
            return redirect("/property/")
        enc_id = request.POST.get('encumbrance_id', -1)
        enc = dict()
        enc['prosecutor_id'] = int(request.POST.get('prosecutor_id', -1))
        enc['debtor_id'] = int(request.POST.get('debtor_id', -1))
        rd = {
            "name": request.POST.get("reason_document_name", ""),
            "description": request.POST.get("reason_document_description", ""),
        }
        enc['encumbrance_kind'] = request.POST.get('encumbrance_kind', "")
        enc['encumbrance_type'] = request.POST.get('encumbrance_type', "")
        enc['debt_amount'] = request.POST.get('debt_amount', "0")
        enc['deadline'] = str(request.POST.get('deadline', "1900-01-01"))
        obj = {
            "serial_number": request.POST.get("object_serial_number", ""),
            "description": request.POST.get("object_description", ""),
        }

        pm.modify_encumbrance(enc_id, enc, obj, rd)
        return redirect("/property/profile/")
    else:
        if request.user.is_superuser:
            return redirect("/property/")
        id = request.GET.get('id', -1)
        enc = pm.read_encumbrance_for_modifying(id)
        enc = enc[0] if enc else None
        print(enc)
        if enc and enc['notary_id_id'] == request.user.id:
            rd = pm.read_reason_documents(enc['reason_document_id'])
            obj = pm.read_objects(enc['object_id_id'])
            prosecs = pm.read_prosecutors()
            prosecs = [{
                "id": p['id'],
                "code": p['code'],
            } for p in prosecs]
            debts = pm.read_debtors()
            debts = [{
                "id": d['id'],
                "code": d['code'],
            } for d in debts]
            enc['date'] = str(enc['date'])
            enc['deadline'] = str(enc['deadline'])
            return render(request, 'property/modify_encumbrance.html', {
                "current_prosecutor_code": pm.read_prosecutors(enc['prosecutor_id_id']).code,
                "current_debtor_code": pm.read_debtors(enc['debtor_id_id']).code,
                "encumbrance": enc,
                "reason_document": rd,
                "object": obj,
                "prosecutors": prosecs,
                "debtors": debts,
            })
        else:
            return render(request, 'property/index.html')


@login_required
def create_debtor(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")
    if request.method == "POST":
        debtor = dict()
        debtor['full_name'] = str(request.POST.get('full_name', ""))
        debtor['options'] = request.POST.get('options', "")
        debtor['code'] = request.POST.get('code', "")
        address = {
            "index": request.POST.get('address_index', ""),
            "city": request.POST.get('address_city', ""),
            "street": request.POST.get('address_street', ""),
            "country": request.POST.get('address_country', ""),
        }

        debtor_id = pm.create_debtor(debtor, address)
        return redirect("/property/")
    else:
        return render(request, 'property/create_debtor.html')


@login_required
def create_prosecutor(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")
    if request.method == "POST":
        prosecutor = dict()
        prosecutor['full_name'] = str(request.POST.get('full_name', ""))
        prosecutor['options'] = request.POST.get('options', "")
        prosecutor['code'] = request.POST.get('code', "")
        address = {
            "index": request.POST.get('address_index', ""),
            "city": request.POST.get('address_city', ""),
            "street": request.POST.get('address_street', ""),
            "country": request.POST.get('address_country', ""),
        }

        prosecutor_id = pm.create_prosecutor(prosecutor, address)
        return redirect("/property/")
    else:
        return render(request, 'property/create_prosecutor.html')


# TODO REDO
@login_required
def debtors(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")

    try:
        query = request.GET['query']
    except KeyError:
        query = None

    if query is None:
        debts = Debtor.objects.all()
    else:
        debts = Debtor.objects.filter(code=query)

    return render(request, 'property/debtors.html',
                  {
                      "debtors": debts,
                  })


# TODO REDO
@login_required
def prosecutors(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")

    try:
        query = request.GET['query']
    except KeyError:
        query = None

    if query is None:
        prosecs = Prosecutor.objects.all()
    else:
        prosecs = Prosecutor.objects.filter(code=query)

    return render(request, 'property/prosecutors.html',
                  {
                      "prosecutors": prosecs,
                  })


# TODO REDO
@login_required
def delete_debtor(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")

    if request.method == "POST":
        id = int(request.POST['target'])
        if Encumbrance.objects.filter(debtor_id__id=id).count() is not 0:
            pass
        else:
            Debtor.objects.get(pk=id).delete()

    return redirect('/property/debtors/')


# TODO REDO
@login_required
def delete_prosecutor(request):
    if request.user.is_superuser or not request.user.notary.licensed:
        return redirect("/property/")
    if request.method == "POST":
        id = int(request.POST['target'])
        if Encumbrance.objects.filter(prosecutor_id__id=id).count() is not 0:
            pass
        else:
            Prosecutor.objects.get(id=id).delete()

    return redirect('/property/prosecutors/')

