"""
Utilitários do MapaGov - Versão 2.1
Funções auxiliares para o sistema de Governança, Riscos e Conformidade
Correções: Paginação PDF, Metadados, QR Code funcional
"""

import re
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import unicodedata
from pathlib import Path

# Imports para geração de PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfgen import canvas as reportlab_canvas
import qrcode
from io import BytesIO


class ValidadorUtils:
    """Utilitários para validação de dados"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        if cpf == cpf[0] * 11:
            return False
        
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != dv1:
            return False
        
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        return int(cpf[10]) == dv2
    
    @staticmethod
    def validar_siape(siape: str) -> bool:
        """Valida matrícula SIAPE (7 dígitos)"""
        siape = re.sub(r'[^0-9]', '', siape)
        return len(siape) == 7 and siape.isdigit()
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validar_nome_processo(nome: str) -> Tuple[bool, str]:
        """Valida nome de processo (mínimo 10 caracteres, máximo 200)"""
        nome = nome.strip()
        if len(nome) < 10:
            return False, "Nome deve ter pelo menos 10 caracteres"
        if len(nome) > 200:
            return False, "Nome deve ter no máximo 200 caracteres"
        if not re.match(r'^[a-zA-ZÀ-ÿ0-9\s\-.,()]+$', nome):
            return False, "Nome contém caracteres inválidos"
        return True, "Válido"


class FormatadorUtils:
    """Utilitários para formatação de dados"""
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata CPF para exibição (XXX.XXX.XXX-XX)"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def formatar_siape(siape: str) -> str:
        """Formata SIAPE para exibição"""
        siape = re.sub(r'[^0-9]', '', siape)
        return siape.zfill(7) if siape else ""
    
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Remove acentos e caracteres especiais"""
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
        return texto.lower()
    
    @staticmethod
    def formatar_data_brasileiro(data: datetime) -> str:
        """Formata data no padrão brasileiro (DD/MM/AAAA HH:MM)"""
        return data.strftime("%d/%m/%Y %H:%M")
    
    @staticmethod
    def limpar_texto_sistema(texto: str) -> str:
        """Remove caracteres problemáticos para uso em sistemas"""
        texto = re.sub(r'\n\s*\n', '\n', texto)
        texto = re.sub(r' +', ' ', texto)
        return texto.strip()


class CodigoUtils:
    """Utilitários para geração e validação de códigos"""
    
    AREAS_PREFIXOS = {
        "CGBEN": "1", "CGPAG": "2", "COATE": "3", "CGGAF": "4",
        "DIGEP": "5", "CGRIS": "6", "CGCAF": "7", "CGECO": "8"
    }
    
    @staticmethod
    def gerar_codigo_processo(area_codigo: str, sequencial: Optional[int] = None) -> str:
        """
        Gera código de processo baseado na área
        Formato: PREFIXO.MACROPROCESSO.PROCESSO.ATIVIDADE
        """
        prefixo = CodigoUtils.AREAS_PREFIXOS.get(area_codigo, "X")
        
        if sequencial is None:
            sequencial = 1
        
        return f"{prefixo}.1.1.{sequencial}"
    
    @staticmethod
    def validar_codigo_processo(codigo: str) -> bool:
        """Valida formato do código de processo"""
        pattern = r'^[1-8]\.(\d+)\.(\d+)\.(\d+)$'
        return re.match(pattern, codigo) is not None
    
    @staticmethod
    def extrair_componentes_codigo(codigo: str) -> Dict[str, str]:
        """Extrai componentes do código de processo"""
        match = re.match(r'^([1-8])\.(\d+)\.(\d+)\.(\d+)$', codigo)
        if match:
            return {
                "area": match.group(1),
                "macroprocesso": match.group(2),
                "processo": match.group(3),
                "atividade": match.group(4)
            }
        return {}


class ArquivoUtils:
    """Utilitários para manipulação de arquivos"""
    
    @staticmethod
    def criar_diretorio_seguro(caminho: str) -> bool:
        """Cria diretório se não existir"""
        try:
            Path(caminho).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar diretório {caminho}: {e}")
            return False
    
    @staticmethod
    def gerar_nome_arquivo_seguro(nome_base: str, extensao: str = "txt") -> str:
        """Gera nome de arquivo seguro removendo caracteres problemáticos"""
        nome_limpo = re.sub(r'[<>:"/\\|?*]', '_', nome_base)
        nome_limpo = nome_limpo.strip('. ')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{nome_limpo}_{timestamp}.{extensao}"
    
    @staticmethod
    def calcular_hash_arquivo(caminho_arquivo: str) -> Optional[str]:
        """Calcula hash MD5 de um arquivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(caminho_arquivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Erro ao calcular hash: {e}")
            return None


class ConfigUtils:
    """Utilitários para configuração do sistema"""
    
    @staticmethod
    def carregar_config(arquivo: str = "config.json") -> Dict[str, Any]:
        """Carrega configurações do arquivo JSON"""
        try:
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config: {e}")
        
        return {
            "version": "1.0.0",
            "debug": False,
            "max_upload_size": 10485760,
            "allowed_extensions": [".pdf", ".docx", ".txt"],
            "helena": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "timeout": 30
            }
        }
    
    @staticmethod
    def salvar_config(config: Dict[str, Any], arquivo: str = "config.json") -> bool:
        """Salva configurações no arquivo JSON"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
            return False


