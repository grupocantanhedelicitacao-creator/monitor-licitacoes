#!/usr/bin/env python3
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
            "monitoramento eletronico","monitoramento eletr\u00f4nico",
            "videomonitoramento","video monitoramento",
            "vigilancia eletronica","vigil\u00e2ncia eletr\u00f4nica",
            "controle de acesso","sistema de seguranca","sistema de seguran\u00e7a",
            "cameras de seguranca","c\u00e2meras de seguran\u00e7a",
            "camera de seguranca","c\u00e2mera de seguran\u00e7a",
            "instalacao de cameras","instala\u00e7\u00e3o de c\u00e2meras",
            "manutencao de sistemas de seguranca",
            "seguranca eletronica","seguran\u00e7a eletr\u00f4nica"
        ],
        "valor_min": 0,
        "cor": "#1565c0",
        "emoji": "&#128249;"
    },
    {
        "nome": "EXPRESS ALIMENTOS",
        "filtro": "FILTRO 2 - EXPRESS ALIMENTOS (PARA)",
        "estados": ["PA"],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "refei\u00e7\u00e3o","refeicao","refei\u00e7\u00f5es","refeicoes",
            "fornecimento de alimentos","generos alimenticios","g\u00eaneros aliment\u00edcios",
            "alimentacao coletiva","alimenta\u00e7\u00e3o coletiva",
            "merenda","marmitex","quentinha","quentinhas",
            "servicos de alimentacao","servi\u00e7os de alimenta\u00e7\u00e3o",
            "preparo e distribuicao","fornecimento de alimentacao",
            "refeicao coletiva","refei\u00e7\u00e3o coletiva",
            "alimentacao escolar","cozinha industrial"
        ],
        "valor_min": 2000000,
        "cor": "#e65100",
        "emoji": "&#127869;"
    },
    {
        "nome": "EXPRESS ALIMENTOS - NACIONAL",
        "filtro": "FILTRO 3 - ALIMENTOS (BRASIL TODO - ESCALA)",
        "estados": [None],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "fornecimento de alimentos","refei\u00e7\u00e3o","refeicao","refei\u00e7\u00f5es","refeicoes",
            "alimentacao coletiva","alimenta\u00e7\u00e3o coletiva",
            "generos alimenticios","g\u00eaneros aliment\u00edcios",
            "merenda escolar","preparo de alimentos",
            "cozinha industrial","servicos de alimentacao",
            "refeicao coletiva","refei\u00e7\u00e3o coletiva",
            "alimentacao escolar"
        ],
        "valor_min": 3000000,
        "cor": "#b71c1c",
        "emoji": "&#127758;"
    },
    {
        "nome": "LINHARES DISTRIBUIDORA",
        "filtro": "FILTRO 4 - LINHARES DISTRIBUIDORA (MINAS GERAIS)",
        "estados": ["MG"],
        "modalidades": {6: "Pregao Eletronico", 8: "Dispensa Eletronica", 4: "Concorrencia"},
        "palavras": [
            "genero alimenticio","g\u00eanero aliment\u00edcio",
            "generos alimenticios","g\u00eaneros aliment\u00edcios",
            "aquisicao de alimentos","aquisi\u00e7\u00e3o de alimentos",
            "fornecimento de alimentos","produtos alimenticios",
            "distribuicao de alimentos","distribui\u00e7\u00e3o de alimentos",
            "cesta basica","cesta b\u00e1sica","merenda escolar",
            "alimentos nao pereciveis","atacado de alimentos",
            "material de consumo alimenticio"
        ],
        "valor_min": 0,
        "cor": "#1b5e20",
        "emoji": "&#127968;"
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
    cnpj = ""
    try:
        cnpj = item_raw["orgaoEntidade"]["cnpj"].replace(".", "").replace("/", "").replace("-", "")
    except:
        pass
    ano = item_raw.get("anoCompra", "")
    seq = item_raw.get("sequencialCompra", "")
    link_pncp = (
        "https://pncp.gov.br/app/editais/" + str(cnpj) + "/" + str(ano) + "/" + str(seq)
        if cnpj and ano and seq
        else "https://pncp.gov.br/app/editais"
    )
    link_externo = (item_raw.get("linkSistemaOrigem") or "").strip().rstrip("/")
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
    data_fim = item.get("data_fim", "Nao informado")
    horario  = item.get("horario",  "Nao informado")
    orgao    = item.get("orgao",    "N/I")
    objeto   = item.get("objeto",   "")[:450]
    valor    = item.get("valor",    "Nao informado")
    portal   = item.get("portal",   "PNCP")
    modalidade = item.get("modalidade", "")

    uf_badge = (
        '<span style="background:#e3f2fd;color:#1565c0;padding:2px 10px;'
        'border-radius:12px;font-size:11px;font-weight:bold;margin-right:5px">'
        '&#128205; ' + uf + '</span>'
    ) if uf else ""

    mod_badge = (
        '<span style="background:#fff8e1;color:#f57f17;padding:2px 10px;'
        'border-radius:12px;font-size:11px;margin-right:5px">'
        '&#128204; ' + modalidade + '</span>'
    )

    btn_edital = (
        '<a href="' + link_edital + '" style="background:' + cor + ';color:#fff;'
        'padding:9px 18px;border-radius:6px;text-decoration:none;font-size:13px;'
        'font-weight:bold;display:inline-block;margin-right:8px">'
        '&#128279; Acessar Edital no Portal</a>'
    )

    btn_pncp = "" if mesmo_link else (
        '<a href="' + link_pncp + '" style="background:#fff;color:' + cor + ';'
        'padding:9px 18px;border-radius:6px;text-decoration:none;font-size:13px;'
        'font-weight:bold;border:2px solid ' + cor + ';display:inline-block">'
        '&#128196; Ver no PNCP</a>'
    )

    return (
        '<div style="background:#ffffff;border:1px solid #e0e0e0;border-left:5px solid '
        + cor +
        ';border-radius:8px;padding:18px;margin:10px 0;box-shadow:0 2px 6px rgba(0,0,0,0.05)">'
        '<div style="margin-bottom:10px">' + uf_badge + mod_badge + '</div>'
        '<table style="width:100%;border-collapse:collapse;font-size:13.5px">'
        '<tr style="border-bottom:1px solid #f5f5f5">'
        '<td style="padding:6px 10px;color:#777;font-weight:bold;width:190px;white-space:nowrap">&#127970; Orgao</td>'
        '<td style="padding:6px 10px;color:#111;font-weight:bold">' + orgao + '</td>'
        '</tr>'
        '<tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">'
        '<td style="padding:6px 10px;color:#777;font-weight:bold;vertical-align:top">&#128203; Objeto</td>'
        '<td style="padding:6px 10px;color:#333;line-height:1.6">' + objeto + '</td>'
        '</tr>'
        '<tr style="border-bottom:1px solid #f5f5f5">'
        '<td style="padding:6px 10px;color:#777;font-weight:bold">&#128197; Data fim proposta</td>'
        '<td style="padding:6px 10px;color:#111;font-weight:bold">' + data_fim + '</td>'
        '</tr>'
        '<tr style="border-bottom:1px solid #f5f5f5;background:#fafafa">'
        '<td style="padding:6px 10px;color:#777;font-weight:bold">&#128336; Horario da sessao</td>'
        '<td style="padding:6px 10px;color:#111;font-weight:bold">' + horario + '</td>'
        '</tr>'
        '<tr style="border-bottom:1px solid #f5f5f5">'
        '<td style="padding:6px 10px;color:#777;font-weight:bold">&#127760; Portal</td>'
        '<td style="padding:6px 10px;color:#111">' + portal + '</td>'
        '</tr>'
        '<tr style="background:#f1f8e9">'
        '<td style="padding:8px 10px;color:#2e7d32;font-weight:bold">&#128176; Valor estimado</td>'
        '<td style="padding:8px 10px;color:#1b5e20;font-weight:bold;font-size:16px">' + valor + '</td>'
        '</tr>'
        '</table>'
        '<div style="margin-top:14px">' + btn_edital + btn_pncp + '</div>'
        '</div>'
    )


def secao_cliente_html(cliente, resultados):
    cor    = cliente["cor"]
    nome   = cliente["nome"]
    filtro = cliente["filtro"]
    emoji  = cliente["emoji"]
    total  = len(resultados)
    badge  = "&#128293;" if total > 0 else "&#128564;"

    estados_str = ", ".join(e if e else "BRASIL INTEIRO" for e in cliente["estados"])
    val_str = " | Min: " + fmt_valor(cliente["valor_min"]) if cliente["valor_min"] > 0 else ""

    if resultados:
        cards = "".join(card_html(r, cor) for r in resultados)
    else:
        cards = (
            '<div style="background:#fafafa;padding:20px;border-radius:8px;'
            'text-align:center;color:#bbb;border:1px dashed #ddd">'
            '<p style="margin:0;font-size:15px">Nenhuma licitacao encontrada hoje.</p>'
            '<p style="margin:6px 0 0;font-size:12px">Monitor verifica novamente amanha as 08:30.</p>'
            '</div>'
        )

    return (
        '<div style="margin:16px 0;border-radius:10px;overflow:hidden;'
        'box-shadow:0 3px 10px rgba(0,0,0,0.08);border:1px solid #e0e0e0">'
        '<div style="background:' + cor + ';padding:16px 20px">'
        '<h2 style="color:#fff;margin:0;font-size:16px;font-weight:bold">'
        + badge + ' ' + emoji + ' ' + filtro +
        '</h2>'
        '<p style="color:rgba(255,255,255,0.92);margin:4px 0 0;font-size:13px;font-weight:bold">'
        'Cliente: ' + nome +
        '</p>'
        '<p style="color:rgba(255,255,255,0.75);margin:2px 0 0;font-size:12px">'
        '&#128205; ' + estados_str + val_str + ' &nbsp;&#183;&nbsp; '
        '<b style="color:#fff">' + str(total) + '</b> licitacao(oes)'
        '</p>'
        '</div>'
        '<div style="background:#f7f9fc;padding:14px 16px">'
        + cards +
        '</div>'
        '</div>'
    )


def rodar():
    hoje     = datetime.now().strftime("%Y%m%d")
    data_fmt = datetime.now().strftime("%d/%m/%Y")

    print("\n" + "="*60)
    print("  MONITOR PNCP - Grupo Cantanhede - " + data_fmt)
    print("="*60)

    resultados_por_cliente = {c["nome"]: [] for c in CLIENTES}

    for cliente in CLIENTES:
        print("\nFiltro: " + cliente["filtro"])
        vistos = set()

        for uf in cliente["estados"]:
            for mod_id, mod_nome in cliente["modalidades"].items():
                max_pag = 15 if uf is None else 10
                print("  " + mod_nome + " | UF: " + str(uf or "BRASIL"))
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
                        "orgao":      item.get("orgaoEntidade", {}).get("razaoSocial", "N/I"),
                        "objeto":     obj,
                        "data_fim":   data_fim,
                        "horario":    horario,
                        "portal":     portal_nome,
                        "valor":      fmt_valor(valor),
                        "modalidade": mod_nome,
                        "uf":         uf_real,
                        "numero":     num,
                        "_raw":       item,
                    })

        total_c = len(resultados_por_cliente[cliente["nome"]])
        print("  -> " + str(total_c) + " resultado(s)")

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
            '<tr style="border-bottom:1px solid #f0f0f0">'
            '<td style="padding:8px 14px">' + c["emoji"] + ' <b>' + c["nome"] + '</b></td>'
            '<td style="padding:8px 14px;text-align:center">'
            '<span style="background:' + cor_n + ';color:#fff;padding:3px 12px;'
            'border-radius:12px;font-weight:bold;font-size:13px">' + str(t) + '</span></td>'
            '<td style="padding:8px 14px;font-size:12px;color:#888">'
            + ", ".join(e if e else "Brasil" for e in c["estados"]) +
            '</td></tr>'
        )

    html = (
        '<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;'
        'background:#f0f2f5;margin:0;padding:16px">'
        '<div style="max-width:820px;margin:auto">'
        '<div style="background:#ffffff;padding:24px 28px;border-radius:12px 12px 0 0;border:1px solid #e0e0e0;border-bottom:4px solid #1565c0">'
        '<table style="width:100%"><tr><td>'
        '<h1 style="color:#1a1a2e;margin:0;font-size:22px;font-weight:bold">'
        + emoji_titulo + ' Monitor PNCP &#8212; Grupo Cantanhede</h1>'
        '<p style="color:#666;margin:6px 0 0;font-size:14px">&#128197; '
        + data + ' &nbsp;&#183; '
        '<b style="color:#1565c0">' + str(total_geral) + ' licitacao(oes)</b></p>'
        '</td><td style="text-align:right;vertical-align:middle">'
        '<span style="background:#1565c0;color:#fff;padding:8px 18px;border-radius:20px;font-size:14px;font-weight:bold">'
        + str(total_geral) + ' resultados</span></td></tr></table></div>'
        '<div style="background:#fff;padding:18px 24px;border-left:1px solid #e0e0e0;border-right:1px solid #e0e0e0">'
        '<p style="margin:0 0 10px;color:#444;font-weight:bold;font-size:14px">&#128202; Resumo por cliente</p>'
        '<table style="width:100%;border-collapse:collapse;font-size:14px">'
        '<thead><tr style="background:#f5f7ff">'
        '<th style="padding:8px 14px;text-align:left;color:#444">Cliente</th>'
        '<th style="padding:8px 14px;text-align:center;color:#444">Resultados</th>'
        '<th style="padding:8px 14px;text-align:left;color:#444">Estados</th>'
        '</tr></thead><tbody>' + rows + '</tbody></table></div>'
        '<div style="padding:6px 0">' + secoes + '</div>'
        '<div style="background:#fff;padding:12px 20px;border-radius:0 0 12px 12px;border:1px solid #e0e0e0;border-top:2px solid #e0e0e0;text-align:center">'
        '<p style="color:#aaa;margin:0;font-size:11px">Monitor automatico &#183; Grupo Cantanhede &#183; '
        + data + ' as 08:30 (Brasilia)</p></div>'
        '</div></body></html>'
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "PNCP " + data + " - " + str(total_geral) + " licitacao(oes) | U.Relvas / Express / Linhares"
    msg["From"]    = EMAIL_REMETENTE
    msg["To"]      = EMAIL_DESTINATARIJ
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
        srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())

    print("\nEmail enviado! " + str(total_geral) + " resultado(s).")


if __name__ == "__main__":
    rodar()
