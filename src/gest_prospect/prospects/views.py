from io import StringIO

from django.contrib import messages
from django.core.management import call_command
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ImportProspectsForm, ProspectStatusForm
from .models import Prospect


def prospect_list(request):
    prospects = Prospect.objects.all()
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        prospects = prospects.filter(
            Q(name__icontains=search) | Q(phone__icontains=search) | Q(address__icontains=search)
        )
    if status:
        prospects = prospects.filter(status=status)

    context = {
        "prospects": prospects,
        "import_form": ImportProspectsForm(),
        "status_choices": Prospect.Status.choices,
        "selected_status": status,
        "search": search,
        "total": Prospect.objects.count(),
        "new_count": Prospect.objects.filter(status=Prospect.Status.NEW).count(),
        "contacted_count": Prospect.objects.exclude(status=Prospect.Status.NEW).count(),
    }
    return render(request, "prospects/prospect_list.html", context)


@require_POST
def import_prospects(request):
    form = ImportProspectsForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Confira o termo de busca e o limite informado.")
        return redirect("prospects:list")

    output = StringIO()
    try:
        call_command(
            "import_prospects",
            form.cleaned_data["query"],
            limit=form.cleaned_data["limit"],
            stdout=output,
        )
    except Exception as error:
        messages.error(request, str(error))
    else:
        messages.success(request, output.getvalue().strip())
    return redirect("prospects:list")


@require_POST
def update_status(request, pk):
    prospect = get_object_or_404(Prospect, pk=pk)
    form = ProspectStatusForm(request.POST, instance=prospect)
    if not form.is_valid():
        return HttpResponseBadRequest("Status inválido.")

    prospect = form.save(commit=False)
    if prospect.status == Prospect.Status.CONTACTED and prospect.contacted_at is None:
        prospect.contacted_at = timezone.now()
    prospect.save(update_fields=("status", "contacted_at", "updated_at"))
    messages.success(request, f"Status de {prospect.name} atualizado.")
    return redirect("prospects:list")


@require_POST
def open_whatsapp(request, pk):
    prospect = get_object_or_404(Prospect, pk=pk)
    if not prospect.whatsapp_url:
        messages.error(request, f"{prospect.name} não possui telefone cadastrado.")
        return redirect("prospects:list")

    if prospect.status == Prospect.Status.NEW:
        prospect.status = Prospect.Status.CONTACTED
    if prospect.contacted_at is None:
        prospect.contacted_at = timezone.now()
    prospect.save(update_fields=("status", "contacted_at", "updated_at"))
    return redirect(prospect.whatsapp_url)