class LogUtils:
    """Utilitários para logging do sistema"""
    
    @staticmethod
    def criar_log_entrada(usuario: str, acao: str, dados: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria entrada de log estruturada"""
        return {
            "timestamp": datetime.now().isoformat(),
            "usuario": usuario,
            "acao": acao,
            "dados": dados or {},
            "ip": "127.0.0.1",
            "user_agent": "MapaGov/1.0"
        }
    
    @staticmethod
    def log_helena_interacao(usuario: str, pergunta: str, resposta: str, estado: str) -> Dict[str, Any]:
        """Log específico para interações com Helena"""
        return LogUtils.criar_log_entrada(
            usuario=usuario,
            acao="helena_interacao",
            dados={
                "pergunta": pergunta[:200] if pergunta else "",
                "resposta_size": len(resposta) if resposta else 0,
                "estado": estado,
                "sucesso": True
            }
        )


class SegurancaUtils:
    """Utilitários para segurança e sanitização"""
    
    @staticmethod
    def sanitizar_entrada_usuario(texto: str) -> str:
        """Sanitiza entrada do usuário removendo conteúdo perigoso"""
        texto = re.sub(r'<[^>]+>', '', texto)
        texto = ''.join(char for char in texto if ord(char) >= 32 or char in '\n\r\t')
        
        if len(texto) > 5000:
            texto = texto[:5000] + "..."
        
        return texto.strip()
    
    @staticmethod
    def verificar_conteudo_suspeito(texto: str) -> List[str]:
        """Verifica se há conteúdo potencialmente suspeito"""
        alertas = []
        
        padroes_suspeitos = [
            (r'<script[^>]*>', "Tag script detectada"),
            (r'javascript:', "JavaScript detectado"),
            (r'eval\s*\(', "Função eval detectada"),
            (r'document\.', "Acesso ao DOM detectado")
        ]
        
        for padrao, descricao in padroes_suspeitos:
            if re.search(padrao, texto, re.IGNORECASE):
                alertas.append(descricao)
        
        return alertas


class HelenaUtils:
    """Utilitários específicos para Helena"""
    
    @staticmethod
    def extrair_sistemas_texto(texto: str, sistemas_disponiveis: List[str]) -> List[str]:
        """Extrai sistemas mencionados em texto livre"""
        sistemas_encontrados = []
        texto_normalizado = HelenaUtils.normalizar_para_busca(texto)
        
        for sistema in sistemas_disponiveis:
            sistema_normalizado = HelenaUtils.normalizar_para_busca(sistema)
            
            if (sistema_normalizado in texto_normalizado or 
                sistema.upper() in texto.upper() or
                sistema.lower() in texto.lower()):
                sistemas_encontrados.append(sistema)
        
        return sistemas_encontrados
    
    @staticmethod
    def normalizar_para_busca(texto: str) -> str:
        """Normaliza texto para facilitar busca"""
        texto = FormatadorUtils.normalizar_texto(texto)
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        return ' '.join(texto.split())
    
    @staticmethod
    def detectar_intencao_finalizacao(texto: str) -> bool:
        """Detecta se usuário quer finalizar etapa"""
        palavras_finalizacao = [
            'não', 'nao', 'fim', 'finalizar', 'terminar', 'acabou',
            'não há mais', 'nao ha mais', 'só isso', 'so isso'
        ]
        
        texto_limpo = texto.lower().strip()
        return any(palavra in texto_limpo for palavra in palavras_finalizacao)
    
    @staticmethod
    def gerar_resumo_dados(dados: Dict[str, Any]) -> str:
        """Gera resumo textual dos dados coletados"""
        resumo_parts = []
        
        if dados.get('nome_processo'):
            resumo_parts.append(f"Processo: {dados['nome_processo']}")
        
        if dados.get('area', {}).get('nome'):
            resumo_parts.append(f"Área: {dados['area']['nome']}")
        
        if dados.get('sistemas'):
            sistemas = ', '.join(dados['sistemas'][:3])
            if len(dados['sistemas']) > 3:
                sistemas += f" (e mais {len(dados['sistemas']) - 3})"
            resumo_parts.append(f"Sistemas: {sistemas}")
        
        if dados.get('etapas'):
            resumo_parts.append(f"Etapas: {len(dados['etapas'])} mapeadas")
        
        return " | ".join(resumo_parts) if resumo_parts else "Dados não disponíveis"


class EstadoUtils:
    """Utilitários para gerenciamento de estado da conversa"""
    
    FLUXO_ESTADOS = ['nome', 'area', 'sistemas', 'campos', 'etapas', 'fluxos', 'revisao']
    
    @staticmethod
    def proximo_estado(estado_atual: str) -> str:
        """Retorna próximo estado no fluxo"""
        try:
            indice_atual = EstadoUtils.FLUXO_ESTADOS.index(estado_atual)
            if indice_atual < len(EstadoUtils.FLUXO_ESTADOS) - 1:
                return EstadoUtils.FLUXO_ESTADOS[indice_atual + 1]
        except ValueError:
            pass
        return estado_atual
    
    @staticmethod
    def calcular_progresso_percentual(estado: str, dados: Dict[str, Any]) -> int:
        """Calcula progresso em percentual"""
        try:
            indice = EstadoUtils.FLUXO_ESTADOS.index(estado)
            base = int((indice / len(EstadoUtils.FLUXO_ESTADOS)) * 100)
            
            if estado == 'campos' and dados.get('campos_coletados', 0) > 0:
                campos_total = 7
                campos_atual = dados.get('campos_coletados', 0)
                ajuste = int((campos_atual / campos_total) * 15)
                base += ajuste
            
            return min(base, 100)
        except ValueError:
            return 0


class PDFGenerator:
    """
    Gerador de PDF para Procedimentos Operacionais Padrão (POP)
    Versão 2.1 - Com paginação corrigida, metadados e QR Code funcional
    """
    
    COR_AZUL_GOVBR = colors.HexColor('#1351B4')
    COR_AZUL_CLARO = colors.HexColor('#F0F4FF')
    COR_CINZA_CLARO = colors.HexColor('#F8F8F8')
    
    def __init__(self):
        """Inicializa gerador com configurações padrão"""
        self.estilos = self._criar_estilos()
        self.largura_pagina, self.altura_pagina = A4
        
    def _criar_estilos(self) -> Dict[str, ParagraphStyle]:
        """Cria estilos personalizados para o PDF"""
        estilos_base = getSampleStyleSheet()
        
        estilos_customizados = {
            'titulo_capa': ParagraphStyle(
                'titulo_capa',
                parent=estilos_base['Heading1'],
                fontSize=32,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName='Helvetica-Bold',
                leading=38
            ),
            'subtitulo_capa': ParagraphStyle(
                'subtitulo_capa',
                parent=estilos_base['Normal'],
                fontSize=18,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName='Helvetica',
                leading=22
            ),
            'titulo_secao': ParagraphStyle(
                'titulo_secao',
                parent=estilos_base['Heading2'],
                fontSize=14,
                textColor=self.COR_AZUL_GOVBR,
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                backColor=self.COR_AZUL_CLARO,
                borderPadding=(10, 10, 10, 10),
                leading=18
            ),
            'texto_normal': ParagraphStyle(
                'texto_normal',
                parent=estilos_base['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=10,
                fontName='Helvetica',
                leading=14
            ),
            'texto_identificacao': ParagraphStyle(
                'texto_identificacao',
                parent=estilos_base['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                spaceAfter=6,
                fontName='Helvetica',
                leading=12
            ),
            'lista_item': ParagraphStyle(
                'lista_item',
                parent=estilos_base['Normal'],
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=8,
                leftIndent=20,
                fontName='Helvetica',
                leading=14
            )
        }
        
        return estilos_customizados
    
    def _gerar_qr_code(self, url: str) -> Optional[Image]:
        """Gera QR Code para URL do processo"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            img_reportlab = Image(buffer, width=3*cm, height=3*cm)
            return img_reportlab
            
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")
            return None
    
    def _adicionar_rodape(self, canvas: reportlab_canvas.Canvas, doc) -> None:
        """Adiciona rodapé personalizado em cada página (exceto capa)"""
        if canvas.getPageNumber() == 1:
            return
        
        canvas.saveState()
        
        # Linha decorativa azul
        canvas.setStrokeColor(self.COR_AZUL_GOVBR)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 2*cm, self.largura_pagina - 2*cm, 2*cm)
        
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        
        # Código do processo (esquerda)
        codigo = getattr(doc, 'codigo_processo', '[Código]')
        canvas.drawString(2*cm, 1.5*cm, codigo)
        
        # Número da página (centro) - SEM total de páginas
        # Subtrai 1 porque a capa não conta
        pagina_atual = canvas.getPageNumber() - 1
        texto_pagina = f"Pág. {pagina_atual}"
        largura_texto = canvas.stringWidth(texto_pagina, 'Helvetica', 9)
        canvas.drawString(
            (self.largura_pagina - largura_texto) / 2,
            1.5*cm,
            texto_pagina
        )
        
        # Data de geração (direita)
        data_geracao = datetime.now().strftime("%d/%m/%Y")
        texto_data = f"Gerado pelo MapaGov em {data_geracao}"
        largura_data = canvas.stringWidth(texto_data, 'Helvetica', 9)
        canvas.drawString(
            self.largura_pagina - 2*cm - largura_data,
            1.5*cm,
            texto_data
        )
        
        canvas.restoreState()
    
    def _gerar_capa(self, dados: Dict[str, Any], url_base: Optional[str] = None) -> List:
        """Gera elementos da página de capa"""
        elementos = []
        
        # Espaço superior
        elementos.append(Spacer(1, 6*cm))
        
        # Título principal
        titulo = Paragraph(
            "PROCEDIMENTO<br/>OPERACIONAL<br/>PADRÃO",
            self.estilos['titulo_capa']
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 2*cm))
        
        # Nome do processo
        nome_processo = dados.get('nome_processo', '[Nome do Processo]')
        subtitulo = Paragraph(
            nome_processo.upper(),
            self.estilos['subtitulo_capa']
        )
        elementos.append(subtitulo)
        elementos.append(Spacer(1, 1*cm))
        
        # Código do processo e área (novo)
        codigo = dados.get('codigo_processo', 'X.X.X.X')
        area = dados.get('area', {}).get('nome', '[Área não informada]')
        
        info_processo = Paragraph(
            f"<b>Código:</b> {codigo}<br/><b>Área:</b> {area}",
            self.estilos['subtitulo_capa']
        )
        elementos.append(info_processo)
        elementos.append(Spacer(1, 4*cm))
        
        # Texto explicativo do QR Code (novo)
        texto_qr = Paragraph(
            "Escaneie para acessar versão digital",
            ParagraphStyle(
                'texto_qr',
                parent=self.estilos['subtitulo_capa'],
                fontSize=12,
                alignment=TA_CENTER
            )
        )
        elementos.append(texto_qr)
        elementos.append(Spacer(1, 0.5*cm))
        
        # QR Code com URL funcional
        codigo_processo = dados.get('codigo_processo', 'xxxx')
        if url_base:
            url_processo = f"{url_base}/pop/{codigo_processo}"
        else:
            # URL padrão caso não seja fornecida
            url_processo = f"https://mapagov.app/pop/{codigo_processo}"
        
        qr_img = self._gerar_qr_code(url_processo)
        if qr_img:
            elementos.append(qr_img)
        
        # Data de geração (novo)
        elementos.append(Spacer(1, 0.5*cm))
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        texto_data = Paragraph(
            f"Gerado em {data_geracao}",
            ParagraphStyle(
                'texto_data_capa',
                parent=self.estilos['subtitulo_capa'],
                fontSize=10,
                alignment=TA_CENTER
            )
        )
        elementos.append(texto_data)
        
        # Quebra de página
        elementos.append(PageBreak())
        
        return elementos
    
    def _gerar_identificacao(self, dados: Dict[str, Any]) -> List:
        """Gera página de identificação do processo"""
        elementos = []
        
        elementos.append(Paragraph("IDENTIFICAÇÃO DO PROCESSO", self.estilos['titulo_secao']))
        elementos.append(Spacer(1, 0.5*cm))
        
        codigo = dados.get('codigo_processo', '[Não informado]')
        data_aprovacao = dados.get('data_aprovacao', datetime.now().strftime("%m/%Y"))
        versao = dados.get('versao', '1.0')
        
        dados_identificacao = [
            f"<b>Código na arquitetura:</b> {codigo}",
            f"<b>Data de Aprovação:</b> {data_aprovacao}",
            f"<b>Versão:</b> {versao}",
            "",
            f"<b>MACROPROCESSO:</b> {dados.get('macroprocesso', '[Não informado]')}",
            f"<b>PROCESSO:</b> {dados.get('processo_especifico', '[Não informado]')}",
            f"<b>SUBPROCESSO:</b> {dados.get('subprocesso', '[Não informado]')}",
            f"<b>ATIVIDADE:</b> {dados.get('nome_processo', '[Não informado]')}"
        ]
        
        for linha in dados_identificacao:
            elementos.append(Paragraph(linha, self.estilos['texto_identificacao']))
        
        elementos.append(PageBreak())
        
        return elementos
    
    def _gerar_sumario(self) -> List:
        """Gera sumário automático do documento"""
        elementos = []
        
        elementos.append(Paragraph("SUMÁRIO", self.estilos['titulo_secao']))
        elementos.append(Spacer(1, 0.5*cm))
        
        itens_sumario = [
            "1. ENTREGA ESPERADA DA ATIVIDADE",
            "2. DISPOSITIVOS NORMATIVOS APLICÁVEIS",
            "3. SISTEMAS UTILIZADOS / ACESSOS NECESSÁRIOS",
            "4. OPERADORES DA ATIVIDADE",
            "5. TAREFAS REALIZADAS NA ATIVIDADE",
            "6. DOCUMENTOS, FORMULÁRIOS E MODELOS UTILIZADOS",
            "7. PONTOS GERAIS DE ATENÇÃO NA ATIVIDADE"
        ]
        
        for item in itens_sumario:
            elementos.append(Paragraph(item, self.estilos['lista_item']))
        
        elementos.append(PageBreak())
        
        return elementos
    
    def _gerar_secao_conteudo(self, titulo: str, conteudo: Any) -> List:
        """Gera uma seção de conteúdo formatada"""
        elementos = []
        
        elementos.append(Paragraph(titulo, self.estilos['titulo_secao']))
        elementos.append(Spacer(1, 0.3*cm))
        
        if isinstance(conteudo, str):
            if conteudo.strip():
                elementos.append(Paragraph(conteudo, self.estilos['texto_normal']))
            else:
                elementos.append(Paragraph("[Não informado]", self.estilos['texto_normal']))
                
        elif isinstance(conteudo, list):
            if conteudo:
                for item in conteudo:
                    if isinstance(item, dict):
                        numero = item.get('numero', '')
                        descricao = item.get('descricao', '')
                        texto = f"<b>{numero}.</b> {descricao}"
                        elementos.append(Paragraph(texto, self.estilos['lista_item']))
                    else:
                        elementos.append(Paragraph(f"• {str(item)}", self.estilos['lista_item']))
            else:
                elementos.append(Paragraph("[Nenhum item informado]", self.estilos['texto_normal']))
        
        elementos.append(Spacer(1, 0.5*cm))

        return elementos

    def _gerar_secao_etapas(self, etapas: list) -> List:
        """Gera seção 5. TAREFAS com formatação rica (operador, sistemas, cenários)."""
        elementos = []
        elementos.append(Paragraph("5. TAREFAS REALIZADAS NA ATIVIDADE", self.estilos['titulo_secao']))
        elementos.append(Spacer(1, 0.3*cm))

        if not etapas:
            elementos.append(Paragraph("[Nenhuma etapa mapeada]", self.estilos['texto_normal']))
            elementos.append(Spacer(1, 0.5*cm))
            return elementos

        for etapa in etapas:
            if not isinstance(etapa, dict):
                elementos.append(Paragraph(f"• {str(etapa)}", self.estilos['lista_item']))
                continue

            numero = etapa.get('numero', '')
            descricao = etapa.get('descricao', '[Sem descrição]')
            is_condicional = etapa.get('tipo') == 'condicional'

            # Título da etapa
            titulo_etapa = f"<b>Etapa {numero}:</b> {descricao}"
            if is_condicional:
                titulo_etapa += " <i>[CONDICIONAL]</i>"
            elementos.append(Paragraph(titulo_etapa, self.estilos['lista_item']))

            # Operador
            operador = etapa.get('operador_nome', '')
            if operador:
                elementos.append(Paragraph(f"    Operador: {operador}", self.estilos['texto_normal']))

            # Sistemas
            sistemas = etapa.get('sistemas', [])
            if sistemas:
                elementos.append(Paragraph(f"    Sistemas: {', '.join(sistemas)}", self.estilos['texto_normal']))

            # Docs requeridos
            docs_req = etapa.get('docs_requeridos', [])
            if docs_req:
                elementos.append(Paragraph(f"    Docs requeridos: {', '.join(docs_req)}", self.estilos['texto_normal']))

            # Docs gerados
            docs_ger = etapa.get('docs_gerados', [])
            if docs_ger:
                elementos.append(Paragraph(f"    Docs gerados: {', '.join(docs_ger)}", self.estilos['texto_normal']))

            # Tempo estimado
            tempo = etapa.get('tempo_estimado')
            if tempo:
                elementos.append(Paragraph(f"    Tempo estimado: {tempo}", self.estilos['texto_normal']))

            if is_condicional:
                # Antes da decisão
                antes = etapa.get('antes_decisao')
                if antes:
                    desc_antes = antes.get('descricao', '') if isinstance(antes, dict) else str(antes)
                    if desc_antes:
                        elementos.append(Paragraph(f"    Antes da decisão: {desc_antes}", self.estilos['texto_normal']))

                # Cenários
                cenarios = etapa.get('cenarios', [])
                for cenario in cenarios:
                    if not isinstance(cenario, dict):
                        continue
                    c_num = cenario.get('numero', '')
                    c_desc = cenario.get('descricao', '')
                    elementos.append(Paragraph(
                        f"    <b>Cenário {c_num} - {c_desc}:</b>",
                        self.estilos['texto_normal']
                    ))
                    for sub in cenario.get('subetapas', []):
                        if isinstance(sub, dict):
                            elementos.append(Paragraph(
                                f"        {sub.get('numero', '')} {sub.get('descricao', '')}",
                                self.estilos['texto_normal']
                            ))
            else:
                # Detalhes (etapa linear)
                detalhes = etapa.get('detalhes', [])
                for det in detalhes:
                    elementos.append(Paragraph(f"    • {det}", self.estilos['texto_normal']))

            elementos.append(Spacer(1, 0.2*cm))

        elementos.append(Spacer(1, 0.3*cm))
        return elementos

    def _gerar_controle_revisoes(self, dados: Dict[str, Any]) -> List:
        """Gera tabela de controle de revisões"""
        elementos = []
        
        elementos.append(PageBreak())
        elementos.append(Paragraph("CONTROLE DE REVISÕES", self.estilos['titulo_secao']))
        elementos.append(Spacer(1, 0.5*cm))
        
        nome_usuario = dados.get('nome_usuario', '[Usuário]')
        data_criacao = dados.get('data_criacao', datetime.now().strftime("%d/%m/%Y"))
        
        info_controle = [
            f"<b>Elaborado por:</b> {nome_usuario}",
            f"<b>Aprovado por:</b> [Pendente]",
            f"<b>Em:</b> {data_criacao}"
        ]
        
        for linha in info_controle:
            elementos.append(Paragraph(linha, self.estilos['texto_identificacao']))
        
        elementos.append(Spacer(1, 1*cm))
        
        dados_tabela = [
            ['Nº REV', 'DATA', 'ITEM REVISADO', 'REVISADO POR'],
            ['1.0', data_criacao, 'Criação inicial', nome_usuario]
        ]
        
        tabela = Table(dados_tabela, colWidths=[3*cm, 3*cm, 7*cm, 5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COR_AZUL_GOVBR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, self.COR_AZUL_GOVBR),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elementos.append(tabela)
        
        return elementos
    
    def gerar_pop_completo(self, dados: Dict[str, Any], nome_arquivo: str, url_base: Optional[str] = None) -> Optional[str]:
        """
        Gera PDF completo do POP
        
        Args:
            dados: Dict com estrutura completa do processo
            nome_arquivo: Nome do arquivo PDF a ser gerado
            url_base: URL base do sistema para gerar QR Code funcional (opcional)
                      Ex: "https://mapagov.app" gerará "https://mapagov.app/pop/2.3.3.1"
        
        Returns:
            str: Caminho completo do arquivo gerado ou None em caso de erro
        """
        try:
            if not dados.get('nome_processo'):
                print("Erro: nome_processo é obrigatório")
                return None
            
            diretorio_pdf = os.path.join(os.getcwd(), 'media', 'pdfs')
            ArquivoUtils.criar_diretorio_seguro(diretorio_pdf)
            
            caminho_completo = os.path.join(diretorio_pdf, nome_arquivo)
            
            doc = SimpleDocTemplate(
                caminho_completo,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=3*cm
            )
            
            # Adicionar metadados ao PDF
            doc.title = dados.get('nome_processo', 'Procedimento Operacional Padrão')
            doc.author = dados.get('nome_usuario', 'MapaGov')
            doc.subject = f"Procedimento Operacional Padrão - {dados.get('codigo_processo', '')}"
            doc.creator = "MapaGov - Sistema de Governança, Riscos e Conformidade"
            doc.keywords = "POP, Procedimento, Processo, Governança, Setor Público, DECIPEX"
            
            # Armazenar código do processo para uso no rodapé
            doc.codigo_processo = dados.get('codigo_processo', '[Código]')
            
            elementos = []
            
            # CAPA
            elementos.extend(self._gerar_capa(dados, url_base))
            
            # IDENTIFICAÇÃO
            elementos.extend(self._gerar_identificacao(dados))
            
            # SUMÁRIO
            elementos.extend(self._gerar_sumario())
            
            # SEÇÕES DE CONTEÚDO
            entrega = dados.get('entrega_esperada', '[Não informado]')
            elementos.extend(self._gerar_secao_conteudo(
                "1. ENTREGA ESPERADA DA ATIVIDADE",
                entrega
            ))
            
            dispositivos = dados.get('dispositivos_normativos', '[Não informado]')
            elementos.extend(self._gerar_secao_conteudo(
                "2. DISPOSITIVOS NORMATIVOS APLICÁVEIS",
                dispositivos
            ))
            
            sistemas = dados.get('sistemas', [])
            sistemas_texto = "\n".join([f"• {s}" for s in sistemas]) if sistemas else "[Nenhum sistema informado]"
            elementos.extend(self._gerar_secao_conteudo(
                "3. SISTEMAS UTILIZADOS / ACESSOS NECESSÁRIOS",
                sistemas_texto
            ))

            operadores = dados.get('operadores', '[Não informado]')
            # Converter lista para texto formatado
            if isinstance(operadores, list):
                operadores = "\n".join([f"• {op}" for op in operadores]) if operadores else "[Nenhum operador informado]"
            elementos.extend(self._gerar_secao_conteudo(
                "4. OPERADORES DA ATIVIDADE",
                operadores
            ))
            
            etapas = dados.get('etapas', [])
            elementos.extend(self._gerar_secao_etapas(etapas))
            
            documentos = dados.get('documentos_utilizados', '[Não informado]')
            elementos.extend(self._gerar_secao_conteudo(
                "6. DOCUMENTOS, FORMULÁRIOS E MODELOS UTILIZADOS",
                documentos
            ))
            
            pontos = dados.get('pontos_atencao', '[Não informado]')
            elementos.extend(self._gerar_secao_conteudo(
                "7. PONTOS GERAIS DE ATENÇÃO NA ATIVIDADE",
                pontos
            ))
            
            # CONTROLE DE REVISÕES
            elementos.extend(self._gerar_controle_revisoes(dados))
            
            def adicionar_elementos_capa(canvas, doc):
                """Adiciona fundo azul na primeira página"""
                if canvas.getPageNumber() == 1:
                    canvas.saveState()
                    canvas.setFillColor(self.COR_AZUL_GOVBR)
                    canvas.rect(0, 0, self.largura_pagina, self.altura_pagina, fill=1, stroke=0)
                    
                    canvas.setFillColor(colors.HexColor('#1E5FBF'))
                    canvas.setStrokeColor(colors.HexColor('#1E5FBF'))
                    canvas.setLineWidth(1)
                    
                    for i in range(0, int(self.largura_pagina), 50):
                        for j in range(0, int(self.altura_pagina), 50):
                            canvas.circle(i, j, 15, stroke=1, fill=0)
                    
                    canvas.restoreState()
                else:
                    self._adicionar_rodape(canvas, doc)
            
            doc.build(elementos, onFirstPage=adicionar_elementos_capa, onLaterPages=adicionar_elementos_capa)
            
            print(f"✅ PDF gerado com sucesso: {caminho_completo}")
            return caminho_completo
            
        except Exception as e:
            print(f"❌ Erro ao gerar PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


class BaseLegalSuggestor:
    """
    Sugestor de Base Legal para processos do setor público
    Utiliza biblioteca estática com fallback para IA semântica
    """
    
    def __init__(self):
        """Inicializa sugestor com biblioteca de normas"""
        self.biblioteca = self._carregar_biblioteca()
        
    def _carregar_biblioteca(self) -> Dict[str, Any]:
        """Carrega biblioteca estática de 50 normas fundamentais"""
        biblioteca = {
            "normas": [
                # Assistência à Saúde
                {
                    "id": "norm_001",
                    "nome_curto": "IN 97/2022",
                    "nome_completo": "Instrução Normativa SGP/SEDGG/ME nº 97, de 26 de dezembro de 2022",
                    "artigos": "Art. 34-42",
                    "palavras_chave": ["ressarcimento", "aposentado", "plano saude", "auxilio saude", "assistencia suplementar"],
                    "areas": ["CGBEN"],
                    "hierarquia": 3
                },
                {
                    "id": "norm_002",
                    "nome_curto": "Lei 8112/90",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 230",
                    "palavras_chave": ["servidor publico", "aposentadoria", "direitos", "regime juridico"],
                    "areas": ["todas"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_003",
                    "nome_curto": "Decreto 4978/2004",
                    "nome_completo": "Decreto nº 4.978, de 3 de fevereiro de 2004",
                    "artigos": "Todos",
                    "palavras_chave": ["assistencia saude", "servidor", "dependente", "plano saude"],
                    "areas": ["CGBEN"],
                    "hierarquia": 2
                },
                # Pagamento e Folha
                {
                    "id": "norm_004",
                    "nome_curto": "IN 02/2018",
                    "nome_completo": "Instrução Normativa SEGES/MPDG nº 2, de 30 de março de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["consignacao", "desconto", "folha pagamento", "margem consignavel"],
                    "areas": ["CGPAG"],
                    "hierarquia": 3
                },
                {
                    "id": "norm_005",
                    "nome_curto": "Lei 10520/2002",
                    "nome_completo": "Lei nº 10.520, de 17 de julho de 2002",
                    "artigos": "Todos",
                    "palavras_chave": ["pregao", "licitacao", "compras", "contratos"],
                    "areas": ["CGGAF"],
                    "hierarquia": 1
                },
                # Atendimento e Processos
                {
                    "id": "norm_006",
                    "nome_curto": "Lei 9784/99",
                    "nome_completo": "Lei nº 9.784, de 29 de janeiro de 1999",
                    "artigos": "Todos",
                    "palavras_chave": ["processo administrativo", "atendimento", "prazo", "devido processo legal"],
                    "areas": ["COATE", "todas"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_007",
                    "nome_curto": "Decreto 9094/2017",
                    "nome_completo": "Decreto nº 9.094, de 17 de julho de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["simplificacao", "atendimento", "usuario", "servico publico"],
                    "areas": ["COATE"],
                    "hierarquia": 2
                },
                # Gestão Financeira
                {
                    "id": "norm_008",
                    "nome_curto": "Lei 4320/64",
                    "nome_completo": "Lei nº 4.320, de 17 de março de 1964",
                    "artigos": "Todos",
                    "palavras_chave": ["orcamento", "contabilidade", "financeiro", "despesa", "receita"],
                    "areas": ["CGGAF", "CGECO"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_009",
                    "nome_curto": "LRF",
                    "nome_completo": "Lei Complementar nº 101, de 4 de maio de 2000",
                    "artigos": "Todos",
                    "palavras_chave": ["responsabilidade fiscal", "lrf", "gestao fiscal", "despesa pessoal"],
                    "areas": ["CGGAF", "CGECO"],
                    "hierarquia": 1
                },
                # Gestão de Pessoas
                {
                    "id": "norm_010",
                    "nome_curto": "Lei 8112/90 - Capacitação",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 87-101",
                    "palavras_chave": ["capacitacao", "treinamento", "desenvolvimento", "licenca capacitacao"],
                    "areas": ["DIGEP"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_011",
                    "nome_curto": "Decreto 9991/2019",
                    "nome_completo": "Decreto nº 9.991, de 28 de agosto de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["capacitacao", "desenvolvimento", "gestao pessoas", "politica nacional"],
                    "areas": ["DIGEP"],
                    "hierarquia": 2
                },
                # Riscos e Controles
                {
                    "id": "norm_012",
                    "nome_curto": "IN Conjunta 01/2016",
                    "nome_completo": "Instrução Normativa Conjunta CGU/MP nº 01, de 10 de maio de 2016",
                    "artigos": "Todos",
                    "palavras_chave": ["controles internos", "gestao riscos", "governanca", "integridade"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 3
                },
                {
                    "id": "norm_013",
                    "nome_curto": "Decreto 9203/2017",
                    "nome_completo": "Decreto nº 9.203, de 22 de novembro de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["governanca", "governanca publica", "gestao riscos", "accountability"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 2
                },
                # Dados e Cadastro
                {
                    "id": "norm_014",
                    "nome_curto": "LGPD",
                    "nome_completo": "Lei nº 13.709, de 14 de agosto de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["dados pessoais", "privacidade", "lgpd", "protecao dados", "cadastro"],
                    "areas": ["CGCAF", "todas"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_015",
                    "nome_curto": "Decreto 10046/2019",
                    "nome_completo": "Decreto nº 10.046, de 9 de outubro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["governanca dados", "compartilhamento dados", "interoperabilidade"],
                    "areas": ["CGCAF"],
                    "hierarquia": 2
                },
                # Contratos e Licitações
                {
                    "id": "norm_016",
                    "nome_curto": "Lei 14133/2021",
                    "nome_completo": "Lei nº 14.133, de 1º de abril de 2021",
                    "artigos": "Todos",
                    "palavras_chave": ["licitacao", "contratos", "nova lei licitacoes", "pregao", "dispensa"],
                    "areas": ["CGGAF"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_017",
                    "nome_curto": "IN 65/2021",
                    "nome_completo": "Instrução Normativa SEGES/ME nº 65, de 7 de julho de 2021",
                    "artigos": "Todos",
                    "palavras_chave": ["processo administrativo eletronico", "sei", "tramitacao", "documento digital"],
                    "areas": ["todas"],
                    "hierarquia": 3
                },
                # TCU
                {
                    "id": "norm_018",
                    "nome_curto": "Acórdão TCU 1078/2023",
                    "nome_completo": "Acórdão TCU nº 1078, de 2023",
                    "artigos": "Todos",
                    "palavras_chave": ["controles", "auditoria", "prestacao contas", "tcu"],
                    "areas": ["todas"],
                    "hierarquia": 4
                },
                {
                    "id": "norm_019",
                    "nome_curto": "IN TCU 84/2020",
                    "nome_completo": "Instrução Normativa TCU nº 84, de 22 de abril de 2020",
                    "artigos": "Todos",
                    "palavras_chave": ["governanca", "controles", "gestao riscos", "auditoria interna"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 4
                },
                # CGU
                {
                    "id": "norm_020",
                    "nome_curto": "Portaria CGU 909/2015",
                    "nome_completo": "Portaria CGU nº 909, de 16 de abril de 2015",
                    "artigos": "Todos",
                    "palavras_chave": ["controles internos", "auditoria", "cgu", "gestao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 3
                },
                # Transparência
                {
                    "id": "norm_021",
                    "nome_curto": "LAI",
                    "nome_completo": "Lei nº 12.527, de 18 de novembro de 2011",
                    "artigos": "Todos",
                    "palavras_chave": ["acesso informacao", "lai", "transparencia", "publicidade"],
                    "areas": ["todas"],
                    "hierarquia": 1
                },
                {
                    "id": "norm_022",
                    "nome_curto": "Decreto 7724/2012",
                    "nome_completo": "Decreto nº 7.724, de 16 de maio de 2012",
                    "artigos": "Todos",
                    "palavras_chave": ["acesso informacao", "transparencia", "sic", "esic"],
                    "areas": ["todas"],
                    "hierarquia": 2
                },
                # Licitações Antigas
                {
                    "id": "norm_023",
                    "nome_curto": "Lei 8666/93",
                    "nome_completo": "Lei nº 8.666, de 21 de junho de 1993",
                    "artigos": "Todos",
                    "palavras_chave": ["licitacao antiga", "contratos", "obras", "servicos"],
                    "areas": ["CGGAF"],
                    "hierarquia": 1
                },
                # Estatais
                {
                    "id": "norm_024",
                    "nome_curto": "Lei Estatais",
                    "nome_completo": "Lei nº 13.303, de 30 de junho de 2016",
                    "artigos": "Todos",
                    "palavras_chave": ["estatais", "empresas publicas", "governanca corporativa"],
                    "areas": ["todas"],
                    "hierarquia": 1
                },
                # Simplificação
                {
                    "id": "norm_025",
                    "nome_curto": "Decreto 11129/2022",
                    "nome_completo": "Decreto nº 11.129, de 11 de julho de 2022",
                    "artigos": "Todos",
                    "palavras_chave": ["simplificacao", "burocracia", "governanca", "eficiencia"],
                    "areas": ["todas"],
                    "hierarquia": 2
                },
                # Trabalho Remoto
                {
                    "id": "norm_026",
                    "nome_curto": "Portaria 424/2020",
                    "nome_completo": "Portaria SGP/SEDGG/ME nº 424, de 27 de março de 2020",
                    "artigos": "Todos",
                    "palavras_chave": ["trabalho remoto", "teletrabalho", "home office"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3
                },
                # Horário Flexível
                {
                    "id": "norm_027",
                    "nome_curto": "IN 05/2017",
                    "nome_completo": "Instrução Normativa SGP/MP nº 5, de 26 de maio de 2017",
                    "artigos": "Todos",
                    "palavras_chave": ["horario flexivel", "jornada trabalho", "banco horas"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3
                },
                # Controles Internos
                {
                    "id": "norm_028",
                    "nome_curto": "Portaria Interministerial 140/2006",
                    "nome_completo": "Portaria Interministerial MF/CGU/MP nº 140, de 16 de março de 2006",
                    "artigos": "Todos",
                    "palavras_chave": ["controles internos", "auditoria", "conformidade"],
                    "areas": ["CGRIS"],
                    "hierarquia": 3
                },
                # Inclusão
                {
                    "id": "norm_029",
                    "nome_curto": "Lei Inclusão",
                    "nome_completo": "Lei nº 13.146, de 6 de julho de 2015",
                    "artigos": "Todos",
                    "palavras_chave": ["pessoa deficiencia", "pcd", "inclusao", "acessibilidade"],
                    "areas": ["DIGEP", "todas"],
                    "hierarquia": 1
                },
                # Integridade
                {
                    "id": "norm_030",
                    "nome_curto": "Decreto 9739/2019",
                    "nome_completo": "Decreto nº 9.739, de 28 de março de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["medidas protetivas", "integridade", "combate corrupcao"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 2
                },
                # Segurança da Informação
                {
                    "id": "norm_031",
                    "nome_curto": "Portaria 443/2018",
                    "nome_completo": "Portaria GM/MD nº 443, de 28 de fevereiro de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["seguranca informacao", "dsic", "ciberseguranca"],
                    "areas": ["todas"],
                    "hierarquia": 3
                },
                # Lei Anticorrupção
                {
                    "id": "norm_032",
                    "nome_curto": "Lei Anticorrupção",
                    "nome_completo": "Lei nº 12.846, de 1º de agosto de 2013",
                    "artigos": "Todos",
                    "palavras_chave": ["lei anticorrupcao", "compliance", "integridade", "pessoa juridica"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 1
                },
                # Decreto Anticorrupção
                {
                    "id": "norm_033",
                    "nome_curto": "Decreto 8420/2015",
                    "nome_completo": "Decreto nº 8.420, de 18 de março de 2015",
                    "artigos": "Todos",
                    "palavras_chave": ["responsabilizacao empresas", "compliance", "acordos leniencia"],
                    "areas": ["CGRIS"],
                    "hierarquia": 2
                },
                # CNMP
                {
                    "id": "norm_034",
                    "nome_curto": "Resolução CNMP 201/2018",
                    "nome_completo": "Resolução CNMP nº 201, de 23 de outubro de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["compliance publico", "integridade", "programa conformidade"],
                    "areas": ["CGRIS", "todas"],
                    "hierarquia": 5
                },
                # Gestão de Processos
                {
                    "id": "norm_035",
                    "nome_curto": "Portaria 57/2019",
                    "nome_completo": "Portaria ME nº 57, de 4 de fevereiro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["gestao processos", "modelagem", "bpm", "mapeamento"],
                    "areas": ["todas"],
                    "hierarquia": 3
                },
                # TI
                {
                    "id": "norm_036",
                    "nome_curto": "IN 04/2014",
                    "nome_completo": "Instrução Normativa SLTI/MP nº 4, de 11 de setembro de 2014",
                    "artigos": "Todos",
                    "palavras_chave": ["contratacao ti", "software", "sistemas", "tecnologia"],
                    "areas": ["CGGAF"],
                    "hierarquia": 3
                },
                # Férias
                {
                    "id": "norm_037",
                    "nome_curto": "Portaria 778/2019",
                    "nome_completo": "Portaria SGP/SEDGG/ME nº 778, de 13 de junho de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["ferias", "recesso", "afastamento", "licencas"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3
                },
                # Carreira Universitária
                {
                    "id": "norm_038",
                    "nome_curto": "Lei 11091/2005",
                    "nome_completo": "Lei nº 11.091, de 12 de janeiro de 2005",
                    "artigos": "Todos",
                    "palavras_chave": ["carreira tecnico administrativa", "universidade", "ifes"],
                    "areas": ["DIGEP"],
                    "hierarquia": 1
                },
                # Revisão de Atos
                {
                    "id": "norm_039",
                    "nome_curto": "Decreto 10139/2019",
                    "nome_completo": "Decreto nº 10.139, de 28 de novembro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["revisao atos", "simplificacao", "desburocratizacao"],
                    "areas": ["todas"],
                    "hierarquia": 2
                },
                # Perícia Médica
                {
                    "id": "norm_040",
                    "nome_curto": "Portaria 1675/2018",
                    "nome_completo": "Portaria GM/MS nº 1.675, de 7 de junho de 2018",
                    "artigos": "Todos",
                    "palavras_chave": ["pericia medica", "atestado", "junta medica", "licenca saude"],
                    "areas": ["DIGEP"],
                    "hierarquia": 3
                },
                # Pregão Eletrônico
                {
                    "id": "norm_041",
                    "nome_curto": "Decreto 10024/2019",
                    "nome_completo": "Decreto nº 10.024, de 20 de setembro de 2019",
                    "artigos": "Todos",
                    "palavras_chave": ["pregao eletronico", "licitacao eletronica", "comprasnet"],
                    "areas": ["CGGAF"],
                    "hierarquia": 2
                },
                # Código de Ética
                {
                    "id": "norm_042",
                    "nome_curto": "Decreto 1171/94",
                    "nome_completo": "Decreto nº 1.171, de 22 de junho de 1994",
                    "artigos": "Todos",
                    "palavras_chave": ["codigo etica", "etica", "conduta servidor", "deveres"],
                    "areas": ["todas"],
                    "hierarquia": 2
                },
                # Reposição ao Erário
                {
                    "id": "norm_043",
                    "nome_curto": "Lei 8112/90 - Reposição",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 46-47",
                    "palavras_chave": ["reposicao erario", "ressarcimento", "devolucao", "pagamento indevido"],
                    "areas": ["CGPAG"],
                    "hierarquia": 1
                },
                # Gratificações
                {
                    "id": "norm_044",
                    "nome_curto": "Lei 11357/2006",
                    "nome_completo": "Lei nº 11.357, de 19 de outubro de 2006",
                    "artigos": "Todos",
                    "palavras_chave": ["gratificacao", "funcao comissionada", "cargo direcao", "remuneracao"],
                    "areas": ["CGPAG"],
                    "hierarquia": 1
                },
                # Adicional Noturno
                {
                    "id": "norm_045",
                    "nome_curto": "Lei 8112/90 - Adicional",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 75",
                    "palavras_chave": ["adicional noturno", "servico noturno", "jornada noturna"],
                    "areas": ["CGPAG"],
                    "hierarquia": 1
                },
                # Pensão
                {
                    "id": "norm_046",
                    "nome_curto": "Lei 8112/90 - Pensão",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 215-225",
                    "palavras_chave": ["pensao", "pensionista", "dependente", "falecimento"],
                    "areas": ["CGBEN"],
                    "hierarquia": 1
                },
                # Auxílio-Funeral
                {
                    "id": "norm_047",
                    "nome_curto": "Lei 8112/90 - Auxílio Funeral",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 226-228",
                    "palavras_chave": ["auxilio funeral", "falecimento", "obito", "funeral"],
                    "areas": ["CGBEN"],
                    "hierarquia": 1
                },
                # Auxílio-Natalidade
                {
                    "id": "norm_048",
                    "nome_curto": "Lei 8112/90 - Auxílio Natalidade",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 196",
                    "palavras_chave": ["auxilio natalidade", "nascimento", "filho", "dependente"],
                    "areas": ["CGBEN"],
                    "hierarquia": 1
                },
                # Assistência Pré-Escolar
                {
                    "id": "norm_049",
                    "nome_curto": "Lei 8112/90 - Assistência Pré-Escolar",
                    "nome_completo": "Lei nº 8.112, de 11 de dezembro de 1990",
                    "artigos": "Art. 230",
                    "palavras_chave": ["assistencia pre escolar", "creche", "crianca", "filho"],
                    "areas": ["CGBEN"],
                    "hierarquia": 1
                },
                # Avaliação de Desempenho
                {
                    "id": "norm_050",
                    "nome_curto": "Lei 11784/2008",
                    "nome_completo": "Lei nº 11.784, de 22 de setembro de 2008",
                    "artigos": "Art. 139-142",
                    "palavras_chave": ["avaliacao desempenho", "progressao", "promocao", "merito"],
                    "areas": ["DIGEP"],
                    "hierarquia": 1
                }
            ]
        }
        
        return biblioteca
    
    def _normalizar_keywords(self, texto: str) -> List[str]:
        """
        Normaliza e extrai keywords de um texto
        
        Args:
            texto: Texto a ser normalizado
            
        Returns:
            Lista de keywords normalizadas
        """
        texto_limpo = FormatadorUtils.normalizar_texto(texto)
        texto_limpo = re.sub(r'[^a-z0-9\s]', ' ', texto_limpo)
        
        palavras = texto_limpo.split()
        palavras = [p for p in palavras if len(p) > 3]
        
        return list(set(palavras))
    
    def _calcular_score_norma(self, norma: Dict[str, Any], contexto_keywords: List[str], area_codigo: str) -> float:
        """
        Calcula score de relevância de uma norma
        
        Args:
            norma: Dicionário com dados da norma
            contexto_keywords: Keywords extraídas do contexto
            area_codigo: Código da área
            
        Returns:
            Score de 0 a 100
        """
        score = 0.0
        
        # Match de keywords (peso 60)
        keywords_norma = norma.get('palavras_chave', [])
        matches = sum(1 for kw in contexto_keywords if any(kw in nkw for nkw in keywords_norma))
        
        if len(contexto_keywords) > 0:
            score += (matches / len(contexto_keywords)) * 60
        
        # Match de área (peso 20)
        areas_norma = norma.get('areas', [])
        if 'todas' in areas_norma or area_codigo in areas_norma:
            score += 20
        
        # Hierarquia (peso 20) - quanto menor a hierarquia, maior a prioridade
        hierarquia = norma.get('hierarquia', 5)
        score_hierarquia = ((6 - hierarquia) / 5) * 20
        score += score_hierarquia
        
        return min(score, 100.0)
    
    def sugerir_base_legal(self, contexto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sugere base legal baseada no contexto do processo
        
        Args:
            contexto: Dict com:
                - nome_processo: str
                - area_codigo: str
                - sistemas: List[str] (opcional)
                - objetivo: str (opcional)
        
        Returns:
            List[Dict] com top 3 sugestões:
                - nome_curto: str
                - nome_completo: str
                - artigos: str
                - confianca: float (0-100)
                - fonte: str ("biblioteca" ou "ia")
        """
        try:
            # Extrair keywords do contexto
            texto_contexto = f"{contexto.get('nome_processo', '')} {contexto.get('objetivo', '')}"
            if contexto.get('sistemas'):
                texto_contexto += " " + " ".join(contexto.get('sistemas', []))
            
            keywords = self._normalizar_keywords(texto_contexto)
            area_codigo = contexto.get('area_codigo', '')
            
            # Calcular scores para todas as normas
            normas_com_score = []
            for norma in self.biblioteca['normas']:
                score = self._calcular_score_norma(norma, keywords, area_codigo)
                
                if score > 0:
                    normas_com_score.append({
                        'nome_curto': norma['nome_curto'],
                        'nome_completo': norma['nome_completo'],
                        'artigos': norma['artigos'],
                        'confianca': round(score, 2),
                        'fonte': 'biblioteca'
                    })
            
            # Ordenar por score decrescente
            normas_com_score.sort(key=lambda x: x['confianca'], reverse=True)
            
            # Verificar se melhor resultado tem confiança < 70
            if not normas_com_score or normas_com_score[0]['confianca'] < 70:
                # Fallback para IA (se disponível)
                # Por enquanto, retorna sugestão genérica
                if not normas_com_score:
                    normas_com_score.append({
                        'nome_curto': 'Lei 9784/99',
                        'nome_completo': 'Lei nº 9.784, de 29 de janeiro de 1999',
                        'artigos': 'Todos',
                        'confianca': 50.0,
                        'fonte': 'biblioteca'
                    })
            
            # Retornar top 3
            return normas_com_score[:3]
            
        except Exception as e:
            print(f"Erro ao sugerir base legal: {e}")
            return []
    
    def buscar_por_palavra_chave(self, palavra_chave: str) -> List[Dict[str, Any]]:
        """
        Busca normas por palavra-chave específica
        
        Args:
            palavra_chave: Termo a ser buscado
            
        Returns:
            Lista de normas que contêm a palavra-chave
        """
        palavra_normalizada = FormatadorUtils.normalizar_texto(palavra_chave)
        resultados = []
        
        for norma in self.biblioteca['normas']:
            keywords_norma = norma.get('palavras_chave', [])
            
            if any(palavra_normalizada in kw for kw in keywords_norma):
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'confianca': 100.0,
                    'fonte': 'biblioteca'
                })
        
        return resultados
    
    def obter_normas_por_area(self, area_codigo: str) -> List[Dict[str, Any]]:
        """
        Retorna todas as normas aplicáveis a uma área específica
        
        Args:
            area_codigo: Código da área (ex: "CGBEN", "CGPAG")
            
        Returns:
            Lista de normas da área
        """
        resultados = []
        
        for norma in self.biblioteca['normas']:
            areas_norma = norma.get('areas', [])
            
            if 'todas' in areas_norma or area_codigo in areas_norma:
                resultados.append({
                    'nome_curto': norma['nome_curto'],
                    'nome_completo': norma['nome_completo'],
                    'artigos': norma['artigos'],
                    'hierarquia': norma['hierarquia']
                })
        
        # Ordenar por hierarquia (Lei > Decreto > IN)
        resultados.sort(key=lambda x: x['hierarquia'])
        
        return resultados


# Funções de conveniência para uso direto

def validar_entrada_helena(mensagem: str) -> Tuple[bool, str]:
    """Valida entrada do usuário para Helena"""
    if not mensagem or not mensagem.strip():
        return False, "Mensagem vazia"
    
    if len(mensagem) > 2000:
        return False, "Mensagem muito longa (máximo 2000 caracteres)"
    
    alertas = SegurancaUtils.verificar_conteudo_suspeito(mensagem)
    if alertas:
        return False, f"Conteúdo suspeito detectado: {', '.join(alertas)}"
    
    return True, "Válido"


def preparar_dados_para_pdf(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepara e valida dados para geração de PDF
    
    Args:
        dados: Dicionário com dados brutos do processo
        
    Returns:
        Dicionário com dados validados e formatados
    """
    dados_limpos = {}
    
    # Campos obrigatórios com valores padrão
    campos_obrigatorios = {
        'nome_processo': '[Não informado]',
        'codigo_processo': 'X.X.X.X',
        'entrega_esperada': '[Não informado]',
        'dispositivos_normativos': '[Não informado]',
        'operadores': '[Não informado]',
        'documentos_utilizados': '[Não informado]',
        'pontos_atencao': '[Não informado]',
        'processo_especifico': '[Não informado]',
        'macroprocesso': '[Não informado]',
        'subprocesso': '[Não informado]',
        'versao': '1.0',
        'data_aprovacao': datetime.now().strftime("%m/%Y"),
        'data_criacao': datetime.now().strftime("%d/%m/%Y"),
        'nome_usuario': '[Usuário]'
    }
    
    # Preencher campos obrigatórios
    for campo, valor_padrao in campos_obrigatorios.items():
        dados_limpos[campo] = dados.get(campo, valor_padrao)
    
    # Limpar campos de texto
    for chave, valor in dados_limpos.items():
        if isinstance(valor, str):
            dados_limpos[chave] = FormatadorUtils.limpar_texto_sistema(valor)
    
    # Processar listas
    if 'sistemas' in dados:
        sistemas = dados['sistemas']
        if isinstance(sistemas, list):
            dados_limpos['sistemas'] = [
                FormatadorUtils.limpar_texto_sistema(str(s)) 
                for s in sistemas
            ]
        else:
            dados_limpos['sistemas'] = []
    else:
        dados_limpos['sistemas'] = []

    # Processar operadores (lista)
    if 'operadores' in dados:
        operadores = dados['operadores']
        if isinstance(operadores, list):
            dados_limpos['operadores'] = [
                FormatadorUtils.limpar_texto_sistema(str(o))
                for o in operadores if o
            ]
        elif isinstance(operadores, str) and operadores.strip():
            # Operadores vêm como string separada por '; ' do frontend
            dados_limpos['operadores'] = [
                FormatadorUtils.limpar_texto_sistema(o.strip())
                for o in operadores.split(';') if o.strip()
            ]
        else:
            dados_limpos['operadores'] = []
    else:
        dados_limpos['operadores'] = []

    # Processar etapas (schema completo: operador, sistemas, docs, cenários)
    limpar = FormatadorUtils.limpar_texto_sistema
    if 'etapas' in dados:
        etapas = dados['etapas']
        if isinstance(etapas, list):
            dados_limpos['etapas'] = []
            for i, etapa in enumerate(etapas, 1):
                if isinstance(etapa, dict):
                    etapa_limpa = {
                        'numero': etapa.get('numero', i),
                        'descricao': limpar(etapa.get('descricao', '[Sem descrição]')),
                        'operador_nome': limpar(etapa.get('operador_nome', '')),
                        'sistemas': [limpar(str(s)) for s in etapa.get('sistemas', []) if s],
                        'docs_requeridos': [limpar(str(d)) for d in etapa.get('docs_requeridos', []) if d],
                        'docs_gerados': [limpar(str(d)) for d in etapa.get('docs_gerados', []) if d],
                        'tempo_estimado': limpar(etapa.get('tempo_estimado', '')) if etapa.get('tempo_estimado') else None,
                    }
                    # Campos condicionais
                    if etapa.get('tipo') == 'condicional':
                        etapa_limpa['tipo'] = 'condicional'
                        etapa_limpa['tipo_condicional'] = etapa.get('tipo_condicional')
                        antes = etapa.get('antes_decisao')
                        if isinstance(antes, dict):
                            etapa_limpa['antes_decisao'] = {
                                'numero': antes.get('numero', ''),
                                'descricao': limpar(antes.get('descricao', ''))
                            }
                        elif isinstance(antes, str):
                            etapa_limpa['antes_decisao'] = {'numero': '', 'descricao': limpar(antes)}
                        cenarios_raw = etapa.get('cenarios', [])
                        cenarios_limpos = []
                        for c in cenarios_raw:
                            if isinstance(c, dict):
                                cenario_limpo = {
                                    'numero': c.get('numero', ''),
                                    'descricao': limpar(c.get('descricao', '')),
                                    'subetapas': []
                                }
                                for sub in c.get('subetapas', []):
                                    if isinstance(sub, dict):
                                        cenario_limpo['subetapas'].append({
                                            'numero': sub.get('numero', ''),
                                            'descricao': limpar(sub.get('descricao', ''))
                                        })
                                cenarios_limpos.append(cenario_limpo)
                        etapa_limpa['cenarios'] = cenarios_limpos
                    else:
                        # Etapa linear: detalhes
                        etapa_limpa['detalhes'] = [limpar(str(d)) for d in etapa.get('detalhes', []) if d]
                    dados_limpos['etapas'].append(etapa_limpa)
                else:
                    # Fallback: etapa como string (schema antigo)
                    dados_limpos['etapas'].append({
                        'numero': i,
                        'descricao': limpar(str(etapa))
                    })
        else:
            dados_limpos['etapas'] = []
    else:
        dados_limpos['etapas'] = []
    
    # Processar área
    if 'area' in dados:
        if isinstance(dados['area'], dict):
            dados_limpos['area'] = dados['area']
        else:
            dados_limpos['area'] = {'codigo': 'X', 'nome': '[Não informado]'}
    else:
        dados_limpos['area'] = {'codigo': 'X', 'nome': '[Não informado]'}
    
    return dados_limpos


def gerar_id_unico() -> str:
    """Gera ID único baseado em timestamp"""
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(hash(datetime.now()))[-6:]


# Funções auxiliares para testes
def testar_pdf_generator():
    """Testa geração de PDF com dados de exemplo"""
    print("Testando PDFGenerator...")
    
    dados_teste = {
        "nome_processo": "Conceder Ressarcimento a Aposentado Civil",
        "codigo_processo": "2.3.3.1",
        "area": {"codigo": "CGBEN", "nome": "Coordenação-Geral de Benefícios"},
        "sistemas": ["SouGov", "SEI", "SIGEPE"],
        "entrega_esperada": "Auxílio de caráter indenizatório, por ressarcimento concedido à aposentado civil.",
        "dispositivos_normativos": "Art. 34 a 42 da IN SGP/SEDGG/ME nº 97/2022",
        "operadores": "Equipe técnica de Benefícios",
        "etapas": [
            {"numero": 1, "descricao": "Analisar requerimentos SIGEPE"},
            {"numero": 2, "descricao": "Verificar documentação completa"},
            {"numero": 3, "descricao": "Inserir auxílio no sistema"}
        ],
        "documentos_utilizados": "Requerimento SIGEPE, CPF, Contrato plano de saúde",
        "pontos_atencao": "Auditar situação do interessado desde a centralização",
        "processo_especifico": "Gestão de Benefícios",
        "macroprocesso": "Gestão de Auxílios",
        "subprocesso": "Gestão dos Auxílios de Caráter Indenizatório",
        "nome_usuario": "João Silva",
        "data_criacao": "29/09/2025"
    }
    
    generator = PDFGenerator()
    # Testar com URL base customizada
    url_base = "https://mapagov.app"
    caminho = generator.gerar_pop_completo(dados_teste, "teste_pop.pdf", url_base)
    
    if caminho:
        print(f"PDF gerado: {caminho}")
        print(f"   URL do QR Code: {url_base}/pop/{dados_teste['codigo_processo']}")
        return True
    else:
        print("Falha ao gerar PDF")
        return False


def testar_base_legal_suggestor():
    """Testa sugestão de base legal"""
    print("\nTestando BaseLegalSuggestor...")
    
    suggestor = BaseLegalSuggestor()
    
    # Teste 1: Ressarcimento
    contexto1 = {
        "nome_processo": "Ressarcimento plano de saúde aposentado",
        "area_codigo": "CGBEN",
        "objetivo": "Conceder auxílio saúde"
    }
    
    sugestoes1 = suggestor.sugerir_base_legal(contexto1)
    print(f"\nTeste 1 - Ressarcimento:")
    for i, sug in enumerate(sugestoes1, 1):
        print(f"  {i}. {sug['nome_curto']} - Confiança: {sug['confianca']}%")
    
    # Teste 2: Licitação
    contexto2 = {
        "nome_processo": "Realizar pregão eletrônico",
        "area_codigo": "CGGAF",
        "objetivo": "Contratar serviços"
    }
    
    sugestoes2 = suggestor.sugerir_base_legal(contexto2)
    print(f"\nTeste 2 - Licitação:")
    for i, sug in enumerate(sugestoes2, 1):
        print(f"  {i}. {sug['nome_curto']} - Confiança: {sug['confianca']}%")
    
    # Teste 3: Busca por área
    normas_cgben = suggestor.obter_normas_por_area("CGBEN")
    print(f"\nTeste 3 - Normas CGBEN: {len(normas_cgben)} encontradas")
    
    return len(sugestoes1) > 0 and len(sugestoes2) > 0


if __name__ == "__main__":
    print("=" * 60)
    print("MapaGov - Utils v2.1 - Testes")
    print("=" * 60)
    
    # Executar testes
    teste_pdf = testar_pdf_generator()
    teste_legal = testar_base_legal_suggestor()
    
    print("\n" + "=" * 60)
    print("Resultado dos Testes:")
    print(f"  PDF Generator: {'PASS' if teste_pdf else 'FAIL'}")
    print(f"  Base Legal Suggestor: {'PASS' if teste_legal else 'FAIL'}")
    print("=" * 60)