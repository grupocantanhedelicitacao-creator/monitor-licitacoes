#!/usr/bin/env python3
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

EMAIL_REMETENTE    = os.environ.get("EMAIL_REMETENTE", "")
SENHA_APP_GMAIL    = os.environ.get("SENHA_APP_GMAIL", "")
EMAIL_DESTINATARIO = os.environ.get("EMAIL_DESTINATARIO", "")

# ============================================================
# CLIENTES — cada cliente tem nome, estados, modalidades e palavras-chave
# ============================================================
CLIENTES = [
    {
        "nome": "U RELVAS DOLIVEIRA",
        "estados": ["PA", "AM", "TO", "MA", "RO"],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "cftv", "monitoramento eletronico", "monitoramento eletrônico",
            "cameras de seguranca", "câmeras de segurança", "camera de seguranca",
            "câmera de segurança", "controle de acesso", "videomonitoramento",
            "circuito fechado", "vigilancia eletronica", "seguranca eletronica"
        ],
        "cor": "#1a56db"
    },
    {
        "nome": "EXPRESS ALIMENTOS",
        "estados": [None],  # None = todos os estados do Brasil
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "refeição", "refeicao", "refeições", "refeicoes",
            "fornecimento de alimentos", "fornecimento de alimentacao",
            "almoço", "almoco", "janta", "jantar", "lanche",
            "dieta", "alimentação", "alimentacao", "alimentos",
            "refeição coletiva", "refeicao coletiva",
            "preparo de refeicao", "preparo de refeição"
        ],
        "cor": "#e67e22"
    },
    {
        "nome": "LINHARES DISTRIBUIDORA",
        "estados": ["MG"],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "genero alimenticio", "gênero alimentício",
            "generos alimenticios", "gêneros alimentícios",
            "aquisicao de alimentos", "aquisição de alimentos",
            "material de consumo alimenticio", "merenda",
            "abastecimento alimentar"
        ],
        "cor": "#27ae60"
    }
]

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"


def buscar_licitacoes(data, uf=None, mod_id=6, max_pag=10):
    res = []
    for p in range(1, max_pag + 1):
        params = {
            "dataInicial": data, "dataFinal": data,
            "codigoModalidadeContratacao": mod_id,
            "pagina": p, "tamanhoPagina": 50
        }
        if uf:
            params["uf"] = uf
        try:
            r = requests.get(BASE_URL, params=params, timeout=20)
            if r.status_code == 200:
                d = r.json()
                res.extend(d.get("data", []))
                if p >= d.get("totalPaginas", 1):
                    break
        except Exception as e:
            print(f"Erro na busca: {e}")
            break
    return res


def tem_palavra(texto, palavras):
    t = (texto or "").lower()
    return any(p.lower() in t for p in palavras)


