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

CLIENTES = [
    {
        "nome": "U RELVAS DOLIVEIRA",
        "filtro": "FILTRO 1 – CFTV E SEGURANÇA ELETRÔNICA (PARÁ)",
        "estados": ["PA"],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "cftv","circuito fechado de tv","circuito fechado",
            "monitoramento eletronico","monitoramento eletrônico",
            "videomonitoramento","video monitoramento",
            "vigilancia eletronica","vigilância eletrônica",
            "controle de acesso","sistema de seguranca","sistema de segurança",
            "cameras de seguranca","câmeras de segurança",
            "camera de seguranca","câmera de segurança",
            "instalacao de cameras","instalação de câmeras",
            "manutencao de sistemas de seguranca","manutenção de sistemas de segurança",
            "seguranca eletronica","segurança eletrônica"
        ],
        "valor_min": 0,
        "cor": "#1a56db",
        "emoji": "📹"
    },
    {
        "nome": "EXPRESS ALIMENTOS",
        "filtro": "FILTRO 2 – EXPRESS ALIMENTOS (PARÁ)",
        "estados": ["PA"],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "refeição","refeicao","refeições","refeicoes",
            "fornecimento de alimentos","generos alimenticios","gêneros alimentícios",
            "alimentacao coletiva","alimentação coletiva",
            "merenda","marmitex","quentinha","quentinhas",
            "servicos de alimentacao","serviços de alimentação",
            "preparo e distribuicao de refeicoes","preparo e distribuição de refeições",
            "fornecimento de alimentacao","fornecimento de alimentação",
            "refeicao coletiva","refeição coletiva"
        ],
        "valor_min": 2000000,
        "cor": "#e67e22",
        "emoji": "🍽️"
    },
    {
        "nome": "EXPRESS ALIMENTOS – ESCALA NACIONAL",
        "filtro": "FILTRO 3 – ALIMENTOS (BRASIL TODO – ESCALA)",
        "estados": [None],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "fornecimento de alimentos","refeição","refeicao","refeições","refeicoes",
            "alimentacao coletiva","alimentação coletiva",
            "generos alimenticios","gêneros alimentícios",
            "merenda escolar","preparo de alimentos",
            "cozinha industrial","servicos de alimentacao","serviços de alimentação",
            "preparo e distribuicao","distribuicao de refeicoes","distribuição de refeições",
            "refeicao coletiva","refeição coletiva"
        ],
        "valor_min": 3000000,
        "cor": "#c0392b",
        "emoji": "🌎"
    },
    {
        "nome": "LINHARES DISTRIBUIDORA",
        "filtro": "FILTRO 4 – LINHARES DISTRIBUIDORA (MINAS GERAIS)",
        "estados": ["MG"],
        "modalidades": {6: "Pregão Eletrônico", 8: "Dispensa Eletrônica", 4: "Concorrência"},
        "palavras": [
            "genero alimenticio","gênero alimentício",
            "generos alimenticios","gêneros alimentícios",
            "aquisicao de alimentos","aquisição de alimentos",
            "fornecimento de alimentos","produtos alimenticios","produtos alimentícios",
            "distribuicao de alimentos","distribuição de alimentos",
            "cesta basica","cesta básica",
            "merenda escolar","alimentos nao pereciveis","alimentos não perecíveis",
            "atacado de alimentos","material de consumo alimenticio"
        ],
        "valor_min": 0,
        "cor": "#27ae60",
        "emoji": "🏪"
    }
]

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MODALIDADES_EXTRA = "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}"


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
            print(f"  Erro: {e}")
            break
    return res


def tem_palavra(texto, palavras):
    t = (texto or "").lower()
    return any(p.lower() in t for p in palavras)


def fmt_valor(v):
    if not v or v == 0:
        return "Não informado"
    return "R$ {:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_data(data_str):
    if not data_str:
        return "Não informado"
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except:
        return data_str[:10] if len(data_str) >= 10 else data_str


def fmt_hora(data_str):
    if not data_str:
        return "Não informado"
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return "Não informado"


