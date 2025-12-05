from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.core.mixins import ConsultorRequiredMixin
from apps.proyectos.models import Proyecto, ProveedorProyecto
from apps.empresas.models import EmpresaAncla
from .models import ReporteGenerado


class ReporteListView(ConsultorRequiredMixin, ListView):
    model = ReporteGenerado
    template_name = 'reportes/lista.html'
    context_object_name = 'reportes'
    paginate_by = 20


def generar_reporte_proveedor(request, pk):
    """Generar reporte de avance de un proveedor."""
    proveedor_proyecto = get_object_or_404(ProveedorProyecto, pk=pk)

    # TODO: Implementar generación de PDF con ReportLab o WeasyPrint
    # Por ahora, retornamos un placeholder

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_proveedor_{pk}.pdf"'

    return response


def generar_reporte_proyecto(request, pk):
    """Generar reporte consolidado del proyecto."""
    proyecto = get_object_or_404(Proyecto, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_proyecto_{proyecto.codigo}.pdf"'

    return response


def generar_reporte_ejecutivo(request, pk):
    """Generar reporte ejecutivo para empresa ancla."""
    empresa = get_object_or_404(EmpresaAncla, pk=pk)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_ejecutivo_{empresa.nit}.pdf"'

    return response


def descargar_reporte(request, pk):
    """Descargar un reporte generado."""
    reporte = get_object_or_404(ReporteGenerado, pk=pk)
    return FileResponse(reporte.archivo.open(), as_attachment=True, filename=reporte.archivo.name)
