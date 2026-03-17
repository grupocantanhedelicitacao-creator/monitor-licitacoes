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
        "cor": "#1565c0",
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
            "refeicao coletiva","refeição coletiva","alimentação escolar",
            "alimentacao escolar","cozinha industrial"
        ],
        "valor_min": 2000000,
        "cor": "#e65100",
        "emoji": "🍽️"
    },
    {
        "nome": "EXPRESS ALIMENTOS – NACIONAL",
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
            "refeicao coletiva","refeição coletiva","alimentação escolar","alimentacao escolar"
        ],
        "valor_min": 3000000,
        "cor": "#b71c1c",
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
            "cesta basica","cesta básica","merenda escolar",
            "alimentos nao pereciveis","alimentos não perecíveis",
            "atacado de alimentos","material de consumo alimenticio","material de consumo alimentício"
        ],
        "valor_min": 0,
        "cor": "#1b5e20",
        "emoji": "🏪"
    }
]

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

# Mapeamento de portais por domínio
PORTAIS = {
    "portaldecompraspublicas.com.br": "Portal de Compras Públicas",
    "compras.gov.br": "Compras.gov.br",
    "bnccompras.com": "BNC Compras",
    "licitanet.com.br": "Licitanet",
    "bllcompras.com": "BLL Compras",
    "licitacoes-e.com.br": "Licitações-e (BB)",
    "comprasnet.gov.br": "ComprasNet",
    "gov.br": "Compras.gov.br",
    "tce.sp.gov.br": "TCE-SP",
    "tce.mg.gov.br": "TCE-MG",
    "e-licitacao.com.br": "e-Licitação",
    "pncp.gov.br": "PNCP",
    "audesp.tce.sp.gov.br": "AUDESP",
    "bnc.org.br": "BNC",
    "compraselectronicas.net": "Compras Eletrônicas",
    "licitacon.tcm.ba.gov.br": "LICITACON-BA",
    "sistemas.tcm.go.gov.br": "TCM-GO",
}


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