def gerar_link(item):
    try:
        cnpj = item["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
        ano = item.get("anoCompra", "")
        seq = item.get("sequencialCompra", "")
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
    except:
        return "https://pncp.gov.br/app/editais"


def get_portal(item):
    portal = item.get("linkSistemaOrigem", "")
    if not portal:
        portal = item.get("sistemaOrigem", "PNCP")
    if portal and "compras.gov" in portal.lower():
        return "Compras.gov.br"
    elif portal and "bll" in portal.lower():
        return "BLL Compras"
    elif portal and "licitanet" in portal.lower():
        return "Licitanet"
    elif portal and "portaldecompras" in portal.lower():
        return "Portal de Compras Públicas"
    elif portal:
        return "PNCP"
    return "PNCP"


def card_html(item, cor, emoji_cliente):
    link = gerar_link(item)
    uf_badge = f'<span style="background:#e8f0fe;color:#1a56db;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;margin-right:4px">📍 {item.get("uf","")}</span>' if item.get("uf") else ""
    mod_badge = f'<span style="background:#fff3e0;color:#e67e22;padding:2px 8px;border-radius:10px;font-size:11px;margin-right:4px">📌 {item.get("modalidade","")}</span>'

    return f"""
<div style="background:#fff;border:1px solid #e0e0e0;border-left:5px solid {cor};
    border-radius:8px;padding:16px;margin:10px 0;box-shadow:0 1px 4px rgba(0,0,0,0.06)">

  <div style="margin-bottom:8px">{uf_badge}{mod_badge}</div>

  <table style="width:100%;border-collapse:collapse;font-size:13px">
    <tr style="border-bottom:1px solid #f0f0f0">
      <td style="padding:5px 8px;color:#888;font-weight:bold;width:220px">🏢 Órgão</td>
      <td style="padding:5px 8px;color:#222;font-weight:bold">{item.get("orgao","N/I")}</td>
    </tr>
    <tr style="border-bottom:1px solid #f0f0f0;background:#fafafa">
      <td style="padding:5px 8px;color:#888;font-weight:bold">📋 Objeto</td>
      <td style="padding:5px 8px;color:#333">{item.get("objeto","")[:350]}</td>
    </tr>
    <tr style="border-bottom:1px solid #f0f0f0">
      <td style="padding:5px 8px;color:#888;font-weight:bold">📅 Data fim proposta</td>
      <td style="padding:5px 8px;color:#222">{item.get("data_fim","Não informado")}</td>
    </tr>
    <tr style="border-bottom:1px solid #f0f0f0;background:#fafafa">
      <td style="padding:5px 8px;color:#888;font-weight:bold">🕐 Horário da sessão</td>
      <td style="padding:5px 8px;color:#222">{item.get("horario","Não informado")}</td>
    </tr>
    <tr style="border-bottom:1px solid #f0f0f0">
      <td style="padding:5px 8px;color:#888;font-weight:bold">🌐 Portal</td>
      <td style="padding:5px 8px;color:#222">{item.get("portal","PNCP")}</td>
    </tr>
    <tr style="background:#e8f5e9">
      <td style="padding:5px 8px;color:#27ae60;font-weight:bold">💰 Valor estimado</td>
      <td style="padding:5px 8px;color:#27ae60;font-weight:bold;font-size:15px">{item.get("valor","Não informado")}</td>
    </tr>
  </table>

  <div style="margin-top:10px;text-align:right">
    <a href="{link}" style="background:{cor};color:#fff;padding:8px 16px;
       border-radius:6px;text-decoration:none;font-size:13px;font-weight:bold">
      🔗 Acessar edital no PNCP →
    </a>
  </div>
</div>"""


def secao_cliente_html(cliente, resultados):
    cor = cliente["cor"]
    nome = cliente["nome"]
    filtro = cliente["filtro"]
    emoji = cliente["emoji"]
    total = len(resultados)
    badge = "🔥" if total > 0 else "😴"

    estados_str = ", ".join(e if e else "BRASIL INTEIRO" for e in cliente["estados"])
    val_min = f" | Valor mínimo: {fmt_valor(cliente['valor_min'])}" if cliente["valor_min"] > 0 else ""

    cards = "".join(card_html(r, cor, emoji) for r in resultados) if resultados else """
<div style="background:#f5f5f5;padding:20px;border-radius:8px;text-align:center;color:#999">
  <p style="margin:0;font-size:15px">😴 Nenhuma licitação encontrada hoje para este cliente.</p>
  <p style="margin:4px 0 0;font-size:12px">O monitor continua ativo e verificará novamente amanhã às 08:30.</p>
</div>"""

    return f"""
<div style="margin:20px 0;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
  <div style="background:{cor};padding:18px 22px">
    <h2 style="color:#fff;margin:0;font-size:17px">{badge} {emoji} {filtro}</h2>
    <p style="color:rgba(255,255,255,0.9);margin:4px 0 0;font-size:13px;font-weight:bold">
      Cliente: {nome}
    </p>
    <p style="color:rgba(255,255,255,0.75);margin:2px 0 0;font-size:12px">
      📍 Estados: {estados_str}{val_min} &nbsp;|&nbsp; {total} licitação(ões) encontrada(s)
    </p>
  </div>
  <div style="background:#f9f9f9;padding:14px">
    {cards}
  </div>
</div>"""


def rodar():
    hoje = datetime.now().strftime("%Y%m%d")
    data_fmt = datetime.now().strftime("%d/%m/%Y")

    print(f"\n{'='*60}")
    print(f"  MONITOR PNCP — Grupo Cantanhede — {data_fmt}")
    print(f"{'='*60}")

    resultados_por_cliente = {c["nome"]: [] for c in CLIENTES}

    for cliente in CLIENTES:
        print(f"\n🔍 {cliente['filtro']}")
        vistos = set()
        for uf in cliente["estados"]:
            for mod_id, mod_nome in cliente["modalidades"].items():
                max_pag = 15 if uf is None else 10
                print(f"  {mod_nome} | UF: {uf or 'BRASIL'}")
                items = buscar_licitacoes(hoje, uf=uf, mod_id=mod_id, max_pag=max_pag)
                for item in items:
                    obj = item.get("objetoCompra", "")
                    valor = item.get("valorTotalEstimado") or 0
                    num = item.get("numeroControlePNCP", "")

                    if num in vistos:
                        continue

                    if not tem_palavra(obj, cliente["palavras"]):
                        continue

                    if valor < cliente["valor_min"]:
                        continue

                    vistos.add(num)

                    # Extrair datas
                    data_fim = fmt_data(item.get("dataEncerramentoProposta") or item.get("dataFim") or "")
                    horario = fmt_hora(item.get("dataEncerramentoProposta") or item.get("dataFim") or "")

                    # UF real do órgão
                    uf_real = ""
                    try:
                        uf_real = item.get("unidadeOrgao", {}).get("ufSigla", "") or uf or ""
                    except:
                        uf_real = uf or ""

                    resultados_por_cliente[cliente["nome"]].append({
                        "orgao": item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                        "objeto": obj,
                        "data_fim": data_fim,
                        "horario": horario,
                        "portal": get_portal(item),
                        "valor": fmt_valor(valor),
                        "modalidade": mod_nome,
                        "uf": uf_real,
                        "link": gerar_link(item),
                        "numero": num
                    })

        total_c = len(resultados_por_cliente[cliente["nome"]])
        print(f"  ✅ {total_c} resultado(s) encontrado(s)")

    enviar_email(data_fmt, resultados_por_cliente)


def enviar_email(data, resultados_por_cliente):
    total_geral = sum(len(v) for v in resultados_por_cliente.values())
    emoji_titulo = "🔥" if total_geral > 0 else "😴"

    secoes = "".join(
        secao_cliente_html(c, resultados_por_cliente[c["nome"]])
        for c in CLIENTES
    )

    # Tabela de resumo
    resumo_rows = ""
    for c in CLIENTES:
        t = len(resultados_por_cliente[c["nome"]])
        cor_n = "#27ae60" if t > 0 else "#aaa"
        resumo_rows += f"""
        <tr style="border-bottom:1px solid #f0f0f0">
          <td style="padding:8px 14px">{c["emoji"]} {c["nome"]}</td>
          <td style="padding:8px 14px;text-align:center">
            <span style="background:{cor_n};color:#fff;padding:3px 12px;border-radius:12px;font-weight:bold">{t}</span>
          </td>
          <td style="padding:8px 14px;font-size:12px;color:#888">{", ".join(e if e else "Brasil" for e in c["estados"])}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;background:#f0f2f5;margin:0;padding:20px">
<div style="max-width:780px;margin:auto">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
      padding:28px 30px;border-radius:12px 12px 0 0;text-align:center">
    <h1 style="color:#fff;margin:0;font-size:24px;letter-spacing:1px">
      {emoji_titulo} Monitor PNCP — Grupo Cantanhede
    </h1>
    <p style="color:#aab4d4;margin:8px 0 0;font-size:14px">
      📅 {data} &nbsp;|&nbsp;
      <b style="color:#fff">{total_geral} licitação(ões) encontrada(s)</b> no total
    </p>
  </div>

  <!-- RESUMO -->
  <div style="background:#fff;padding:20px 24px;border-left:1px solid #ddd;border-right:1px solid #ddd">
    <h3 style="margin:0 0 12px;color:#333;font-size:15px">📊 Resumo por cliente</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="background:#f5f5f5">
          <th style="padding:8px 14px;text-align:left;color:#555">Cliente</th>
          <th style="padding:8px 14px;text-align:center;color:#555">Resultados</th>
          <th style="padding:8px 14px;text-align:left;color:#555">Estados</th>
        </tr>
      </thead>
      <tbody>{resumo_rows}</tbody>
    </table>
  </div>

  <!-- SEÇÕES POR CLIENTE -->
  <div style="background:#f0f2f5;padding:10px 0">
    {secoes}
  </div>

  <!-- RODAPÉ -->
  <div style="background:#1a1a2e;padding:14px;border-radius:0 0 12px 12px;text-align:center">
    <p style="color:#aab4d4;margin:0;font-size:11px">
      Monitor automático · Grupo Cantanhede · Gerado em {data} às 08:30 (Brasília)
      <br>Campos exibidos: Órgão · Objeto · Data fim proposta · Horário · Portal · Valor estimado · Link
    </p>
  </div>

</div>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{emoji_titulo} PNCP {data} — {total_geral} licitação(ões) | U.Relvas / Express / Linhares"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINATARIO
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
        srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())

    print(f"\n✅ Email enviado com sucesso! {total_geral} resultado(s).")


if __name__ == "__main__":
    rodar()
