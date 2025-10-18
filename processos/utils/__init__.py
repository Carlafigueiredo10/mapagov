# -*- coding: utf-8 -*-
"""
Utilitarios do MapaGov
Exporta classes e funcoes do modulo utils
"""

# Import all utilities from processos.utils module (the file, not the package)
import importlib.util
from pathlib import Path

# Load utils.py file directly to avoid naming conflict with utils/ directory
utils_file = Path(__file__).parent.parent / 'utils.py'

if utils_file.exists():
    spec = importlib.util.spec_from_file_location("processos_utils_module", utils_file)
    if spec and spec.loader:
        utils_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(utils_module)

        # Export all classes and functions
        ValidadorUtils = utils_module.ValidadorUtils
        FormatadorUtils = utils_module.FormatadorUtils
        CodigoUtils = utils_module.CodigoUtils
        ArquivoUtils = utils_module.ArquivoUtils
        LogUtils = utils_module.LogUtils
        SegurancaUtils = utils_module.SegurancaUtils
        HelenaUtils = utils_module.HelenaUtils
        EstadoUtils = utils_module.EstadoUtils
        PDFGenerator = utils_module.PDFGenerator
        BaseLegalSuggestor = utils_module.BaseLegalSuggestor
        ConfigUtils = utils_module.ConfigUtils

        # Export helper functions
        validar_entrada_helena = utils_module.validar_entrada_helena
        preparar_dados_para_pdf = utils_module.preparar_dados_para_pdf
        gerar_id_unico = utils_module.gerar_id_unico

        __all__ = [
            'ValidadorUtils',
            'FormatadorUtils',
            'CodigoUtils',
            'ArquivoUtils',
            'LogUtils',
            'SegurancaUtils',
            'HelenaUtils',
            'EstadoUtils',
            'PDFGenerator',
            'BaseLegalSuggestor',
            'ConfigUtils',
            'validar_entrada_helena',
            'preparar_dados_para_pdf',
            'gerar_id_unico'
        ]