def fmt_valor(v):
    if not v:
        return "Não informado"
    return "R$ {:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_link(item):
    try:
        cnpj = item["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
        ano = item.get("anoCompra", "")
        seq = item.get("sequencialCompra", "")
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
    except Exception:
        return "https://pncp.gov.br/app/editais"


def card_html(item, cor_cliente):
    obj = item['objeto'][:300]
    uf_tag = f"<span style='background:#e8f0fe;color:#1a56db;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:6px'>📍 {item['uf']}</span>" if item.get('uf') else ""
    return (
        f'<div style="border-left:4px solid {cor_cliente};background:#f9f9f9;'
        f'padding:14px;margin:10px 0;border-radius:4px;border:1px solid #eee">'
        f'<b style="font-size:15px">🏢 {item["orgao"]}</b><br>'
        f'<div style="margin:6px 0">'
        f'{uf_tag}'
        f'<span style="background:#fff3e0;color:#e67e22;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:6px">📌 {item["modalidade"]}</span>'
        f'<span style="background:#e8f5e9;color:#27ae60;padding:2px 8px;border-radius:12px;font-size:12px"><b>💰 {item["valor"]}</b></span>'
        f'</div>'
        f'<p style="margin:8px 0;font-size:14px;color:#333">{obj}</p>'
        f'<a href="{item["link"]}" style="color:#1a56db;font-size:13px;text-decoration:none">🔗 Acessar edital no PNCP →</a>'
        f'</div>'
    )


def secao_cliente_html(cliente, resultados):
    cor = cliente["cor"]
    nome = cliente["nome"]
    total = len(resultados)
    emoji = "🔥" if total > 0 else "😴"

    estados_str = ", ".join(e if e else "BRASIL" for e in cliente["estados"])
    palavras_str = ", ".join(cliente["palavras"][:5]) + ("..." if len(cliente["palavras"]) > 5 else "")

    cards = "".join(card_html(r, cor) for r in resultados) if resultados else (
        "<div style='background:#f5f5f5;padding:12px;border-radius:4px;color:#999;text-align:center'>"
        "Nenhuma licitação encontrada hoje para este cliente.</div>"
    )

    return f"""
<div style="margin:24px 0;border:2px solid {cor};border-radius:10px;overflow:hidden">
  <div style="background:{cor};padding:16px 20px">
    <h2 style="color:#fff;margin:0;font-size:18px">{emoji} {nome}</h2>
    <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:13px">
      📍 Estados: {estados_str} &nbsp;|&nbsp; 📋 {total} licitação(ões) encontrada(s)
    </p>
    <p style="color:rgba(255,255,255,0.7);margin:2px 0 0;font-size:12px">
      🔍 Palavras-chave: {palavras_str}
    </p>
  </div>
  <div style="padding:16px">
    {cards}
  </div>
</div>"""


def rodar():
    hoje = datetime.now().strftime("%Y%m%d")
    data_fmt = datetime.now().strftime("%d/%m/%Y")

    print(f"\n{'='*55}")
    print(f"  MONITOR PNCP — Grupo Cantanhede — {data_fmt}")
    print(f"{'='*55}")

    resultados_por_cliente = {c["nome"]: [] for c in CLIENTES}

    for cliente in CLIENTES:
        print(f"\nBuscando para: {cliente['nome']}")
        for uf in cliente["estados"]:
            for mod_id, mod_nome in cliente["modalidades"].items():
                max_pag = 15 if uf is None else 10
                print(f"  {mod_nome} | UF: {uf or 'BRASIL'}")
                items = buscar_licitacoes(hoje, uf=uf, mod_id=mod_id, max_pag=max_pag)
                for item in items:
                    obj = item.get("objetoCompra", "")
                    if tem_palavra(obj, cliente["palavras"]):
                        resultados_por_cliente[cliente["nome"]].append({
                            "objeto": obj,
                            "orgao": item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                            "valor": fmt_valor(item.get("valorTotalEstimado")),
                            "modalidade": mod_nome,
                            "uf": item.get("unidadeOrgao", {}).get("ufSigla", uf or "BR"),
                            "link": gerar_link(item)
                        })
        total_c = len(resultados_por_cliente[cliente["nome"]])
        print(f"  -> {total_c} resultado(s) encontrado(s)")

    enviar_email(data_fmt, resultados_por_cliente)


def enviar_email(data, resultados_por_cliente):
    total_geral = sum(len(v) for v in resultados_por_cliente.values())
    emoji = "🔥" if total_geral > 0 else "😴"

    secoes = "".join(
        secao_cliente_html(c, resultados_por_cliente[c["nome"]])
        for c in CLIENTES
    )

    resumo_itens = ""
    for c in CLIENTES:
        t = len(resultados_por_cliente[c["nome"]])
        cor_badge = "#27ae60" if t > 0 else "#999"
        resumo_itens += (
            f'<tr>'
            f'<td style="padding:6px 12px;font-weight:bold">{c["nome"]}</td>'
            f'<td style="padding:6px 12px;text-align:center">'
            f'<span style="background:{cor_badge};color:#fff;padding:2px 10px;'
            f'border-radius:12px;font-size:13px">{t}</span>'
            f'</td>'
            f'</tr>'
        )

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;max-width:750px;margin:auto;color:#222;background:#f0f2f5;padding:20px">

<div style="background:#1a1a2e;padding:24px;border-radius:10px 10px 0 0;text-align:center">
  <h1 style="color:#fff;margin:0;font-size:22px">{emoji} Monitor PNCP — Grupo Cantanhede</h1>
  <p style="color:#aab4d4;margin:8px 0 0">{data} &nbsp;|&nbsp; <b style="color:#fff">{total_geral} licitação(ões)</b> encontrada(s) no total</p>
</div>

<div style="background:#fff;padding:20px;border-radius:0 0 10px 10px;margin-bottom:20px">
  <h3 style="margin:0 0 12px;color:#444">📊 Resumo por cliente</h3>
  <table style="width:100%;border-collapse:collapse;background:#f9f9f9;border-radius:8px;overflow:hidden">
    <thead>
      <tr style="background:#1a1a2e;color:#fff">
        <th style="padding:8px 12px;text-align:left">Cliente</th>
        <th style="padding:8px 12px;text-align:center">Resultados</th>
      </tr>
    </thead>
    <tbody>{resumo_itens}</tbody>
  </table>
</div>

{secoes}

<div style="text-align:center;padding:16px;color:#aaa;font-size:11px">
  Monitor automático · Grupo Cantanhede · {data} às 08:30 (Brasília)
</div>

</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{emoji} PNCP {data} — {total_geral} licitacao(oes) | U Relvas / Express / Linhares"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
        srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())

    print(f"\n✅ Email enviado! {total_geral} resultado(s) no total.")


if __name__ == "__main__":
    rodar()
