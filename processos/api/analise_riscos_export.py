"""
Exportacao de Analise de Riscos para Word e PDF

Endpoints:
- GET /api/analise-riscos/<id>/exportar/?formato=docx
- GET /api/analise-riscos/<id>/exportar/?formato=pdf
"""
import io
import logging
from datetime import datetime
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from processos.models_analise_riscos import AnaliseRiscos
from processos.infra.rate_limiting import rate_limit_user

logger = logging.getLogger(__name__)


def get_orgao_id(request):
    """Extrai orgao_id do usuario (RLS)"""
    import uuid
    if hasattr(request.user, "orgao_id"):
        return request.user.orgao_id
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


# =============================================================================
# GERACAO WORD (python-docx)
# =============================================================================

def gerar_docx(analise: AnaliseRiscos) -> io.BytesIO:
    """Gera documento Word com a analise de riscos"""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT

    doc = Document()

    # Estilos
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)

    # === CABECALHO ===
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run('MINISTERIO DA GESTAO E DA INOVACAO EM SERVICOS PUBLICOS')
    run.bold = True
    run.font.size = Pt(12)

    subheader = doc.add_paragraph()
    subheader.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subheader.add_run('Secretaria de Gestao de Pessoas - DECIPEX')
    run.font.size = Pt(11)

    doc.add_paragraph()

    # === TITULO ===
    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = titulo.add_run('RELATORIO DE ANALISE DE RISCOS')
    run.bold = True
    run.font.size = Pt(14)

    doc.add_paragraph()

    # === INFORMACOES GERAIS ===
    doc.add_heading('1. Informacoes Gerais', level=1)

    contexto = analise.contexto_estruturado or {}
    bloco_a = contexto.get('bloco_a', {})

    table = doc.add_table(rows=5, cols=2)
    table.style = 'Table Grid'

    dados = [
        ('Objeto', bloco_a.get('nome_objeto', 'Nao informado')),
        ('Tipo', analise.tipo_origem or 'Nao informado'),
        ('Area Responsavel', bloco_a.get('area_responsavel', 'Nao informado')),
        ('Data da Analise', analise.criado_em.strftime('%d/%m/%Y')),
        ('Status', analise.status or 'Nao informado'),
    ]

    for i, (label, valor) in enumerate(dados):
        row = table.rows[i]
        row.cells[0].text = label
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[1].text = str(valor)

    doc.add_paragraph()

    # === CONTEXTO ===
    doc.add_heading('2. Contexto', level=1)

    if bloco_a.get('objetivo_finalidade'):
        doc.add_paragraph(f"Objetivo/Finalidade: {bloco_a.get('objetivo_finalidade')}")

    if bloco_a.get('descricao_escopo'):
        doc.add_paragraph(f"Escopo: {bloco_a.get('descricao_escopo')}")

    doc.add_paragraph()

    # === RISCOS IDENTIFICADOS ===
    doc.add_heading('3. Riscos Identificados', level=1)

    riscos = list(analise.riscos.filter(ativo=True))

    if not riscos:
        doc.add_paragraph('Nenhum risco identificado.')
    else:
        # Agrupar por nivel
        niveis = ['CRITICO', 'ALTO', 'MEDIO', 'BAIXO']
        cores_nivel = {
            'CRITICO': RGBColor(220, 38, 38),
            'ALTO': RGBColor(249, 115, 22),
            'MEDIO': RGBColor(234, 179, 8),
            'BAIXO': RGBColor(34, 197, 94),
        }

        for nivel in niveis:
            riscos_nivel = [r for r in riscos if r.nivel_risco == nivel]
            if not riscos_nivel:
                continue

            # Subtitulo do nivel
            p = doc.add_paragraph()
            run = p.add_run(f'{nivel} ({len(riscos_nivel)} riscos)')
            run.bold = True
            run.font.color.rgb = cores_nivel.get(nivel, RGBColor(0, 0, 0))

            # Tabela de riscos
            table = doc.add_table(rows=1, cols=5)
            table.style = 'Table Grid'

            # Cabecalho
            hdr_cells = table.rows[0].cells
            headers = ['Risco', 'Categoria', 'P', 'I', 'Score']
            for i, h in enumerate(headers):
                hdr_cells[i].text = h
                hdr_cells[i].paragraphs[0].runs[0].bold = True

            # Dados
            for risco in riscos_nivel:
                row_cells = table.add_row().cells
                row_cells[0].text = risco.titulo
                row_cells[1].text = risco.categoria or ''
                row_cells[2].text = str(risco.probabilidade)
                row_cells[3].text = str(risco.impacto)
                row_cells[4].text = str(risco.score_risco)

            doc.add_paragraph()

    # === RESUMO ===
    doc.add_heading('4. Resumo', level=1)

    total = len(riscos)
    criticos = len([r for r in riscos if r.nivel_risco == 'CRITICO'])
    altos = len([r for r in riscos if r.nivel_risco == 'ALTO'])
    medios = len([r for r in riscos if r.nivel_risco == 'MEDIO'])
    baixos = len([r for r in riscos if r.nivel_risco == 'BAIXO'])

    resumo = doc.add_paragraph()
    resumo.add_run(f'Total de riscos: {total}\n')
    resumo.add_run(f'Criticos: {criticos} | Altos: {altos} | Medios: {medios} | Baixos: {baixos}')

    doc.add_paragraph()

    # === RODAPE ===
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run(f'Documento gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(128, 128, 128)

    # Salvar em buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =============================================================================
# GERACAO PDF (reportlab)
# =============================================================================

def gerar_pdf(analise: AnaliseRiscos) -> io.BytesIO:
    """Gera documento PDF com a analise de riscos"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    # Estilos customizados
    styles.add(ParagraphStyle(
        name='CenterTitle',
        parent=styles['Heading1'],
        alignment=1,  # Center
        fontSize=14,
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name='SubHeader',
        parent=styles['Normal'],
        alignment=1,
        fontSize=10,
        textColor=colors.grey,
    ))

    elements = []

    # === CABECALHO ===
    elements.append(Paragraph(
        'MINISTERIO DA GESTAO E DA INOVACAO EM SERVICOS PUBLICOS',
        styles['CenterTitle']
    ))
    elements.append(Paragraph(
        'Secretaria de Gestao de Pessoas - DECIPEX',
        styles['SubHeader']
    ))
    elements.append(Spacer(1, 20))

    # === TITULO ===
    elements.append(Paragraph(
        'RELATORIO DE ANALISE DE RISCOS',
        styles['CenterTitle']
    ))
    elements.append(Spacer(1, 20))

    # === INFORMACOES GERAIS ===
    elements.append(Paragraph('1. Informacoes Gerais', styles['Heading2']))

    contexto = analise.contexto_estruturado or {}
    bloco_a = contexto.get('bloco_a', {})

    info_data = [
        ['Objeto', bloco_a.get('nome_objeto', 'Nao informado')],
        ['Tipo', analise.tipo_origem or 'Nao informado'],
        ['Area Responsavel', bloco_a.get('area_responsavel', 'Nao informado')],
        ['Data da Analise', analise.criado_em.strftime('%d/%m/%Y')],
        ['Status', analise.status or 'Nao informado'],
    ]

    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # === RISCOS IDENTIFICADOS ===
    elements.append(Paragraph('2. Riscos Identificados', styles['Heading2']))

    riscos = list(analise.riscos.filter(ativo=True))

    if not riscos:
        elements.append(Paragraph('Nenhum risco identificado.', styles['Normal']))
    else:
        cores_nivel = {
            'CRITICO': colors.HexColor('#dc2626'),
            'ALTO': colors.HexColor('#f97316'),
            'MEDIO': colors.HexColor('#eab308'),
            'BAIXO': colors.HexColor('#22c55e'),
        }

        for nivel in ['CRITICO', 'ALTO', 'MEDIO', 'BAIXO']:
            riscos_nivel = [r for r in riscos if r.nivel_risco == nivel]
            if not riscos_nivel:
                continue

            # Subtitulo
            elements.append(Paragraph(
                f'<font color="{cores_nivel[nivel].hexval()}">{nivel} ({len(riscos_nivel)} riscos)</font>',
                styles['Heading3']
            ))

            # Tabela
            data = [['Risco', 'Categoria', 'P', 'I', 'Score']]
            for risco in riscos_nivel:
                data.append([
                    risco.titulo[:50] + ('...' if len(risco.titulo) > 50 else ''),
                    risco.categoria or '',
                    str(risco.probabilidade),
                    str(risco.impacto),
                    str(risco.score_risco),
                ])

            t = Table(data, colWidths=[8*cm, 3*cm, 1.5*cm, 1.5*cm, 2*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 20))

    # === RESUMO ===
    elements.append(Paragraph('3. Resumo', styles['Heading2']))

    total = len(riscos)
    criticos = len([r for r in riscos if r.nivel_risco == 'CRITICO'])
    altos = len([r for r in riscos if r.nivel_risco == 'ALTO'])
    medios = len([r for r in riscos if r.nivel_risco == 'MEDIO'])
    baixos = len([r for r in riscos if r.nivel_risco == 'BAIXO'])

    elements.append(Paragraph(
        f'Total de riscos: <b>{total}</b><br/>'
        f'Criticos: <b>{criticos}</b> | Altos: <b>{altos}</b> | Medios: <b>{medios}</b> | Baixos: <b>{baixos}</b>',
        styles['Normal']
    ))

    elements.append(Spacer(1, 30))

    # === RODAPE ===
    elements.append(Paragraph(
        f'<font size=8 color="grey">Documento gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</font>',
        styles['Normal']
    ))

    # Build
    doc.build(elements)
    buffer.seek(0)

    return buffer


# =============================================================================
# ENDPOINT
# =============================================================================

@api_view(["GET"])
@rate_limit_user(limit=10, window=60)
def exportar_analise(request, analise_id):
    """GET /api/analise-riscos/<id>/exportar/?formato=pdf|docx"""
    try:
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return Response({"erro": "Analise nao encontrada"}, status=404)

        formato = request.GET.get('formato', 'pdf').lower()

        if formato == 'docx':
            buffer = gerar_docx(analise)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="analise_riscos_{analise_id}.docx"'
            return response

        elif formato == 'pdf':
            buffer = gerar_pdf(analise)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="analise_riscos_{analise_id}.pdf"'
            return response

        else:
            return Response({"erro": f"Formato '{formato}' nao suportado. Use 'pdf' ou 'docx'."}, status=400)

    except ImportError as e:
        logger.exception("Biblioteca de exportacao nao instalada")
        return Response({"erro": f"Biblioteca nao instalada: {str(e)}"}, status=500)
    except Exception as e:
        logger.exception("Erro ao exportar analise")
        return Response({"erro": str(e)}, status=500)