def fmt_data_hora(data_str):
    """Retorna (data_fmt, hora_fmt) a partir de uma string ISO"""
    if not data_str:
        return "Não informado", "Não informado"
    try:
        # Remove timezone e parse
        clean = data_str.replace("Z", "").replace("+00:00", "").replace("-03:00", "")
        if "T" in clean:
            dt = datetime.fromisoformat(clean)
        else:
            dt = datetime.strptime(clean[:10], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M") if "T" in clean else "Não informado"
    except:
        return data_str[:10] if len(data_str) >= 10 else data_str, "Não informado"


def extrair_portal(link_sistema):
    """Extrai o nome do portal a partir da URL do sistema de origem"""
    if not link_sistema:
        return "PNCP"
    url = link_sistema.lower()
    for dominio, nome in PORTAIS.items():
        if dominio in url:
            return nome
    # Tenta extrair o domínio de forma genérica
    try:
        import re
        match = re.search(r'https?://([^/]+)', url)
        if match:
            dom = match.group(1).replace("www.", "")
            return dom.split(".")[0].upper()
    except:
        pass
    return "Portal Externo"


def gerar_links(item):
    """
    Retorna (link_edital, link_pncp)
    - link_edital: URL direta do portal onde a licitação está publicada
    - link_pncp: URL do PNCP para consulta
    """
    cnpj = ""
    try:
        cnpj = item["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
    except:
        pass

    ano = item.get("anoCompra", "")
    seq = item.get("sequencialCompra", "")

    # Link direto no PNCP (sempre funciona)
    link_pncp = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if cnpj and ano and seq else "https://pncp.gov.br/app/editais"

    # Link do portal de origem (externo) — preferível pois vai direto ao edital
    link_externo = item.get("linkSistemaOrigem", "") or ""

    # Se link externo é só o domínio do PNCP, usar o link completo que construímos
    if not link_externo or link_externo.strip().rstrip("/") in ["https://pncp.gov.br", "http://pncp.gov.br", "https://www.pncp.gov.br"]:
        return link_pncp, link_pncp

    return link_externo, link_pncp


def card_html(item, cor):
    link_edital, link_pncp = gerar_links(item)
    portal = extrair_portal(item.get("link_sistema_origem", ""))
    data_fim = item.get("data_fim", "Não informado")
    horario = item.get("horario", "Não informado")
    uf = item.get("uf", "")

    uf_badge = f'<span style="background:#e3f2fd;color:#1565c0;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:bold;margin-right:5px">📍 {uf}</span>' if uf else ""
    mod_badge = f'<span style="background:#fff8e1;color:#f57f17;padding:2px 10px;border-radius:12px;font-size:11px;margin-right:5px">📌 {item.get("modalidade","")}</span>'

    return f"""
<div style="background:#ffffff;border:1px solid #e0e0e0;border-left:5px solid {cor};
    border-radius:8px;padding:18px;margin:10px 0;box-shadow:0 2px 6px rgba(0,0,0,0.06)">

  <div style="margin-bottom:10px">{uf_badge}{mod_badge}</div>

  <table style="width:100%;border-collapse:collapse;font-size:13.5px">
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#666;font-weight:bold;width:200px;white-space:nowrap">🏢 Órgão</td>
      <td style="padding:6px 10px;color:#111;font-weight:bold">{item.get("orgao","N/I")}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">
      <td style="padding:6px 10px;color:#666;font-weight:bold;vertical-align:top">📋 Objeto</td>
      <td style="padding:6px 10px;color:#333;line-height:1.5">{item.get("objeto","")[:400]}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#666;font-weight:bold">📅 Data fim proposta</td>
      <td style="padding:6px 10px;color:#111"><b>{data_fim}</b></td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">
      <td style="padding:6px 10px;color:#666;font-weight:bold">🕐 Horário da sessão</td>
      <td style="padding:6px 10px;color:#111"><b>{horario}</b></td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#666;font-weight:bold">🌐 Portal</td>
      <td style="padding:6px 10px;color:#111">{item.get("portal","PNCP")}</td>
    </tr>
    <tr style="background:#f1f8e9">
      <td style="padding:8px 10px;color:#2e7d32;font-weight:bold">💰 Valor estimado</td>
      <td style="padding:8px 10px;color:#1b5e20;font-weight:bold;font-size:16px">{item.get("valor","Não informado")}</td>
    </tr>
  </table>

  <div style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">
    <a href="{link_edital}" style="background:{cor};color:#fff;padding:9px 18px;
       border-radius:6px;text-decoration:none;font-size:13px;font-weight:bold;display:inline-block">
      🔗 Acessar Edital (Portal)
    </a>
    <a href="{link_pncp}" style="background:#fff;color:{cor};padding:9px 18px;
       border-radius:6px;text-decoration:none;font-size:13px;font-weight:bold;
       border:2px solid {cor};display:inline-block">
      📄 Ver no PNCP
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
    val_str = f" | Mín: {fmt_valor(cliente['valor_min'])}" if cliente["valor_min"] > 0 else ""

    cards = "".join(card_html(r, cor) for r in resultados) if resultados else """
<div style="background:#f9f9f9;padding:20px;border-radius:8px;text-align:center;color:#aaa;border:1px dashed #ddd">
  <p style="margin:0;font-size:15px">😴 Nenhuma licitação encontrada hoje.</p>
  <p style="margin:6px 0 0;font-size:12px">O monitor verifica novamente amanhã às 08:30.</p>
</div>"""

    return f"""
<div style="margin:16px 0;border-radius:10px;overflow:hidden;
    box-shadow:0 3px 10px rgba(0,0,0,0.08);border:1px solid #e0e0e0">

  <!-- Header do cliente -->
  <div style="background:{cor};padding:16px 20px">
    <h2 style="color:#fff;margin:0;font-size:16px;font-weight:bold">
      {badge} {emoji} {filtro}
    </h2>
    <p style="color:rgba(255,255,255,0.9);margin:4px 0 0;font-size:13px;font-weight:bold">
      Cliente: {nome}
    </p>
    <p style="color:rgba(255,255,255,0.75);margin:2px 0 0;font-size:12px">
      📍 {estados_str}{val_str} &nbsp;·&nbsp; <b style="color:#fff">{total}</b> licitação(ões) encontrada(s)
    </p>
  </div>

  <!-- Cards -->
  <div style="background:#f7f9fc;padding:14px 16px">
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

                    # Datas
                    dt_raw = item.get("dataEncerramentoProposta") or item.get("dataAberturaProposta") or ""
                    data_fim, horario = fmt_data_hora(dt_raw)

                    # UF real
                    uf_real = ""
                    try:
                        uf_real = item.get("unidadeOrgao", {}).get("ufSigla", "") or uf or ""
                    except:
                        uf_real = uf or ""

                    # Link e portal — CORRIGIDO
                    link_sistema = item.get("linkSistemaOrigem", "") or ""
                    portal_nome = extrair_portal(link_sistema)

                    resultados_por_cliente[cliente["nome"]].append({
                        "orgao": item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                        "objeto": obj,
                        "data_fim": data_fim,
                        "horario": horario,
                        "portal": portal_nome,
                        "valor": fmt_valor(valor),
                        "modalidade": mod_nome,
                        "uf": uf_real,
                        "link_sistema_origem": link_sistema,
                        # Guardamos o item original para gerar o link no card
                        "_item_raw": item,
                        "numero": num
                    })

        total_c = len(resultados_por_cliente[cliente["nome"]])
        print(f"  ✅ {total_c} resultado(s)")

    enviar_email(data_fmt, resultados_por_cliente)


def enviar_email(data, resultados_por_cliente):
    total_geral = sum(len(v) for v in resultados_por_cliente.values())
    emoji_titulo = "🔥" if total_geral > 0 else "😴"

    secoes = "".join(
        secao_cliente_html(c, resultados_por_cliente[c["nome"]])
        for c in CLIENTES
    )

    # Resumo
    rows = ""
    for c in CLIENTES:
        t = len(resultados_por_cliente[c["nome"]])
        cor_n = c["cor"] if t > 0 else "#bbb"
        rows += f"""
<tr style="border-bottom:1px solid #f0f0f0">
  <td style="padding:8px 14px">{c['emoji']} <b>{c['nome']}</b></td>
  <td style="padding:8px 14px;text-align:center">
    <span style="background:{cor_n};color:#fff;padding:3px 12px;border-radius:12px;font-weight:bold;font-size:13px">{t}</span>
  </td>
  <td style="padding:8px 14px;font-size:12px;color:#888">{", ".join(e if e else "Brasil" for e in c['estados'])}</td>
</tr>"""

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;background:#f0f2f5;margin:0;padding:16px">
<div style="max-width:800px;margin:auto">

  <!-- HEADER BRANCO -->
  <div style="background:#ffffff;padding:24px 28px;border-radius:12px 12px 0 0;
      border:1px solid #e0e0e0;border-bottom:3px solid #1565c0">
    <table style="width:100%"><tr>
      <td>
        <h1 style="color:#1a1a2e;margin:0;font-size:22px;font-weight:bold">
          {emoji_titulo} Monitor PNCP — Grupo Cantanhede
        </h1>
        <p style="color:#666;margin:6px 0 0;font-size:14px">
          📅 {data} &nbsp;·&nbsp; <b style="color:#1565c0">{total_geral} licitação(ões) encontrada(s)</b>
        </p>
      </td>
      <td style="text-align:right;vertical-align:middle">
        <span style="background:#1565c0;color:#fff;padding:8px 16px;
          border-radius:20px;font-size:13px;font-weight:bold">{total_geral} resultado(s)</span>
      </td>
    </tr></table>
  </div>
import os
import re
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
        "filtro": "FILTRO 1 - CFTV E SEGURANCA ELETRONICA (PARA)",
        "estados": ["PA"],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
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
        "cor": "#1565c0",
        "emoji": "📹"
    },
    {
        "nome": "EXPRESS ALIMENTOS",
        "filtro": "FILTRO 2 - EXPRESS ALIMENTOS (PARA)",
        "estados": ["PA"],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "refeição","refeicao","refeições","refeicoes",
            "fornecimento de alimentos","generos alimenticios","gêneros alimentícios",
            "alimentacao coletiva","alimentação coletiva",
            "merenda","marmitex","quentinha","quentinhas",
            "servicos de alimentacao","serviços de alimentação",
            "preparo e distribuicao de refeicoes","preparo e distribuição de refeições",
            "fornecimento de alimentacao","fornecimento de alimentação",
            "refeicao coletiva","refeição coletiva",
            "alimentação escolar","alimentacao escolar","cozinha industrial"
        ],
        "valor_min": 2000000,
        "cor": "#e65100",
        "emoji": "🍽️"
    },
    {
        "nome": "EXPRESS ALIMENTOS - NACIONAL",
        "filtro": "FILTRO 3 - ALIMENTOS (BRASIL TODO - ESCALA)",
        "estados": [None],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "fornecimento de alimentos","refeição","refeicao","refeições","refeicoes",
            "alimentacao coletiva","alimentação coletiva",
            "generos alimenticios","gêneros alimentícios",
            "merenda escolar","preparo de alimentos",
            "cozinha industrial","servicos de alimentacao","serviços de alimentação",
            "refeicao coletiva","refeição coletiva",
            "alimentação escolar","alimentacao escolar"
        ],
        "valor_min": 3000000,
        "cor": "#b71c1c",
        "emoji": "🌎"
    },
    {
        "nome": "LINHARES DISTRIBUIDORA",
        "filtro": "FILTRO 4 - LINHARES DISTRIBUIDORA (MINAS GERAIS)",
        "estados": ["MG"],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "genero alimenticio","gênero alimentício",
            "generos alimenticios","gêneros alimentícios",
            "aquisicao de alimentos","aquisição de alimentos",
            "fornecimento de alimentos","produtos alimenticios","produtos alimentícios",
            "distribuicao de alimentos","distribuição de alimentos",
            "cesta basica","cesta básica","merenda escolar",
            "alimentos nao pereciveis","alimentos não perecíveis",
            "atacado de alimentos","material de consumo alimenticio"
        ],
        "valor_min": 0,
        "cor": "#1b5e20",
        "emoji": "🏠"
    }
]

