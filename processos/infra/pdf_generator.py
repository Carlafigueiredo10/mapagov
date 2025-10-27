"""
Gerador de PDF profissional para POP (Procedimento Operacional Padrão)

Gera PDFs com:
- Capa profissional com selo do sistema
- Versão e data
- Campo de assinatura
- Todas as seções do POP formatadas
"""
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


class POPPDFGenerator:
    """Gerador de PDF profissional para POP"""

    # Cores do design GOVBR
    COR_PRIMARIA = HexColor('#1351B4')  # Azul GOVBR
    COR_SECUNDARIA = HexColor('#071D41')  # Azul escuro
    COR_DESTAQUE = HexColor('#FFCD07')  # Amarelo
    COR_TEXTO = HexColor('#333333')
    COR_TEXTO_CLARO = HexColor('#666666')

    def __init__(self, dados_pop: dict):
        """
        Inicializa o gerador

        Args:
            dados_pop: Dicionário com todos os dados do POP
                Estrutura esperada:
                {
                    'codigo_cap': str,
                    'area': {'nome': str, 'codigo': str},
                    'macro': str,
                    'processo': str,
                    'subprocesso': str,
                    'atividade': str,
                    'nome_processo': str,
                    'entrega_esperada': str,
                    'dispositivos_normativos': list,
                    'operadores': list,
                    'sistemas': list,
                    'documentos': list,
                    'fluxos_entrada': list,
                    'fluxos_saida': list,
                    'pontos_atencao': str,
                    'nome_usuario': str,
                    'versao': str (opcional),
                }
        """
        self.dados = dados_pop
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        self.story = []

    def _criar_estilos_customizados(self):
        """Cria estilos customizados para o documento"""
        # Título da capa
        self.styles.add(ParagraphStyle(
            name='TituloCapa',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COR_PRIMARIA,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo da capa
        self.styles.add(ParagraphStyle(
            name='SubtituloCapa',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=self.COR_SECUNDARIA,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Informações da capa
        self.styles.add(ParagraphStyle(
            name='InfoCapa',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.COR_TEXTO_CLARO,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Título de seção
        self.styles.add(ParagraphStyle(
            name='TituloSecao',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.COR_PRIMARIA,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            borderColor=self.COR_PRIMARIA,
            borderRadius=None
        ))

        # Subtítulo de seção
        self.styles.add(ParagraphStyle(
            name='SubtituloSecao',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=self.COR_SECUNDARIA,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Corpo de texto
        self.styles.add(ParagraphStyle(
            name='CorpoTexto',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COR_TEXTO,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))

        # Item de lista
        self.styles.add(ParagraphStyle(
            name='ItemLista',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.COR_TEXTO,
            spaceAfter=4,
            leftIndent=20,
            fontName='Helvetica'
        ))

    def _criar_capa(self):
        """Cria a capa do documento"""
        # Logo/Selo do sistema (placeholder - você pode adicionar uma imagem real)
        # Se tiver logo: logo = Image('path/to/logo.png', width=4*cm, height=4*cm)
        # self.story.append(logo)

        # Espaçamento superior
        self.story.append(Spacer(1, 3*cm))

        # Selo textual (enquanto não tem imagem)
        selo_data = [
            ['DECIPEX'],
            ['Sistema de Gestão de Processos'],
        ]
        selo_table = Table(selo_data, colWidths=[12*cm])
        selo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COR_PRIMARIA),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 18),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, self.COR_PRIMARIA),
        ]))
        self.story.append(selo_table)
        self.story.append(Spacer(1, 2*cm))

        # Título
        titulo = Paragraph(
            "PROCEDIMENTO OPERACIONAL PADRÃO",
            self.styles['TituloCapa']
        )
        self.story.append(titulo)

        # Nome do processo
        nome_processo = self.dados.get('nome_processo', 'Processo não especificado')
        subtitulo = Paragraph(
            f"<b>{nome_processo}</b>",
            self.styles['SubtituloCapa']
        )
        self.story.append(subtitulo)

        self.story.append(Spacer(1, 1*cm))

        # Código CAP
        codigo_cap = self.dados.get('codigo_cap', 'N/A')
        info_codigo = Paragraph(
            f"<b>Código CAP:</b> {codigo_cap}",
            self.styles['InfoCapa']
        )
        self.story.append(info_codigo)

        # Área
        area = self.dados.get('area', {})
        area_nome = area.get('nome', 'N/A')
        area_codigo = area.get('codigo', 'N/A')
        info_area = Paragraph(
            f"<b>Área:</b> {area_nome} ({area_codigo})",
            self.styles['InfoCapa']
        )
        self.story.append(info_area)

        self.story.append(Spacer(1, 2*cm))

        # Versão e data
        versao = self.dados.get('versao', '1.0')
        data_criacao = datetime.now().strftime('%d/%m/%Y')

        info_versao_data = [
            [f'Versão {versao}', f'Data: {data_criacao}']
        ]
        versao_table = Table(info_versao_data, colWidths=[8*cm, 8*cm])
        versao_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COR_TEXTO_CLARO),
        ]))
        self.story.append(versao_table)

        self.story.append(Spacer(1, 3*cm))

        # Campo de assinatura
        assinatura_data = [
            [''],
            ['_' * 50],
            [f"{self.dados.get('nome_usuario', 'Responsável')}"],
            ['Elaborador']
        ]
        assinatura_table = Table(assinatura_data, colWidths=[12*cm])
        assinatura_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COR_TEXTO),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        self.story.append(assinatura_table)

        # Quebra de página após a capa
        self.story.append(PageBreak())

    def _criar_secao_identificacao(self):
        """Cria a seção de identificação do processo"""
        self.story.append(Paragraph("1. IDENTIFICAÇÃO DO PROCESSO", self.styles['TituloSecao']))

        # Criar tabela de identificação
        dados_identificacao = [
            ['Código CAP', self.dados.get('codigo_cap', 'N/A')],
            ['Nome do Processo', self.dados.get('nome_processo', 'N/A')],
            ['Área', f"{self.dados.get('area', {}).get('nome', 'N/A')} ({self.dados.get('area', {}).get('codigo', 'N/A')})"],
            ['Macroprocesso', self.dados.get('macro', 'N/A')],
            ['Processo', self.dados.get('processo', 'N/A')],
            ['Subprocesso', self.dados.get('subprocesso', 'N/A')],
            ['Atividade', self.dados.get('atividade', 'N/A')],
        ]

        tabela = Table(dados_identificacao, colWidths=[6*cm, 10*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COR_TEXTO),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.story.append(tabela)
        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_entrega(self):
        """Cria a seção de entrega esperada"""
        self.story.append(Paragraph("2. ENTREGA ESPERADA", self.styles['TituloSecao']))

        entrega = self.dados.get('entrega_esperada', 'Não especificado')
        texto_entrega = Paragraph(entrega, self.styles['CorpoTexto'])
        self.story.append(texto_entrega)
        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_normas(self):
        """Cria a seção de dispositivos normativos"""
        self.story.append(Paragraph("3. DISPOSITIVOS NORMATIVOS", self.styles['TituloSecao']))

        normas = self.dados.get('dispositivos_normativos', [])
        if normas:
            for i, norma in enumerate(normas, 1):
                if isinstance(norma, dict):
                    norma_texto = norma.get('norma', str(norma))
                else:
                    norma_texto = str(norma)
                item = Paragraph(f"• {norma_texto}", self.styles['ItemLista'])
                self.story.append(item)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_operadores(self):
        """Cria a seção de operadores"""
        self.story.append(Paragraph("4. OPERADORES", self.styles['TituloSecao']))

        operadores = self.dados.get('operadores', [])
        if operadores:
            for operador in operadores:
                item = Paragraph(f"• {operador}", self.styles['ItemLista'])
                self.story.append(item)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_sistemas(self):
        """Cria a seção de sistemas"""
        self.story.append(Paragraph("5. SISTEMAS UTILIZADOS", self.styles['TituloSecao']))

        sistemas = self.dados.get('sistemas', [])
        if sistemas:
            for sistema in sistemas:
                item = Paragraph(f"• {sistema}", self.styles['ItemLista'])
                self.story.append(item)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_documentos(self):
        """Cria a seção de documentos"""
        self.story.append(Paragraph("6. DOCUMENTOS, FORMULÁRIOS E MODELOS", self.styles['TituloSecao']))

        documentos = self.dados.get('documentos', [])
        if documentos and len(documentos) > 0:
            # Criar tabela de documentos
            dados_docs = [['Tipo', 'Descrição', 'Uso', 'Obrigatório', 'Sistema']]

            for doc in documentos:
                if isinstance(doc, dict):
                    tipo = doc.get('tipo_documento', 'N/A')
                    descricao = doc.get('descricao', 'N/A')
                    uso = doc.get('tipo_uso', 'N/A')
                    obrigatorio = 'Sim' if doc.get('obrigatorio', False) else 'Não'
                    sistema = doc.get('sistema', '-')
                    dados_docs.append([tipo, descricao, uso, obrigatorio, sistema or '-'])
                else:
                    dados_docs.append(['Documento', str(doc), '-', '-', '-'])

            tabela_docs = Table(dados_docs, colWidths=[3*cm, 6*cm, 2.5*cm, 2.5*cm, 2*cm])
            tabela_docs.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.COR_PRIMARIA),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            self.story.append(tabela_docs)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_fluxos(self):
        """Cria a seção de fluxos de informação"""
        self.story.append(Paragraph("7. FLUXOS DE INFORMAÇÃO", self.styles['TituloSecao']))

        # Fluxos de entrada
        self.story.append(Paragraph("7.1. Entradas", self.styles['SubtituloSecao']))
        fluxos_entrada = self.dados.get('fluxos_entrada', [])
        if fluxos_entrada:
            for fluxo in fluxos_entrada:
                item = Paragraph(f"• {fluxo}", self.styles['ItemLista'])
                self.story.append(item)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.3*cm))

        # Fluxos de saída
        self.story.append(Paragraph("7.2. Saídas", self.styles['SubtituloSecao']))
        fluxos_saida = self.dados.get('fluxos_saida', [])
        if fluxos_saida:
            for fluxo in fluxos_saida:
                item = Paragraph(f"• {fluxo}", self.styles['ItemLista'])
                self.story.append(item)
        else:
            self.story.append(Paragraph("Não especificado", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def _criar_secao_pontos_atencao(self):
        """Cria a seção de pontos de atenção"""
        self.story.append(Paragraph("8. PONTOS DE ATENÇÃO", self.styles['TituloSecao']))

        pontos = self.dados.get('pontos_atencao', '')
        if pontos and pontos.strip():
            # Destaque especial para pontos de atenção
            tabela_alerta = Table([[pontos]], colWidths=[16*cm])
            tabela_alerta.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFF3CD')),
                ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#856404')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOX', (0, 0), (-1, -1), 2, HexColor('#FFC107')),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            self.story.append(tabela_alerta)
        else:
            self.story.append(Paragraph("Não há pontos especiais de atenção.", self.styles['CorpoTexto']))

        self.story.append(Spacer(1, 0.5*cm))

    def gerar_pdf(self) -> BytesIO:
        """
        Gera o PDF completo do POP

        Returns:
            BytesIO: Buffer contendo o PDF gerado
        """
        # Criar capa
        self._criar_capa()

        # Criar todas as seções
        self._criar_secao_identificacao()
        self._criar_secao_entrega()
        self._criar_secao_normas()
        self._criar_secao_operadores()
        self._criar_secao_sistemas()
        self._criar_secao_documentos()
        self._criar_secao_fluxos()
        self._criar_secao_pontos_atencao()

        # Construir o documento
        self.doc.build(self.story)

        # Retornar buffer no início
        self.buffer.seek(0)
        return self.buffer


def gerar_pop_pdf(dados_pop: dict) -> BytesIO:
    """
    Função helper para gerar PDF do POP

    Args:
        dados_pop: Dicionário com os dados do POP

    Returns:
        BytesIO: Buffer contendo o PDF gerado
    """
    gerador = POPPDFGenerator(dados_pop)
    return gerador.gerar_pdf()
