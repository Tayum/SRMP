from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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

        # redirect to page with login
        return render(request, 'property/encumbrances.html')
    else:
        return render(request, 'property/signup.html')


@login_required
def create_encumbrance(request):
    if request.method == "POST":
        enc = dict()
        # (construct encumbrance dictionary from the values from form)
        pm.create_encumbrance(enc)

        # redirect to page with all encumbrances
        encumbrances = pm.read_encumbrances()
        return render(request, 'property/encumbrances.html',
                      {
                          "encumbrances": encumbrances,
                      })
    else:
        return render(request, 'property/create_encumbrance.html')


def encumbrances(request):
    encs = pm.read_encumbrances()
    return render(request, 'property/encumbrances.html',
                  {
                      "encumbrances": encs,
                  })


def encumbrance(request):
    id = int(request.GET.get('id', -1))
    enc = pm.read_encumbrance(id)

    return render(request, 'property/encumbrance.html',
                  {
                      "encumbrance": enc,
                  })
