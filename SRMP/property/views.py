from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


from .postgres_manage import PostgresManage

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

        pm.create_notary(notary)

        # redirect to profile
        return render(request, 'property/profile.html')
    else:
        return render(request, 'property/signup.html')


@login_required
def create_encumbrance(request):
    if request.method == "POST":
        enc = dict()
        enc['date'] = str(request.POST.get('date', "1900-01-01"))
        enc['prosecutor_id'] = request.POST.get('prosecutor', -1)
        enc['debtor_id'] = request.POST.get('debtor', -1)
        enc['notary_id'] = request.POST.get('notary', -1)
        enc['reason_document_id'] = request.POST.get('reason_document', -1)
        enc['encumbrance_kind'] = request.POST.get('encumbrance_kind', "")
        enc['encumbrance_type'] = request.POST.get('encumbrance_type', "")
        enc['debt_amount'] = request.POST.get('debt_amount', "0")
        enc['deadline'] = str(request.POST.get('deadline', "1900-01-01"))
        enc['object_id'] = request.POST.get('object', -1)

        # (construct encumbrance dictionary from the values from form)
        enc_id = pm.create_encumbrance(enc)
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
            prosecutors = pm.read_prosecutors()
            prosecutors = [{
                "id": p['id'],
                "value": p['full_name'],
            } for p in prosecutors]
            debtors = pm.read_debtors()
            debtors = [{
                "id": d['id'],
                "value": d['full_name'],
            } for d in debtors]
            rds = pm.read_reason_documents()
            rds = [{
                "id": rd['id'],
                "value": rd['name'],
            } for rd in rds]
            objs = pm.read_objects()
            objs = [{
                "id": o['id'],
                "value": o['serial_number'],
            } for o in objs]
            return render(request, 'property/create_encumbrance.html', {
                "prosecutors": prosecutors,
                "debtors": debtors,
                "reason_documents": rds,
                "objects": objs,
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
        enc_id = request.POST.get('encumbrance_id', -1)
        enc = dict()
        enc['date'] = str(request.POST.get('date', "1900-01-01"))
        enc['prosecutor_id'] = request.POST.get('prosecutor', -1)
        enc['debtor_id'] = request.POST.get('debtor', -1)
        enc['reason_document_id'] = request.POST.get('reason_document', -1)
        enc['encumbrance_kind'] = request.POST.get('encumbrance_kind', "")
        enc['encumbrance_type'] = request.POST.get('encumbrance_type', "")
        enc['debt_amount'] = request.POST.get('debt_amount', "0")
        enc['deadline'] = str(request.POST.get('deadline', "1900-01-01"))
        enc['object_id'] = request.POST.get('object', -1)

        pm.modify_encumbrance(enc_id, enc)
        return redirect("/property/encumbrance?id=" + enc_id)
    else:
        id = request.GET.get('id', -1)
        enc = pm.read_encumbrance_for_modifying(id)
        enc = enc[0] if enc else None
        if enc:
            prosecutors = pm.read_prosecutors()
            prosecutors = [{
                "id": p['id'],
                "value": p['full_name'],
            } for p in prosecutors]
            debtors = pm.read_debtors()
            debtors = [{
                "id": d['id'],
                "value": d['full_name'],
            } for d in debtors]
            rds = pm.read_reason_documents()
            rds = [{
                "id": rd['id'],
                "value": rd['name'],
            } for rd in rds]
            objs = pm.read_objects()
            objs = [{
                "id": o['id'],
                "value": o['serial_number'],
            } for o in objs]
            enc['date'] = str(enc['date'])
            enc['deadline'] = str(enc['deadline'])
            return render(request, 'property/modify_encumbrance.html', {
                "encumbrance": enc,
                "prosecutors": prosecutors,
                "debtors": debtors,
                "reason_documents": rds,
                "objects": objs,
            })
        else:
            return render(request, 'property/index.html')
