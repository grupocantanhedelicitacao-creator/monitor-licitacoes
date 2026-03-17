monitor.py#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║   MONITOR DE LICITAÇÕES — GRUPO CANTANHEDE               ║
║   Roda automaticamente todo dia às 08:30 (Brasília)      ║
║   Versão: GitHub Actions (gratuito, sem PC ligado)       ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
# ⚙️  CONFIGURAÇÕES — lidas das variáveis de ambiente
#     (definidas nos Secrets do GitHub — ver README)
# ============================================================
EMAIL_REMETENTE    = os.environ.get("EMAIL_REMETENTE", "")
SENHA_APP_GMAIL    = os.environ.get("SENHA_APP_GMAIL", "")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DESTINATARIO", "")

# ============================================================
# 🔍  PALAVRAS-CHAVE DOS FILTROS
# ============================================================
FILTRO1_PALAVRAS = [
    "cftv", "videomonitoramento", "video monitoramento",
    "monitoramento eletrônico", "monitoramento eletronico",
    "circuito fechado", "controle de acesso",
    "câmera de segurança", "camera de seguranca",
    "segurança eletrônica", "seguranca eletronica",
    "vigilância eletrônica", "vigilancia eletronica"
]

FILTRO23_PALAVRAS = [
    "refeição", "refeicao", "refeições", "refeicoes",
    "alimentação", "alimentacao", "alimentos",
    "gêneros alimentícios", "generos alimenticios",
    "fornecimento de refeição", "fornecimento de refeicao",
    "restaurante", "marmita", "merenda", "nutrição", "nutricao",
    "fornecimento de alimentação", "fornecimento de alimentacao"
]

VALOR_MIN_FILTRO2 = 2_000_000   # R$ 2 milhões — PA
VALOR_MIN_FILTRO3 = 3_000_000   # R$ 3 milhões — Brasil

# Modalidades monitoradas
MODALIDADES = {
    6: "Pregão Eletrônico",
    8: "Dispensa Eletrônica",
    4: "Concorrência",
}

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

# ============================================================
# 🛠️  FUNÇÕES
# ============================================================

def buscar_licitacoes(data_str, uf=None, modalidade_id=6, max_paginas=10):
    """Busca licitações na API oficial do PNCP."""
    resultados = []
    for pagina in range(1, max_paginas + 1):
        params = {
            "dataInicial": data_str,
            "dataFinal":   data_str,
            "codigoModalidadeContratacao": modalidade_id,
            "pagina":      pagina,
            "tamanhoPagina": 50,
        }
        if uf:
            params["uf"] = uf
        try:
            resp = requests.get(BASE_URL, params=params, timeout=20)
            if resp.status_code == 200:
                dados = resp.json()
                items = dados.get("data", [])
                resultados.extend(items)
                total_pag = dados.get("totalPaginas", 1)
                print(f"   Página {pagina}/{total_pag} — {len(items)} registros")
                if pagina >= total_pag:
                    break
            else:
                print(f"   ⚠️  Status {resp.status_code} na página {pagina}")
                break
        except Exception as e:
            print(f"   ❌ Erro página {pagina}: {e}")
            break
    return resultados


def contem_palavra(texto, palavras):
    texto_lower = (texto or "").lower()
    return any(p in texto_lower for p in palavras)


