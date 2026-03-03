"""
Validador de links da Base Legal — MapaGov

Le baseLegalLinks.ts, testa cada URL e gera report JSON.
Uso: python frontend/scripts/validate-base-legal.py
"""
import re
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Instalando requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


LINKS_FILE = Path(__file__).resolve().parent.parent / "src" / "pages" / "baseLegalLinks.ts"
REPORT_FILE = Path(__file__).resolve().parent / "base-legal-report.json"

TIMEOUT = 8  # segundos
MAX_REDIRECTS = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (MapaGov Link Validator)"
}


def extract_urls(filepath: Path) -> list[dict]:
    """Extrai URLs e titulos do baseLegalLinks.ts via regex."""
    content = filepath.read_text(encoding="utf-8")
    entries = []
    # Regex para capturar title e url em sequencia
    pattern = re.compile(
        r'title:\s*"([^"]+)".*?url:\s*("([^"]+)"|null)',
        re.DOTALL,
    )
    for match in pattern.finditer(content):
        title = match.group(1)
        url = match.group(3)  # None se null
        entries.append({"title": title, "url": url})
    return entries


def check_url(url: str) -> dict:
    """Testa uma URL com HEAD (fallback GET), seguindo redirects."""
    result = {
        "url": url,
        "status": None,
        "final_url": None,
        "method": None,
        "error": None,
    }

    for method in ["HEAD", "GET"]:
        try:
            resp = requests.request(
                method,
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True,
                stream=(method == "GET"),  # nao baixa corpo inteiro no GET
            )
            result["status"] = resp.status_code
            result["final_url"] = resp.url if resp.url != url else None
            result["method"] = method

            # HEAD pode retornar 405/403 em alguns servidores, tentar GET
            if method == "HEAD" and resp.status_code in (405, 403, 406):
                continue

            # Se deu resposta valida, parar
            break

        except requests.exceptions.TooManyRedirects:
            result["error"] = "redirect_loop"
            result["method"] = method
            break
        except requests.exceptions.Timeout:
            result["error"] = "timeout"
            result["method"] = method
            break
        except requests.exceptions.ConnectionError as e:
            result["error"] = f"connection_error: {str(e)[:100]}"
            result["method"] = method
            break
        except Exception as e:
            result["error"] = f"unknown: {str(e)[:100]}"
            result["method"] = method
            break

    # Classificar
    status = result["status"]
    if status and 200 <= status <= 299:
        result["classification"] = "ok"
    elif status and status in (301, 302, 303, 307, 308):
        # Se chegou aqui, redirect nao resolveu (raro com allow_redirects=True)
        result["classification"] = "redirect_unresolved"
    elif status and status in (404, 410):
        result["classification"] = "broken"
    elif result["error"]:
        result["classification"] = "error"
    else:
        result["classification"] = "unknown"

    return result


def main():
    if not LINKS_FILE.exists():
        print(f"Arquivo nao encontrado: {LINKS_FILE}")
        sys.exit(1)

    entries = extract_urls(LINKS_FILE)
    print(f"Encontradas {len(entries)} URLs em baseLegalLinks.ts\n")

    results = []
    for i, entry in enumerate(entries, 1):
        title = entry["title"][:60]
        url = entry["url"]

        if not url:
            print(f"  [{i:2d}] SKIP (null)  {title}")
            results.append({
                "title": entry["title"],
                "url": None,
                "classification": "null",
            })
            continue

        print(f"  [{i:2d}] Testando... {title[:50]}", end="", flush=True)
        check = check_url(url)
        check["title"] = entry["title"]

        status_icon = {
            "ok": "OK",
            "broken": "BROKEN",
            "redirect_unresolved": "REDIRECT?",
            "error": "ERROR",
            "unknown": "???",
        }.get(check["classification"], "???")

        extra = ""
        if check.get("final_url"):
            extra = f" -> {check['final_url'][:60]}"
        if check.get("error"):
            extra = f" ({check['error'][:40]})"

        print(f"  [{check.get('status', '---')}] {status_icon}{extra}")
        results.append(check)

    # Salvar report
    report = {
        "total": len(results),
        "ok": sum(1 for r in results if r["classification"] == "ok"),
        "broken": sum(1 for r in results if r["classification"] == "broken"),
        "error": sum(1 for r in results if r["classification"] == "error"),
        "null": sum(1 for r in results if r["classification"] == "null"),
        "results": results,
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nReport salvo em: {REPORT_FILE}")
    print(f"  OK: {report['ok']} | Broken: {report['broken']} | Error: {report['error']} | Null: {report['null']}")

    if report["broken"] > 0 or report["error"] > 0:
        print("\n Links que precisam de atenção:")
        for r in results:
            if r["classification"] in ("broken", "error", "redirect_unresolved"):
                print(f"  - [{r.get('status', '---')}] {r['title'][:60]}")
                print(f"    URL: {r.get('url', 'N/A')}")
                if r.get("error"):
                    print(f"    Erro: {r['error']}")
                if r.get("final_url"):
                    print(f"    Redirect final: {r['final_url']}")


if __name__ == "__main__":
    main()
