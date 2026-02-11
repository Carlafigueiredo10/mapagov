"""
PDF sob demanda version-aware para o catálogo de POPs.

GET /api/areas/{slug}/pops/{codigo}/pdf/
GET /api/areas/{slug}/pops/{codigo}/pdf/?v=3

Fluxo:
  1. Resolve POP por area slug + codigo_processo
  2. Decide fonte de dados (PopVersion.payload ou POP corrente)
  3. Normaliza via preparar_pop_para_pdf()
  4. Gera PDF via PDFGenerator.gerar_pop_completo()
  5. Retorna HttpResponse(application/pdf)
"""
import logging
import os
import tempfile

from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view

from processos.export.pop_adapter import preparar_pop_para_pdf
from processos.models import Area, POP, PopVersion
from processos.utils import PDFGenerator

logger = logging.getLogger(__name__)


def _resolver_pop_e_area(slug, codigo):
    """Resolve POP por area slug + codigo_processo (inclui sub-areas)."""
    area = Area.objects.filter(slug=slug, ativo=True).first()
    if not area:
        return None, None, 'Área não encontrada.'

    area_ids = [area.id] + list(area.subareas.values_list('id', flat=True))
    pop = POP.objects.filter(
        area_id__in=area_ids,
        codigo_processo=codigo,
        is_deleted=False,
    ).first()

    if not pop:
        return area, None, 'POP não encontrado.'

    return area, pop, None


def _dados_para_pdf(pop, version_payload=None, area=None, versao_label=None, published_at=None):
    """
    Monta dict de dados no formato esperado pelo PDFGenerator.
    Se version_payload for fornecido, usa ele; senão usa POP corrente.
    """
    if version_payload:
        dados = dict(version_payload)
    else:
        dados = pop.get_dados_completos()

    # Garantir area como dict (renderer espera .get('nome'))
    if area and not isinstance(dados.get('area'), dict):
        dados['area'] = {'codigo': area.codigo, 'nome': area.nome_curto}
    elif area:
        dados.setdefault('area', {})
        dados['area'].setdefault('codigo', area.codigo)
        dados['area'].setdefault('nome', area.nome_curto)

    # Versao e data
    if versao_label:
        dados['versao'] = str(versao_label)
    elif not dados.get('versao'):
        dados['versao'] = str(pop.versao)

    if published_at:
        dados['data_aprovacao'] = published_at.strftime('%d/%m/%Y')

    return preparar_pop_para_pdf(dados)


@api_view(['GET'])
def gerar_pdf_catalogo(request, slug, codigo):
    """
    GET /api/areas/{slug}/pops/{codigo}/pdf/
    GET /api/areas/{slug}/pops/{codigo}/pdf/?v=3

    Gera PDF sob demanda a partir de:
    - ?v=N  → PopVersion com versao=N
    - sem v → PopVersion is_current=True (se existir), senão POP corrente
    """
    area, pop, erro = _resolver_pop_e_area(slug, codigo)
    if erro:
        status = 404
        return JsonResponse({'error': erro}, status=status)

    # Decidir fonte de dados
    v_param = request.query_params.get('v')
    version = None
    version_payload = None
    versao_label = None
    published_at = None

    if v_param:
        try:
            v_int = int(v_param)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Parâmetro v deve ser inteiro.'}, status=400)

        version = PopVersion.objects.filter(pop=pop, versao=v_int).first()
        if not version:
            return JsonResponse(
                {'error': f'Versão {v_int} não encontrada para este POP.'},
                status=404,
            )
        version_payload = version.payload
        versao_label = version.versao
        published_at = version.published_at
    else:
        # Preferir versão publicada atual
        version = PopVersion.objects.filter(pop=pop, is_current=True).first()
        if version:
            version_payload = version.payload
            versao_label = version.versao
            published_at = version.published_at

    # Preparar dados
    dados = _dados_para_pdf(
        pop,
        version_payload=version_payload,
        area=area,
        versao_label=versao_label,
        published_at=published_at,
    )

    if not dados.get('nome_processo'):
        return JsonResponse(
            {'error': 'POP sem nome_processo — não é possível gerar PDF.'},
            status=400,
        )

    # Gerar PDF em diretório temporário
    v_suffix = f'v{versao_label}' if versao_label else f'v{pop.versao}'
    nome_arquivo = f'POP_{slug}_{codigo.replace(".", "-")}_{v_suffix}.pdf'

    generator = PDFGenerator()
    tmp_dir = tempfile.mkdtemp(prefix='mapagov_pdf_')
    tmp_path = os.path.join(tmp_dir, nome_arquivo)

    # PDFGenerator salva em media/pdfs/ por padrão.
    # Geramos lá e lemos de volta para streaming.
    pdf_path = generator.gerar_pop_completo(dados, nome_arquivo)

    if not pdf_path or not os.path.exists(pdf_path):
        return JsonResponse(
            {'error': 'Erro ao gerar PDF. Verifique os logs do servidor.'},
            status=500,
        )

    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
    finally:
        # Limpar arquivo gerado (é sob demanda, não precisa persistir)
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    response['Content-Length'] = len(pdf_bytes)

    logger.info(
        f"[catalogo_pdf] PDF gerado: {nome_arquivo} "
        f"({len(pdf_bytes) / 1024:.1f} KB, version={'v' + str(versao_label) if versao_label else 'corrente'})"
    )

    return response