def formatar_valor(valor):
    if not valor or valor == 0:
        return "Não informado"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_link_pncp(item):
    try:
        cnpj = item["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
        ano  = item.get("anoCompra", "")
        seq  = item.get("sequencialCompra", "")
        if cnpj and ano and seq:
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
    except Exception:
        pass
    return "https://pncp.gov.br/app/editais"


def montar_card_html(item, cor_borda="#3498db"):
    return f"""
<div style="border-left:4px solid {cor_borda};background:#f9f9f9;
            padding:14px;margin:10px 0;border-radius:4px">
  <b style="font-size:15px">🏢 {item['orgao']}</b><br>
  <span style="color:#555;font-size:13px">📌 {item['modalidade']} &nbsp;|&nbsp;
  💰 <b style="color:#27ae60">{item['valor']}</b></span><br><br>
  <span style="font-size:14px">📋 {item['objeto'][:280]}{'...' if len(item['objeto'])>280 else ''}</span><br><br>
  <a href="{item['link']}" style="color:#1a56db;font-size:13px">🔗 Acessar edital no PNCP</a>
</div>"""


# ============================================================
# 🚀  EXECUÇÃO PRINCIPAL
# ============================================================

def rodar():
    hoje     = datetime.now().strftime("%Y%m%d")
    data_fmt = datetime.now().strftime("%d/%m/%Y")

    print(f"\n{'='*55}")
    print(f"  MONITOR PNCP — Grupo Cantanhede — {data_fmt}")
    print(f"{'='*55}\n")

    # ---------- FILTRO 1 — CFTV no PA ----------
    print("🔍 FILTRO 1: CFTV / Monitoramento no PA")
    achou_f1 = []
    for mod_id, mod_nome in MODALIDADES.items():
        print(f"  Modalidade: {mod_nome}")
        items = buscar_licitacoes(hoje, uf="PA", modalidade_id=mod_id)
        for item in items:
            if contem_palavra(item.get("objetoCompra", ""), FILTRO1_PALAVRAS):
                achou_f1.append({
                    "objeto":     item.get("objetoCompra", ""),
                    "orgao":      item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                    "valor":      formatar_valor(item.get("valorTotalEstimado")),
                    "modalidade": mod_nome,
                    "link":       gerar_link_pncp(item),
                    "numero":     item.get("numeroControlePNCP", ""),
                })
    print(f"  ✅ Encontrados: {len(achou_f1)}\n")

    # ---------- FILTRO 2 — Alimentação PA +R$2M ----------
    print("🔍 FILTRO 2: Alimentação no PA (+R$2M)")
    achou_f2 = []
    for mod_id, mod_nome in MODALIDADES.items():
        print(f"  Modalidade: {mod_nome}")
        items = buscar_licitacoes(hoje, uf="PA", modalidade_id=mod_id)
        for item in items:
            valor = item.get("valorTotalEstimado") or 0
            if contem_palavra(item.get("objetoCompra", ""), FILTRO23_PALAVRAS) and valor >= VALOR_MIN_FILTRO2:
                achou_f2.append({
                    "objeto":     item.get("objetoCompra", ""),
                    "orgao":      item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                    "valor":      formatar_valor(valor),
                    "modalidade": mod_nome,
                    "link":       gerar_link_pncp(item),
                    "numero":     item.get("numeroControlePNCP", ""),
                })
    print(f"  ✅ Encontrados: {len(achou_f2)}\n")

    # ---------- FILTRO 3 — Alimentação Brasil +R$3M ----------
    print("🔍 FILTRO 3: Alimentação no Brasil (+R$3M)")
    achou_f3 = []
    for mod_id, mod_nome in MODALIDADES.items():
        print(f"  Modalidade: {mod_nome}")
        items = buscar_licitacoes(hoje, uf=None, modalidade_id=mod_id, max_paginas=15)
        for item in items:
            valor = item.get("valorTotalEstimado") or 0
            if contem_palavra(item.get("objetoCompra", ""), FILTRO23_PALAVRAS) and valor >= VALOR_MIN_FILTRO3:
                achou_f3.append({
                    "objeto":     item.get("objetoCompra", ""),
                    "orgao":      item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                    "valor":      formatar_valor(valor),
                    "modalidade": mod_nome,
                    "link":       gerar_link_pncp(item),
                    "numero":     item.get("numeroControlePNCP", ""),
                })
    print(f"  ✅ Encontrados: {len(achou_f3)}\n")

    # ---------- ENVIAR EMAIL ----------
    enviar_email(data_fmt, achou_f1, achou_f2, achou_f3)


def enviar_email(data, f1, f2, f3):
    total = len(f1) + len(f2) + len(f3)
    emoji = "🔥" if total > 0 else "😴"
    assunto = f"{emoji} PNCP {data} — {total} licitação(ões) encontrada(s)"

    # --- Monta HTML do email ---
    secao_f1 = "".join(montar_card_html(i, "#e74c3c") for i in f1) if f1 else \
        "<p style='color:#888'>Nenhuma licitação encontrada hoje.</p>"
    secao_f2 = "".join(montar_card_html(i, "#e67e22") for i in f2) if f2 else \
        "<p style='color:#888'>Nenhuma licitação encontrada hoje.</p>"
    secao_f3 = "".join(montar_card_html(i, "#27ae60") for i in f3) if f3 else \
        "<p style='color:#888'>Nenhuma licitação encontrada hoje.</p>"

    html = f"""
<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;max-width:720px;margin:auto;color:#222">

  <div style="background:#1a56db;padding:20px 24px;border-radius:8px 8px 0 0">
    <h1 style="color:#fff;margin:0;font-size:20px">
      {emoji} Monitor PNCP — Grupo Cantanhede
    </h1>
    <p style="color:#c8d8ff;margin:6px 0 0">{data} &nbsp;|&nbsp; {total} resultado(s) encontrado(s)</p>
  </div>

  <div style="border:1px solid #ddd;border-top:none;padding:20px;border-radius:0 0 8px 8px">

    <h2 style="color:#e74c3c;border-bottom:2px solid #e74c3c;padding-bottom:6px">
      📹 Filtro 1 — CFTV / Monitoramento Eletrônico no PA
      <span style="font-size:14px;color:#888">({len(f1)} resultado(s))</span>
    </h2>
    {secao_f1}

    <h2 style="color:#e67e22;border-bottom:2px solid #e67e22;padding-bottom:6px;margin-top:28px">
      🍽️ Filtro 2 — Refeições / Alimentação no PA (+R$ 2M)
      <span style="font-size:14px;color:#888">({len(f2)} resultado(s))</span>
    </h2>
    {secao_f2}

    <h2 style="color:#27ae60;border-bottom:2px solid #27ae60;padding-bottom:6px;margin-top:28px">
      🍽️ Filtro 3 — Refeições / Alimentação no Brasil (+R$ 3M)
      <span style="font-size:14px;color:#888">({len(f3)} resultado(s))</span>
    </h2>
    {secao_f3}

    <hr style="margin-top:30px">
    <p style="color:#aaa;font-size:11px;text-align:center">
      Monitor automático · Grupo Cantanhede · Gerado em {data} às 08:30
    </p>
  </div>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"]    = EMAIL_REMETENTE
    msg["To"]      = EMAIL_DESTINATARIO
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
            srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
            srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())
        print(f"✅ Email enviado com sucesso! ({total} resultado(s))")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        raise


if __name__ == "__main__":
    rodar()