BASE_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

PORTAIS_MAP = {
    "portaldecompraspublicas.com.br": "Portal de Compras Publicas",
    "compras.gov.br": "Compras.gov.br",
    "bnccompras.com": "BNC Compras",
    "bnc.org.br": "BNC Compras",
    "licitanet.com.br": "Licitanet",
    "bllcompras.com": "BLL Compras",
    "bll.org.br": "BLL Compras",
    "licitacoes-e.com.br": "Licitacoes-e (BB)",
    "comprasnet.gov.br": "ComprasNet",
    "e-licitacao.com.br": "e-Licitacao",
    "pncp.gov.br": "PNCP",
    "tce.sp.gov.br": "TCE-SP",
    "tce.mg.gov.br": "TCE-MG",
    "compraselectronicas.net": "Compras Eletronicas",
    "licitacon.tcm.ba.gov.br": "LICITACON-BA",
}


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
        return "Nao informado"
    return "R$ {:,.2f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_data_hora(data_str):
    if not data_str:
        return "Nao informado", "Nao informado"
    try:
        clean = data_str[:19]
        if "T" in clean:
            dt = datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d/%m/%Y"), dt.strftime("%H:%M")
        else:
            dt = datetime.strptime(clean[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y"), "Nao informado"
    except:
        return data_str[:10] if len(data_str) >= 10 else data_str, "Nao informado"


def extrair_portal(link_sistema):
    if not link_sistema:
        return "PNCP"
    url = link_sistema.lower()
    for dominio, nome in PORTAIS_MAP.items():
        if dominio in url:
            return nome
    try:
        match = re.search(r'https?://([^/]+)', url)
        if match:
            dom = match.group(1).replace("www.", "")
            partes = dom.split(".")
            return partes[0].upper() if partes else "Portal"
    except:
        pass
    return "Portal Externo"


def gerar_links(item_raw):
    """
    Retorna (link_edital, link_pncp)
    link_edital  -> URL do portal externo (vai direto ao edital)
    link_pncp    -> URL do PNCP (fallback sempre funciona)
    """
    cnpj = ""
    try:
        cnpj = item_raw["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
    except:
        pass

    ano = item_raw.get("anoCompra", "")
    seq = item_raw.get("sequencialCompra", "")
    link_pncp = (
        f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
        if cnpj and ano and seq
        else "https://pncp.gov.br/app/editais"
    )

    link_externo = (item_raw.get("linkSistemaOrigem") or "").strip().rstrip("/")

    # Se link externo e apenas o dominio raiz do PNCP, usar o link completo
    dominios_genericos = [
        "https://pncp.gov.br", "http://pncp.gov.br",
        "https://www.pncp.gov.br", "http://www.pncp.gov.br", ""
    ]
    if link_externo in dominios_genericos:
        return link_pncp, link_pncp

    return link_externo, link_pncp


def card_html(item, cor):
    item_raw = item.get("_raw", {})
    link_edital, link_pncp = gerar_links(item_raw)
    mesmo_link = link_edital == link_pncp

    uf = item.get("uf", "")
    uf_badge = (
        f'<span style="background:#e3f2fd;color:#1565c0;padding:2px 10px;'
        f'border-radius:12px;font-size:11px;font-weight:bold;margin-right:5px">&#128205; {uf}</span>'
        if uf else ""
    )
    mod_badge = (
        f'<span style="background:#fff8e1;color:#f57f17;padding:2px 10px;'
        f'border-radius:12px;font-size:11px;margin-right:5px">&#128204; {item.get("modalidade","")}</span>'
    )

    btn_externo = (
        f'<a href="{link_edital}" style="background:{cor};color:#fff;padding:9px 18px;'
        f'border-radius:6px;text-decoration:none;font-size:13px;font-weight:bold;'
        f'display:inline-block;margin-right:8px">'
        f'&#128279; Acessar Edital no Portal</a>'
    )
    btn_pncp = (
        "" if mesmo_link else
        f'<a href="{link_pncp}" style="background:#fff;color:{cor};padding:9px 18px;'
        f'border-radius:6px;text-decoration:none;font-size:13px;font-weight:bold;'
        f'border:2px solid {cor};display:inline-block">'
        f'&#128196; Ver no PNCP</a>'
    )

    data_fim = item.get("data_fim", "Nao informado")
    horario  = item.get("horario",  "Nao informado")

    return f"""
<div style="background:#ffffff;border:1px solid #e0e0e0;border-left:5px solid {cor};
    border-radius:8px;padding:18px;margin:10px 0;box-shadow:0 2px 6px rgba(0,0,0,0.05)">

  <div style="margin-bottom:10px">{uf_badge}{mod_badge}</div>

  <table style="width:100%;border-collapse:collapse;font-size:13.5px">
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#777;font-weight:bold;width:190px;white-space:nowrap">&#127970; Orgao</td>
      <td style="padding:6px 10px;color:#111;font-weight:bold">{item.get("orgao","N/I")}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">
      <td style="padding:6px 10px;color:#777;font-weight:bold;vertical-align:top">&#128203; Objeto</td>
      <td style="padding:6px 10px;color:#333;line-height:1.6">{item.get("objeto","")[:450]}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#777;font-weight:bold">&#128197; Data fim proposta</td>
      <td style="padding:6px 10px;color:#111;font-weight:bold">{data_fim}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">
      <td style="padding:6px 10px;color:#777;font-weight:bold">&#128336; Horario da sessao</td>
      <td style="padding:6px 10px;color:#111;font-weight:bold">{horario}</td>
    </tr>
    <tr style="border-bottom:1px solid #f5f5f5">
      <td style="padding:6px 10px;color:#777;font-weight:bold">&#127760; Portal</td>
      <td style="padding:6px 10px;color:#111">{item.get("portal","PNCP")}</td>
    </tr>
    <tr style="background:#f1f8e9">
      <td style="padding:8px 10px;color:#2e7d32;font-weight:bold">&#128176; Valor estimado</td>
      <td style="padding:8px 10px;color:#1b5e20;font-weight:bold;font-size:16px">{item.get("valor","Nao informado")}</td>
    </tr>
  </table>

  <div style="margin-top:14px">
    {btn_externo}{btn_pncp}
  </div>
</div>"""


def secao_cliente_html(cliente, resultados):
    cor    = cliente["cor"]
    nome   = cliente["nome"]
    filtro = cliente["filtro"]
    emoji  = cliente["emoji"]
    total  = len(resultados)
    badge  = "&#128293;" if total > 0 else "&#128564;"

    estados_str = ", ".join(e if e else "BRASIL INTEIRO" for e in cliente["estados"])
    val_str = f" | Min: {fmt_valor(cliente['valor_min'])}" if cliente["valor_min"] > 0 else ""

    if resultados:
        cards = "".join(card_html(r, cor) for r in resultados)
    else:
        cards = """
<div style="background:#fafafa;padding:20px;border-radius:8px;
    text-align:center;color:#bbb;border:1px dashed #ddd">
  <p style="margin:0;font-size:15px">Nenhuma licitacao encontrada hoje.</p>
  <p style="margin:6px 0 0;font-size:12px">O monitor verifica novamente amanha as 08:30.</p>
</div>"""

    return f"""
<div style="margin:16px 0;border-radius:10px;overflow:hidden;
    box-shadow:0 3px 10px rgba(0,0,0,0.08);border:1px solid #e0e0e0">
  <div style="background:{cor};padding:16px 20px">
    <h2 style="color:#fff;margin:0;font-size:16px;font-weight:bold">
      {badge} {emoji} {filtro}
    </h2>
    <p style="color:rgba(255,255,255,0.92);margin:4px 0 0;font-size:13px;font-weight:bold">
      Cliente: {nome}
    </p>
    <p style="color:rgba(255,255,255,0.75);margin:2px 0 0;font-size:12px">
      &#128205; {estados_str}{val_str} &nbsp;&#183;&nbsp;
      <b style="color:#fff">{total}</b> licitacao(oes)
    </p>
  </div>
  <div style="background:#f7f9fc;padding:14px 16px">
    {cards}
  </div>
</div>"""


def rodar():
    hoje     = datetime.now().strftime("%Y%m%d")
    data_fmt = datetime.now().strftime("%d/%m/%Y")

    print(f"\n{'='*60}")
    print(f"  MONITOR PNCP - Grupo Cantanhede - {data_fmt}")
    print(f"{'='*60}")

    resultados_por_cliente = {c["nome"]: [] for c in CLIENTES}

    for cliente in CLIENTES:
        print(f"\n&#128269; {cliente['filtro']}")
        vistos = set()

        for uf in cliente["estados"]:
            for mod_id, mod_nome in cliente["modalidades"].items():
                max_pag = 15 if uf is None else 10
                print(f"  {mod_nome} | UF: {uf or 'BRASIL'}")
                items = buscar_licitacoes(hoje, uf=uf, mod_id=mod_id, max_pag=max_pag)

                for item in items:
                    obj   = item.get("objetoCompra", "")
                    valor = item.get("valorTotalEstimado") or 0
                    num   = item.get("numeroControlePNCP", "")

                    if num in vistos:
                        continue
                    if not tem_palavra(obj, cliente["palavras"]):
                        continue
                    if valor < cliente["valor_min"]:
                        continue

                    vistos.add(num)

                    dt_raw   = item.get("dataEncerramentoProposta") or item.get("dataAberturaProposta") or ""
                    data_fim, horario = fmt_data_hora(dt_raw)

                    uf_real = ""
                    try:
                        uf_real = item.get("unidadeOrgao", {}).get("ufSigla", "") or uf or ""
                    except:
                        uf_real = uf or ""

                    link_sistema = item.get("linkSistemaOrigem", "") or ""
                    portal_nome  = extrair_portal(link_sistema)

                    resultados_por_cliente[cliente["nome"]].append({
                        "orgao":     item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                        "objeto":    obj,
                        "data_fim":  data_fim,
                        "horario":   horario,
                        "portal":    portal_nome,
                        "valor":     fmt_valor(valor),
                        "modalidade": mod_nome,
                        "uf":        uf_real,
                        "numero":    num,
                        "_raw":      item,   # item original da API para gerar links corretos
                    })

        total_c = len(resultados_por_cliente[cliente["nome"]])
        print(f"  OK {total_c} resultado(s)")

    enviar_email(data_fmt, resultados_por_cliente)


def enviar_email(data, resultados_por_cliente):
    total_geral  = sum(len(v) for v in resultados_por_cliente.values())
    emoji_titulo = "&#128293;" if total_geral > 0 else "&#128564;"

    secoes = "".join(
        secao_cliente_html(c, resultados_por_cliente[c["nome"]])
        for c in CLIENTES
    )

    rows = ""
    for c in CLIENTES:
        t     = len(resultados_por_cliente[c["nome"]])
        cor_n = c["cor"] if t > 0 else "#bbb"
        rows += (
            f'<tr style="border-bottom:1px solid #f0f0f0">'
            f'<td style="padding:8px 14px">{c["emoji"]} <b>{c["nome"]}</b></td>'
            f'<td style="padding:8px 14px;text-align:center">'
            f'<span style="background:{cor_n};color:#fff;padding:3px 12px;'
            f'border-radius:12px;font-weight:bold;font-size:13px">{t}</span></td>'
            f'<td style="padding:8px 14px;font-size:12px;color:#888">'
            f'{", ".join(e if e else "Brasil" for e in c["estados"])}</td></tr>'
        )

    html = f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;background:#f0f2f5;margin:0;padding:16px">
<div style="max-width:820px;margin:auto">

  <!-- HEADER BRANCO -->
  <div style="background:#ffffff;padding:24px 28px;border-radius:12px 12px 0 0;
      border:1px solid #e0e0e0;border-bottom:4px solid #1565c0">
    <table style="width:100%"><tr>
      <td>
        <h1 style="color:#1a1a2e;margin:0;font-size:22px;font-weight:bold">
          {emoji_titulo} Monitor PNCP &#8212; Grupo Cantanhede
        </h1>
        <p style="color:#666;margin:6px 0 0;font-size:14px">
          &#128197; {data} &nbsp;&#183;&nbsp;
          <b style="color:#1565c0">{total_geral} licitacao(oes) encontrada(s)</b>
        </p>
      </td>
      <td style="text-align:right;vertical-align:middle">
        <span style="background:#1565c0;color:#fff;padding:8px 18px;
          border-radius:20px;font-size:14px;font-weight:bold">{total_geral} resultados</span>
      </td>
    </tr></table>
  </div>

  <!-- RESUMO -->
  <div style="background:#fff;padding:18px 24px;
      border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0">
    <p style="margin:0 0 10px;color:#444;font-weight:bold;font-size:14px">
      &#128202; Resumo por cliente
    </p>
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="background:#f5f7ff">
          <th style="padding:8px 14px;text-align:left;color:#444">Cliente</th>
          <th style="padding:8px 14px;text-align:center;color:#444">Resultados</th>
          <th style="padding:8px 14px;text-align:left;color:#444">Estados</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <!-- SECOES POR CLIENTE -->
  <div style="padding:6px 0">{secoes}</div>

  <!-- RODAPE -->
  <div style="background:#fff;padding:12px 20px;border-radius:0 0 12px 12px;
      border:1px solid #e0e0e0;border-top:2px solid #e0e0e0;text-align:center">
    <p style="color:#aaa;margin:0;font-size:11px">
      Monitor automatico &#183; Grupo Cantanhede &#183; {data} as 08:30 (Brasilia)
      &#183; Campos: Orgao &#183; Objeto &#183; Data fim &#183; Horario &#183; Portal &#183; Valor &#183; Link direto
    </p>
  </div>

</div></body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"PNCP {data} - {total_geral} licitacao(oes) | U.Relvas / Express / Linhares"
    msg["From"]    = EMAIL_REMETENTE
    msg["To"]      = EMAIL_DESTINATARIO
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
        srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())

    print(f"\nEmail enviado! {total_geral} resultado(s).")


if __name__ == "__main__":
    rodar()
