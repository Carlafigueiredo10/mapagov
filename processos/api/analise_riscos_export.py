"""
Exportacao de Analise de Riscos para Word e PDF

Endpoints:
- GET /api/analise-riscos/<id>/exportar/?formato=docx
- GET /api/analise-riscos/<id>/exportar/?formato=pdf

Arquitetura:
- Snapshot como fonte unica de dados
- SECTIONS define estrutura semantica comum
- Builders geram conteudo por secao
- Renderers (PDF/DOCX) iteram mesma estrutura
"""
import io
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from processos.models_analise_riscos import AnaliseRiscos
from processos.infra.rate_limiting import rate_limit_user
from processos.api.export_helpers import (
    get_snapshot_para_export,
    verificar_desatualizacao,
    labelize,
    format_value,
    build_bloco_renderizado,
    NOTA_CONDICIONAIS,
    LABELS,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTES
# =============================================================================

def get_orgao_id(request):
    """Extrai orgao_id do usuario (RLS)"""
    import uuid
    if hasattr(request.user, "orgao_id"):
        return request.user.orgao_id
    return uuid.UUID("00000000-0000-0000-0000-000000000000")


# Estrutura semantica unica (PDF e DOCX seguem a mesma ordem)
SECTIONS = [
    {"id": "resumo", "title": "1. Resumo Executivo"},
    {"id": "evidencias", "title": "2. Contexto e Evidencias"},
    {"id": "diagnostico", "title": "3. Diagnostico por Dimensao"},
    {"id": "riscos", "title": "4. Riscos Identificados"},
    {"id": "metadados", "title": "5. Metadados e Rastreabilidade"},
]


# =============================================================================
# BUILDERS - Geram conteudo semantico por secao
# =============================================================================

def build_resumo(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constroi conteudo da secao Resumo Executivo.

    Retorna:
        - resumo: totais por nivel
        - nivel_predominante: nivel com mais riscos
        - top_riscos: 3 maiores por score (opcional)
    """
    resumo = data.get("resumo", {})
    riscos = data.get("riscos", [])

    # Nivel predominante
    niveis = ["criticos", "altos", "medios", "baixos"]
    predominante = None
    max_count = 0
    for nivel in niveis:
        count = resumo.get(nivel, 0)
        if count > max_count:
            max_count = count
            predominante = nivel.rstrip("s").upper()  # "criticos" -> "CRITICO"

    # Top 3 riscos por score
    top_riscos = sorted(riscos, key=lambda r: r.get("score_risco", 0), reverse=True)[:3]

    return {
        "total": resumo.get("total", 0),
        "criticos": resumo.get("criticos", 0),
        "altos": resumo.get("altos", 0),
        "medios": resumo.get("medios", 0),
        "baixos": resumo.get("baixos", 0),
        "nivel_predominante": predominante,
        "top_riscos": [
            {
                "titulo": r.get("titulo", ""),
                "nivel": r.get("nivel_risco", ""),
                "score": r.get("score_risco", 0),
            }
            for r in top_riscos
        ],
    }


def build_evidencias(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constroi conteudo da secao Contexto e Evidencias.

    Retorna:
        - bloco_a: campos de identificacao
        - bloco_b: campos de contexto operacional
        - nota_condicionais: texto da nota
    """
    contexto = data.get("contexto_estruturado", {})
    bloco_a = contexto.get("bloco_a", {})
    bloco_b = contexto.get("bloco_b", {})

    # Bloco A - campos fixos
    evidencias_a = [
        {"label": "Nome do objeto", "valor": format_value(bloco_a.get("nome_objeto"), required=True)},
        {"label": "Objetivo/Finalidade", "valor": format_value(bloco_a.get("objetivo_finalidade"), required=True)},
        {"label": "Area responsavel", "valor": format_value(bloco_a.get("area_responsavel"), required=True)},
        {"label": "Descricao do escopo", "valor": format_value(bloco_a.get("descricao_escopo"), required=False)},
    ]

    # Bloco B - 7 perguntas
    labels_b = {
        "recursos_necessarios": "Quais recursos sao necessarios?",
        "areas_atores_envolvidos": "Quais areas/atores estao envolvidos?",
        "frequencia_execucao": "Com que frequencia ocorre?",
        "prazos_slas": "Existem prazos legais ou SLAs?",
        "dependencias_externas": "Ha dependencia de terceiros/sistemas externos?",
        "historico_problemas": "Houve problemas ou incidentes anteriores?",
        "impacto_se_falhar": "O que acontece se falhar?",
    }

    evidencias_b = []
    for campo, label in labels_b.items():
        valor_raw = bloco_b.get(campo)
        # Frequencia e enum
        if campo == "frequencia_execucao":
            valor = labelize(valor_raw) if valor_raw else format_value(None, required=True)
        else:
            valor = format_value(valor_raw, required=True)
        evidencias_b.append({"label": label, "valor": valor})

    return {
        "bloco_a": evidencias_a,
        "bloco_b": evidencias_b,
        "nota_condicionais": NOTA_CONDICIONAIS,
    }


def build_diagnostico(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Constroi conteudo da secao Diagnostico por Dimensao.

    Retorna lista dos 6 blocos renderizados (usando helper).
    """
    respostas_blocos = data.get("respostas_blocos", {})

    blocos_ids = ["BLOCO_1", "BLOCO_2", "BLOCO_3", "BLOCO_4", "BLOCO_5", "BLOCO_6"]
    diagnostico = []

    for bloco_id in blocos_ids:
        respostas = respostas_blocos.get(bloco_id, {})
        bloco_renderizado = build_bloco_renderizado(bloco_id, respostas)
        diagnostico.append(bloco_renderizado)

    return diagnostico


def build_riscos(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constroi conteudo da secao Riscos Identificados.

    Retorna:
        - tabela_resumo: lista para tabela compacta
        - detalhes: lista de blocos detalhados por risco
    """
    riscos = data.get("riscos", [])

    # Tabela resumo (titulo + nivel + score)
    tabela_resumo = [
        {
            "titulo": r.get("titulo", ""),
            "categoria": labelize(r.get("categoria", "")),
            "nivel": r.get("nivel_risco", ""),
            "score": r.get("score_risco", 0),
        }
        for r in riscos
    ]

    # Detalhes por risco
    detalhes = []
    for risco in riscos:
        detalhe = {
            "titulo": risco.get("titulo", ""),
            "descricao": format_value(risco.get("descricao"), required=False),
            "categoria": labelize(risco.get("categoria", "")),
            "probabilidade": risco.get("probabilidade", 0),
            "impacto": risco.get("impacto", 0),
            "score": risco.get("score_risco", 0),
            "nivel": risco.get("nivel_risco", ""),
            "fonte": labelize(risco.get("fonte_sugestao", "")),
            "bloco_origem": risco.get("bloco_origem", ""),
            "justificativa": format_value(risco.get("justificativa"), required=False),
            "grau_confianca": labelize(risco.get("grau_confianca", "")) if risco.get("grau_confianca") else None,
            "regra_aplicada": risco.get("regra_aplicada", "") or None,
            "perguntas_acionadoras": risco.get("perguntas_acionadoras", []),
            # RespostaRisco (plano de tratamento)
            "respostas": [],
        }

        for resp in risco.get("respostas", []):
            detalhe["respostas"].append({
                "estrategia": labelize(resp.get("estrategia", "")),
                "acao": resp.get("descricao_acao", ""),
                "responsavel": resp.get("responsavel_nome", ""),
                "area": resp.get("responsavel_area", ""),
                "prazo": resp.get("prazo", ""),
            })

        detalhes.append(detalhe)

    return {
        "tabela_resumo": tabela_resumo,
        "detalhes": detalhes,
        "total": len(riscos),
    }


def build_metadados(data: Dict[str, Any], snap, desatualizado: bool) -> Dict[str, Any]:
    """
    Constroi conteudo da secao Metadados e Rastreabilidade.
    """
    return {
        "analise_id": data.get("analise_id", ""),
        "versao_sistema": data.get("versao_sistema", ""),
        "schema_version": data.get("schema_version", ""),
        "fonte_estado_em": data.get("fonte_estado_em", ""),
        "snapshot_versao": snap.versao if snap else None,
        "snapshot_motivo": snap.motivo_snapshot if snap else None,
        "snapshot_criado_em": snap.criado_em.strftime("%d/%m/%Y %H:%M") if snap and snap.criado_em else None,
        "export_gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "desatualizado": desatualizado,
        "aviso_desatualizacao": "Ha alteracoes apos o snapshot; este export pode estar desatualizado." if desatualizado else None,
    }


# =============================================================================
# RENDERER PDF (reportlab) - DS Gov "good enough"
# =============================================================================

# Cores DS Gov
COR_AZUL_GOV = None  # Inicializado no render
COR_AZUL_ESCURO = None
COR_CINZA = None
COR_CINZA_CLARO = None

CORES_NIVEL_PDF = None


def _init_pdf_colors():
    """Inicializa cores do PDF (lazy load)."""
    global COR_AZUL_GOV, COR_AZUL_ESCURO, COR_CINZA, COR_CINZA_CLARO, CORES_NIVEL_PDF
    from reportlab.lib import colors

    COR_AZUL_GOV = colors.HexColor('#1351B4')
    COR_AZUL_ESCURO = colors.HexColor('#071D41')
    COR_CINZA = colors.HexColor('#636363')
    COR_CINZA_CLARO = colors.HexColor('#E8E8E8')

    CORES_NIVEL_PDF = {
        'CRITICO': colors.HexColor('#dc2626'),
        'ALTO': colors.HexColor('#f97316'),
        'MEDIO': colors.HexColor('#eab308'),
        'BAIXO': colors.HexColor('#22c55e'),
    }


def _draw_header_footer(canvas, doc, metadados: Dict[str, Any]):
    """Desenha header e footer institucional em todas as paginas."""
    from reportlab.lib.units import cm

    _init_pdf_colors()

    width, height = doc.pagesize

    # === HEADER: Faixa azul no topo ===
    canvas.saveState()

    # Faixa azul
    canvas.setFillColor(COR_AZUL_GOV)
    canvas.rect(0, height - 1.2*cm, width, 1.2*cm, fill=1, stroke=0)

    # Texto do header
    canvas.setFillColor('white')
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(2*cm, height - 0.8*cm, "ANALISE DE RISCOS - HELENA")

    # ID e data no header (lado direito)
    canvas.setFont('Helvetica', 8)
    header_right = f"ID: {metadados.get('analise_id', '')[:8]}... | {metadados.get('export_gerado_em', '')}"
    canvas.drawRightString(width - 2*cm, height - 0.8*cm, header_right)

    canvas.restoreState()

    # === FOOTER: Metadados e paginacao ===
    canvas.saveState()

    # Linha separadora
    canvas.setStrokeColor(COR_CINZA_CLARO)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.5*cm, width - 2*cm, 1.5*cm)

    # Texto esquerdo: snapshot info
    canvas.setFillColor(COR_CINZA)
    canvas.setFont('Helvetica', 7)
    footer_left = f"Snapshot v{metadados.get('snapshot_versao', '?')} | {metadados.get('versao_sistema', '')} | Schema {metadados.get('schema_version', '')}"
    canvas.drawString(2*cm, 1*cm, footer_left)

    # Texto direito: paginacao
    page_num = canvas.getPageNumber()
    canvas.drawRightString(width - 2*cm, 1*cm, f"Pagina {page_num}")

    canvas.restoreState()


def render_pdf(data: Dict[str, Any], snap, desatualizado: bool) -> io.BytesIO:
    """Renderiza PDF usando SECTIONS e builders com visual DS Gov."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame,
        Paragraph, Spacer, Table, TableStyle, KeepTogether
    )

    _init_pdf_colors()

    buffer = io.BytesIO()

    # Metadados para header/footer
    metadados = build_metadados(data, snap, desatualizado)

    # Documento com template customizado
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2.5*cm,  # Espaco para header
        bottomMargin=2*cm,  # Espaco para footer
        leftMargin=2*cm,
        rightMargin=2*cm,
    )

    # Frame principal
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id='main'
    )

    # Template com header/footer
    def on_page(canvas, doc):
        _draw_header_footer(canvas, doc, metadados)

    template = PageTemplate(id='main', frames=frame, onPage=on_page)
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()

    # Estilos customizados - DS Gov
    styles.add(ParagraphStyle(
        name='GovTitle',
        parent=styles['Heading1'],
        alignment=1,
        fontSize=18,
        textColor=COR_AZUL_ESCURO,
        spaceBefore=0,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name='GovSubtitle',
        parent=styles['Normal'],
        alignment=1,
        fontSize=10,
        textColor=COR_CINZA,
        spaceAfter=16,
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=COR_AZUL_GOV,
        spaceBefore=20,
        spaceAfter=10,
        borderPadding=(0, 0, 4, 0),
        borderWidth=0,
        borderColor=COR_AZUL_GOV,
    ))
    styles.add(ParagraphStyle(
        name='SubSectionTitle',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=COR_AZUL_ESCURO,
        spaceBefore=12,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name='GovBody',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name='SmallGray',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COR_CINZA,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='CardTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COR_AZUL_ESCURO,
        spaceBefore=0,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name='Warning',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#E52207'),
        backColor=colors.HexColor('#FFF4F2'),
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8,
    ))

    elements = []

    # === TITULO DO DOCUMENTO (primeira pagina) ===
    elements.append(Paragraph('MINISTERIO DA GESTAO E DA INOVACAO', styles['GovTitle']))
    elements.append(Paragraph('EM SERVICOS PUBLICOS', styles['GovTitle']))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph('Relatorio de Analise de Riscos', styles['GovSubtitle']))

    # Aviso de desatualizacao (se aplicavel) - logo no inicio
    if metadados['desatualizado'] and metadados['aviso_desatualizacao']:
        elements.append(Paragraph(f"ATENCAO: {metadados['aviso_desatualizacao']}", styles['Warning']))

    elements.append(Spacer(1, 10))

    # Build conteudo por secao
    resumo = build_resumo(data)
    evidencias = build_evidencias(data)
    diagnostico = build_diagnostico(data)
    riscos = build_riscos(data)
    # metadados ja foi construido acima

    # === SECAO 1: RESUMO EXECUTIVO ===
    elements.append(Paragraph(SECTIONS[0]["title"], styles['SectionTitle']))

    # Tabela de distribuicao (visual)
    dist_data = [
        ['Total', 'Criticos', 'Altos', 'Medios', 'Baixos'],
        [
            str(resumo['total']),
            str(resumo['criticos']),
            str(resumo['altos']),
            str(resumo['medios']),
            str(resumo['baixos']),
        ]
    ]
    dist_table = Table(dist_data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COR_AZUL_GOV),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, COR_CINZA_CLARO),
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#FEE2E2')),  # Criticos
        ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#FFEDD5')),  # Altos
        ('BACKGROUND', (3, 1), (3, 1), colors.HexColor('#FEF9C3')),  # Medios
        ('BACKGROUND', (4, 1), (4, 1), colors.HexColor('#DCFCE7')),  # Baixos
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(dist_table)
    elements.append(Spacer(1, 12))

    if resumo['top_riscos']:
        elements.append(Paragraph('<b>Principais riscos (por score):</b>', styles['GovBody']))
        for i, r in enumerate(resumo['top_riscos'], 1):
            cor = CORES_NIVEL_PDF.get(r['nivel'], colors.black)
            elements.append(Paragraph(
                f"{i}. {r['titulo']} - <font color='{cor.hexval()}'><b>{r['nivel']}</b></font> (score: {r['score']})",
                styles['GovBody']
            ))

    elements.append(Spacer(1, 10))

    # === SECAO 2: CONTEXTO E EVIDENCIAS ===
    elements.append(Paragraph(SECTIONS[1]["title"], styles['SectionTitle']))

    # Bloco A
    elements.append(Paragraph('<b>Identificacao do Objeto</b>', styles['SubSectionTitle']))
    for item in evidencias['bloco_a']:
        if item['valor']:
            elements.append(Paragraph(f"<b>{item['label']}:</b> {item['valor']}", styles['GovBody']))

    elements.append(Spacer(1, 6))

    # Bloco B
    elements.append(Paragraph('<b>Contexto Operacional</b>', styles['SubSectionTitle']))
    for item in evidencias['bloco_b']:
        elements.append(Paragraph(f"<b>{item['label']}:</b> {item['valor']}", styles['GovBody']))

    elements.append(Spacer(1, 10))

    # === SECAO 3: DIAGNOSTICO POR DIMENSAO ===
    elements.append(Paragraph(SECTIONS[2]["title"], styles['SectionTitle']))
    elements.append(Paragraph(f"<i>{evidencias['nota_condicionais']}</i>", styles['SmallGray']))
    elements.append(Spacer(1, 6))

    for bloco in diagnostico:
        elements.append(Paragraph(f"<b>{bloco['titulo']}</b>", styles['SubSectionTitle']))

        if not bloco['perguntas']:
            elements.append(Paragraph("<i>Nenhuma resposta registrada</i>", styles['SmallGray']))
        else:
            for p in bloco['perguntas']:
                elements.append(Paragraph(f"• {p['texto']}: <b>{p['valor_label']}</b>", styles['GovBody']))

        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 10))

    # === SECAO 4: RISCOS IDENTIFICADOS ===
    elements.append(Paragraph(SECTIONS[3]["title"], styles['SectionTitle']))

    if not riscos['detalhes']:
        elements.append(Paragraph("Nenhum risco identificado.", styles['GovBody']))
    else:
        # Tabela resumo compacta (se <= 15 riscos, senao polui)
        if riscos['total'] <= 15:
            table_data = [['Risco', 'Categoria', 'Nivel', 'Score']]
            for r in riscos['tabela_resumo']:
                table_data.append([
                    Paragraph(r['titulo'][:45] + ('...' if len(r['titulo']) > 45 else ''), styles['SmallGray']),
                    r['categoria'],
                    r['nivel'],
                    str(r['score']),
                ])

            t = Table(table_data, colWidths=[8*cm, 3*cm, 2*cm, 1.5*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COR_AZUL_GOV),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, COR_CINZA_CLARO),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 16))

        # Detalhes por risco (CARDS)
        elements.append(Paragraph('<b>Detalhamento dos Riscos</b>', styles['SubSectionTitle']))
        elements.append(Spacer(1, 8))

        for i, detalhe in enumerate(riscos['detalhes'], 1):
            cor_nivel = CORES_NIVEL_PDF.get(detalhe['nivel'], colors.black)

            # === CARD DO RISCO (KeepTogether evita quebra no meio) ===
            card_elements = []

            # Titulo do card
            card_elements.append(Paragraph(
                f"<b>{i}. {detalhe['titulo']}</b>",
                styles['CardTitle']
            ))

            # Linha de metricas: Nivel | Score | Categoria | P/I
            metrics_text = f"<font color='{cor_nivel.hexval()}'><b>{detalhe['nivel']}</b></font> | Score: {detalhe['score']} | {detalhe['categoria']} | P:{detalhe['probabilidade']} I:{detalhe['impacto']}"
            card_elements.append(Paragraph(metrics_text, styles['SmallGray']))

            # Fonte
            card_elements.append(Paragraph(f"Fonte: {detalhe['fonte']}", styles['SmallGray']))

            # Descricao
            if detalhe['descricao']:
                card_elements.append(Spacer(1, 4))
                card_elements.append(Paragraph(f"<b>Descricao:</b> {detalhe['descricao']}", styles['GovBody']))

            # Justificativa
            if detalhe['justificativa']:
                card_elements.append(Paragraph(f"<b>Justificativa:</b> {detalhe['justificativa']}", styles['GovBody']))

            # Bloco origem / regra (se inferido)
            if detalhe['bloco_origem']:
                meta = f"Origem: {detalhe['bloco_origem']}"
                if detalhe['regra_aplicada']:
                    meta += f" | Regra: {detalhe['regra_aplicada']}"
                if detalhe['grau_confianca']:
                    meta += f" | Confianca: {detalhe['grau_confianca']}"
                card_elements.append(Paragraph(meta, styles['SmallGray']))

            # RespostaRisco (plano de tratamento)
            if detalhe['respostas']:
                card_elements.append(Spacer(1, 4))
                card_elements.append(Paragraph("<b>Plano de Resposta:</b>", styles['GovBody']))
                for resp in detalhe['respostas']:
                    resp_text = f"  - {resp['estrategia']}: {resp['acao']}"
                    if resp['responsavel']:
                        resp_text += f" (Resp: {resp['responsavel']}"
                        if resp['area']:
                            resp_text += f" / {resp['area']}"
                        resp_text += ")"
                    if resp['prazo']:
                        resp_text += f" - Prazo: {resp['prazo']}"
                    card_elements.append(Paragraph(resp_text, styles['GovBody']))

            # Linha divisoria (visual de card)
            card_elements.append(Spacer(1, 8))

            # Adiciona card como bloco unico (nao quebra no meio)
            elements.append(KeepTogether(card_elements))

            # Separador entre cards
            elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 16))

    # === SECAO 5: METADADOS E RASTREABILIDADE ===
    elements.append(Paragraph(SECTIONS[4]["title"], styles['SectionTitle']))

    # Metadados em tabela compacta
    meta_data = [
        ['ID da Analise', metadados['analise_id']],
        ['Versao do Sistema', metadados['versao_sistema']],
        ['Schema', metadados['schema_version']],
        ['Estado capturado em', metadados['fonte_estado_em']],
        ['Snapshot', f"v{metadados['snapshot_versao']} ({metadados['snapshot_motivo']})"],
        ['Export gerado em', metadados['export_gerado_em']],
    ]

    meta_table = Table(meta_data, colWidths=[4.5*cm, 10*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), COR_CINZA),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, COR_CINZA_CLARO),
    ]))
    elements.append(meta_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer


# =============================================================================
# RENDERER DOCX (python-docx)
# =============================================================================

def render_docx(data: Dict[str, Any], snap, desatualizado: bool) -> io.BytesIO:
    """Renderiza DOCX usando SECTIONS e builders - editavel e limpo."""
    from docx import Document
    from docx.shared import Pt, RGBColor, Twips
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE

    doc = Document()

    # === CONFIGURAR ESTILOS GLOBAIS ===
    # Normal
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(10)
    style_normal.paragraph_format.space_after = Pt(6)

    # Heading 1
    style_h1 = doc.styles['Heading 1']
    style_h1.font.name = 'Calibri'
    style_h1.font.size = Pt(14)
    style_h1.font.bold = True
    style_h1.font.color.rgb = RGBColor(0x13, 0x51, 0xB4)  # Azul Gov
    style_h1.paragraph_format.space_before = Pt(18)
    style_h1.paragraph_format.space_after = Pt(10)

    # Heading 2
    style_h2 = doc.styles['Heading 2']
    style_h2.font.name = 'Calibri'
    style_h2.font.size = Pt(12)
    style_h2.font.bold = True
    style_h2.font.color.rgb = RGBColor(0x07, 0x1D, 0x41)  # Azul escuro
    style_h2.paragraph_format.space_before = Pt(14)
    style_h2.paragraph_format.space_after = Pt(8)

    # Cores
    COR_AZUL_GOV = RGBColor(0x13, 0x51, 0xB4)
    COR_AZUL_ESCURO = RGBColor(0x07, 0x1D, 0x41)
    COR_CINZA = RGBColor(0x63, 0x63, 0x63)
    COR_VERMELHO = RGBColor(0xE5, 0x22, 0x07)

    CORES_NIVEL = {
        'CRITICO': RGBColor(220, 38, 38),
        'ALTO': RGBColor(249, 115, 22),
        'MEDIO': RGBColor(234, 179, 8),
        'BAIXO': RGBColor(34, 197, 94),
    }

    # === CABECALHO DO DOCUMENTO ===
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = header.add_run('MINISTERIO DA GESTAO E DA INOVACAO EM SERVICOS PUBLICOS')
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = COR_AZUL_ESCURO

    subheader = doc.add_paragraph()
    subheader.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subheader.add_run('Relatorio de Analise de Riscos')
    run.font.size = Pt(11)
    run.font.color.rgb = COR_CINZA

    # Build metadados
    metadados = build_metadados(data, snap, desatualizado)

    # Aviso de desatualizacao (se aplicavel) logo no inicio
    if metadados['desatualizado'] and metadados['aviso_desatualizacao']:
        p_aviso = doc.add_paragraph()
        run_aviso = p_aviso.add_run(f"ATENCAO: {metadados['aviso_desatualizacao']}")
        run_aviso.bold = True
        run_aviso.font.color.rgb = COR_VERMELHO

    doc.add_paragraph()

    # Build conteudo por secao
    resumo = build_resumo(data)
    evidencias = build_evidencias(data)
    diagnostico = build_diagnostico(data)
    riscos = build_riscos(data)
    # metadados ja foi construido acima

    # === SECAO 1: RESUMO EXECUTIVO ===
    doc.add_heading(SECTIONS[0]["title"], level=1)

    # Tabela de distribuicao
    table_dist = doc.add_table(rows=2, cols=5)
    table_dist.style = 'Table Grid'

    # Header
    headers = ['Total', 'Criticos', 'Altos', 'Medios', 'Baixos']
    for i, h in enumerate(headers):
        cell = table_dist.rows[0].cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Valores
    values = [resumo['total'], resumo['criticos'], resumo['altos'], resumo['medios'], resumo['baixos']]
    for i, v in enumerate(values):
        cell = table_dist.rows[1].cells[i]
        cell.text = str(v)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()

    if resumo['top_riscos']:
        p2 = doc.add_paragraph()
        p2.add_run('Principais riscos (por score):').bold = True
        for i, r in enumerate(resumo['top_riscos'], 1):
            p3 = doc.add_paragraph(style='List Bullet')
            p3.add_run(f'{r["titulo"]} - ')
            run_nivel = p3.add_run(r['nivel'])
            run_nivel.font.color.rgb = CORES_NIVEL.get(r['nivel'], COR_CINZA)
            run_nivel.bold = True
            p3.add_run(f' (score: {r["score"]})')

    doc.add_paragraph()

    # === SECAO 2: CONTEXTO E EVIDENCIAS ===
    h2 = doc.add_heading(SECTIONS[1]["title"], level=1)
    h2.runs[0].font.color.rgb = COR_AZUL_GOV

    # Bloco A
    doc.add_heading('Identificacao do Objeto', level=2)
    for item in evidencias['bloco_a']:
        if item['valor']:
            p = doc.add_paragraph()
            p.add_run(f"{item['label']}: ").bold = True
            p.add_run(item['valor'])

    # Bloco B
    doc.add_heading('Contexto Operacional', level=2)
    for item in evidencias['bloco_b']:
        p = doc.add_paragraph()
        p.add_run(f"{item['label']}: ").bold = True
        p.add_run(item['valor'])

    doc.add_paragraph()

    # === SECAO 3: DIAGNOSTICO POR DIMENSAO ===
    h3 = doc.add_heading(SECTIONS[2]["title"], level=1)
    h3.runs[0].font.color.rgb = COR_AZUL_GOV

    # Nota condicionais
    p_nota = doc.add_paragraph()
    run_nota = p_nota.add_run(evidencias['nota_condicionais'])
    run_nota.italic = True
    run_nota.font.size = Pt(9)
    run_nota.font.color.rgb = COR_CINZA

    for bloco in diagnostico:
        doc.add_heading(bloco['titulo'], level=2)

        if not bloco['perguntas']:
            p = doc.add_paragraph()
            run = p.add_run('Nenhuma resposta registrada')
            run.italic = True
            run.font.color.rgb = COR_CINZA
        else:
            for pergunta in bloco['perguntas']:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(f"{pergunta['texto']}: ")
                run_resp = p.add_run(pergunta['valor_label'])
                run_resp.bold = True

    doc.add_paragraph()

    # === SECAO 4: RISCOS IDENTIFICADOS ===
    doc.add_heading(SECTIONS[3]["title"], level=1)

    if not riscos['detalhes']:
        doc.add_paragraph('Nenhum risco identificado.')
    else:
        # Tabela resumo compacta (se <= 15 riscos)
        if riscos['total'] <= 15:
            table = doc.add_table(rows=1, cols=4)
            table.style = 'Table Grid'

            # Header
            headers = ['Risco', 'Categoria', 'Nivel', 'Score']
            for i, h in enumerate(headers):
                cell = table.rows[0].cells[i]
                cell.text = h
                cell.paragraphs[0].runs[0].bold = True

            # Linhas
            for r in riscos['tabela_resumo']:
                row = table.add_row()
                row.cells[0].text = r['titulo'][:50] + ('...' if len(r['titulo']) > 50 else '')
                row.cells[1].text = r['categoria']
                row.cells[2].text = r['nivel']
                row.cells[3].text = str(r['score'])

            doc.add_paragraph()

        # Detalhamento por risco
        doc.add_heading('Detalhamento dos Riscos', level=2)

        for i, detalhe in enumerate(riscos['detalhes'], 1):
            # === CARD DO RISCO ===

            # Titulo
            p_titulo = doc.add_paragraph()
            p_titulo.add_run(f'{i}. {detalhe["titulo"]}').bold = True

            # Linha de metricas
            p_meta = doc.add_paragraph()
            run_nivel = p_meta.add_run(f'{detalhe["nivel"]}')
            run_nivel.bold = True
            run_nivel.font.color.rgb = CORES_NIVEL.get(detalhe['nivel'], COR_CINZA)
            run_rest = p_meta.add_run(f' | Score: {detalhe["score"]} | {detalhe["categoria"]} | P:{detalhe["probabilidade"]} I:{detalhe["impacto"]}')
            run_rest.font.size = Pt(9)
            run_rest.font.color.rgb = COR_CINZA

            # Fonte
            p_fonte = doc.add_paragraph()
            run_fonte = p_fonte.add_run(f'Fonte: {detalhe["fonte"]}')
            run_fonte.font.size = Pt(9)
            run_fonte.font.color.rgb = COR_CINZA

            # Descricao
            if detalhe['descricao']:
                p = doc.add_paragraph()
                p.add_run('Descricao: ').bold = True
                p.add_run(detalhe['descricao'])

            # Justificativa
            if detalhe['justificativa']:
                p = doc.add_paragraph()
                p.add_run('Justificativa: ').bold = True
                p.add_run(detalhe['justificativa'])

            # Origem/Regra
            if detalhe['bloco_origem']:
                p_origem = doc.add_paragraph()
                meta_text = f"Origem: {detalhe['bloco_origem']}"
                if detalhe['regra_aplicada']:
                    meta_text += f" | Regra: {detalhe['regra_aplicada']}"
                if detalhe['grau_confianca']:
                    meta_text += f" | Confianca: {detalhe['grau_confianca']}"
                run_origem = p_origem.add_run(meta_text)
                run_origem.font.size = Pt(9)
                run_origem.font.color.rgb = COR_CINZA

            # RespostaRisco (plano de tratamento)
            if detalhe['respostas']:
                p_plano = doc.add_paragraph()
                p_plano.add_run('Plano de Resposta:').bold = True

                for resp in detalhe['respostas']:
                    p_resp = doc.add_paragraph(style='List Bullet')
                    p_resp.add_run(f"{resp['estrategia']}: ").bold = True
                    p_resp.add_run(resp['acao'])
                    if resp['responsavel']:
                        p_resp.add_run(f" (Resp: {resp['responsavel']}")
                        if resp['area']:
                            p_resp.add_run(f" / {resp['area']}")
                        p_resp.add_run(")")
                    if resp['prazo']:
                        p_resp.add_run(f" - Prazo: {resp['prazo']}")

            # Separador visual entre riscos
            doc.add_paragraph()

    # === SECAO 5: METADADOS E RASTREABILIDADE ===
    doc.add_heading(SECTIONS[4]["title"], level=1)

    # Metadados em tabela compacta
    table_meta = doc.add_table(rows=6, cols=2)

    meta_rows = [
        ('ID da Analise', metadados['analise_id']),
        ('Versao do Sistema', metadados['versao_sistema']),
        ('Schema', metadados['schema_version']),
        ('Estado capturado em', metadados['fonte_estado_em']),
        ('Snapshot', f"v{metadados['snapshot_versao']} ({metadados['snapshot_motivo']})"),
        ('Export gerado em', metadados['export_gerado_em']),
    ]

    for i, (label, value) in enumerate(meta_rows):
        row = table_meta.rows[i]
        cell_label = row.cells[0]
        cell_value = row.cells[1]

        run_label = cell_label.paragraphs[0].add_run(label)
        run_label.bold = True
        run_label.font.size = Pt(9)
        run_label.font.color.rgb = COR_CINZA

        run_value = cell_value.paragraphs[0].add_run(str(value) if value else '')
        run_value.font.size = Pt(9)
        run_value.font.color.rgb = COR_CINZA

    # Salvar
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =============================================================================
# FUNCOES LEGADAS (mantidas para compatibilidade)
# =============================================================================

def gerar_docx(analise: AnaliseRiscos) -> io.BytesIO:
    """Wrapper legado - usa novo sistema de snapshot."""
    from processos.api.export_helpers import build_snapshot_payload
    data = build_snapshot_payload(analise)
    return render_docx(data, snap=None, desatualizado=False)


def gerar_pdf(analise: AnaliseRiscos) -> io.BytesIO:
    """Wrapper legado - usa novo sistema de snapshot."""
    from processos.api.export_helpers import build_snapshot_payload
    data = build_snapshot_payload(analise)
    return render_pdf(data, snap=None, desatualizado=False)


# =============================================================================
# ENDPOINT
# =============================================================================

@api_view(["GET"])
@rate_limit_user(limit=10, window=60)
def exportar_analise(request, analise_id):
    """
    GET /api/analise-riscos/<id>/exportar/?formato=pdf|docx

    Exporta analise usando snapshot como fonte unica.
    """
    try:
        orgao_id = get_orgao_id(request)

        analise = AnaliseRiscos.objects.filter(
            id=analise_id, orgao_id=orgao_id
        ).first()

        if not analise:
            return Response({"erro": "Analise nao encontrada"}, status=404)

        formato = request.GET.get('formato', 'pdf').lower()

        # === NOVO: Snapshot como fonte unica ===
        snap = get_snapshot_para_export(analise, request.user)
        data = snap.dados_completos
        desatualizado = verificar_desatualizacao(analise, snap)

        if formato == 'docx':
            buffer = render_docx(data, snap, desatualizado)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="analise_riscos_{analise_id}.docx"'
            return response

        elif formato == 'pdf':
            buffer = render_pdf(data, snap, desatualizado)
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
