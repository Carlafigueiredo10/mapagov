"""
logging_bootstrap.py — Corrige encoding do stdout no Windows
Executado antes de o Django inicializar os loggers.
"""

import sys
import io
import logging
import unicodedata

# ======================================================================
# Configuração segura: apenas no Windows
# ======================================================================
if sys.platform.startswith("win"):
    try:
        # 1. Reconfigura sys.stdout / sys.stderr se necessário
        current_encoding = getattr(sys.stdout, "encoding", "").lower()
        if "utf" not in current_encoding:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
            print("[BOOTSTRAP] sys.stdout/sys.stderr reconfigurados para UTF-8.")
        else:
            print(f"[BOOTSTRAP] sys.stdout ja configurado ({current_encoding}).")

        # 2. Define filtro de segurança
        class SafeUTF8Filter(logging.Filter):
            def filter(self, record):
                try:
                    safe_msg = unicodedata.normalize("NFKD", str(record.msg))
                    safe_msg = safe_msg.encode("ascii", "ignore").decode("ascii")
                    record.msg = safe_msg
                except Exception:
                    record.msg = str(record.msg)
                return True

        # 3. Aplica o filtro a todos os handlers existentes
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(SafeUTF8Filter())

        # 4. Garante que futuros handlers também recebam o filtro
        logging._original_addHandler = logging.Logger.addHandler

        def patched_addHandler(self, hdlr):
            logging._original_addHandler(self, hdlr)
            try:
                hdlr.addFilter(SafeUTF8Filter())
            except Exception:
                pass

        logging.Logger.addHandler = patched_addHandler

        print("[BOOTSTRAP] Filtro SafeUTF8Filter aplicado a todos os handlers (ativos e futuros).")

    except Exception as e:
        print(f"[BOOTSTRAP] Falha ao configurar logging UTF-8: {e}")
