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
    msg["To"]      = EMAIL_DESTINATARIO
    msg.attach(MIMEText(html, "html", "utf-8"))


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
        srv.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        srv.sendmail(EMAIL_REMETENTE, EMAIL_DESTINATARIO, msg.as_string())


    print("\nEmail enviado! " + str(total_geral) + " resultado(s).")




if __name__ == "__main__":
    rodar()

