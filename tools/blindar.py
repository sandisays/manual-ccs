#!/usr/bin/env python3
"""Aplica as proteções de publicação ao index.html do Manual (e ao da pasta manual-generico).

Rode sempre que o index.html for gerado de novo, antes de publicar:
    python3 tools/blindar.py        (pede a senha do manual)
Precisa de: pip install cryptography

O que faz (pode rodar várias vezes; só altera o que ainda falta):
  1. Tira a chamada ao Google Fonts e embute a fonte Fredoka na própria página (uso offline).
  2. Adiciona a política de segurança (CSP): a página só conversa com o próprio endereço.
  3. Move o logo e a linha de descrição do cabeçalho para dentro do conteúdo criptografado,
     para que nada da empresa apareça para quem não tem a senha.
  4. Põe o botão Sair no cabeçalho: apaga a chave guardada na aba e volta para a tela de senha
     (útil em computador compartilhado).
Depois rode  python3 tools/verificar.py  para conferir.
"""
import base64, getpass, gzip, hashlib, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fontes')
PAGINAS = ['index.html', os.path.join('manual-generico', 'index.html')]
CSP = ("default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; "
       "img-src 'self' data: blob:; font-src data:; connect-src 'self' data: blob:; "
       "frame-src 'self' data: blob:; form-action 'none'; base-uri 'none'")
META = '<meta http-equiv="Content-Security-Policy" content="%s">' % CSP
MARCA = '/*cabecalho-protegido*/'
ICONE_SAIR = ('<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M5 22a1 1 0 0 1-1-1V3'
              'a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v3h-2V4H6v16h12v-2h2v3a1 1 0 0 1-1 1H5zm13-6v-3h-7v-2h7V8l5 4-5 4z"/></svg>')
SAIR = ('<button class="tg ic" id="sair" type="button" aria-label="Sair" title="Sair">%s</button>' % ICONE_SAIR)
# no computador o Voltar vai para a esquerda do Sair; no celular não há espaço, então o Sair
# ocupa o lugar do Voltar e some enquanto o Voltar estiver visível
SAIR_CSS = ('<style id="sair-css">#sair{right:108px}header #bk.tg{right:154px}'
            '@media (max-width:600px){#sair{right:96px}header #bk.tg{right:96px}#bk:not([hidden])~#sair{display:none}}</style>')
SAIR_JS = ('<script id="sair-js">document.getElementById("sair").onclick=function(){'
           'try{sessionStorage.removeItem("ccs-k")}catch(e){}location.reload()};</script>')
b64d, b64e = base64.b64decode, lambda x: base64.b64encode(x).decode()


def fonte_css():
    css = ''
    for peso in ('600', '700'):
        dados = open(os.path.join(FONTES, 'fredoka-latin-%s-normal.woff2' % peso), 'rb').read()
        css += ("@font-face{font-family:'Fredoka';font-weight:%s;font-style:normal;font-display:swap;"
                "src:url(data:font/woff2;base64,%s) format('woff2')}" % (peso, b64e(dados)))
    return '<style id="fonte-embutida">' + css + '</style>'


def blindar(caminho, senha):
    html = open(caminho, encoding='utf-8').read()
    feito = []
    m = re.search(r'(<script id="encdata"[^>]*>)(.*?)(</script>)', html, re.S)
    P = json.loads(m.group(2))
    try:
        chave_senha = hashlib.pbkdf2_hmac('sha256', senha, b64d(P['s']), P['it'], 32)
        chave = AESGCM(chave_senha).decrypt(b64d(P['wi']), b64d(P['w']), None)
    except Exception:
        sys.exit('%s: senha incorreta. Nada foi alterado.' % caminho)
    antes, depois = html[:m.start()], html[m.end():]

    # 1. fonte embutida no lugar do Google Fonts
    novo = re.sub(r'<link[^>]+fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', antes)
    if novo != antes:
        antes = novo
        feito.append('Google Fonts removido')
    if 'id="fonte-embutida"' not in antes and "'Fredoka'" in antes:
        antes = antes.replace('</head>', fonte_css() + '</head>', 1)
        feito.append('fonte embutida')

    # 2. CSP logo depois do primeiro <head>
    if 'Content-Security-Policy' not in antes:
        antes = re.sub(r'<head>', lambda _: '<head>' + META, antes, count=1)
        feito.append('CSP adicionada')

    # 3. logo e descrição do cabeçalho vão para dentro do conteúdo criptografado
    cab = re.search(r'<header>.*?</header>', antes, re.S)
    logo = cab and re.search(r'<img class="lg"[^>]*>', cab.group(0))
    desc = cab and re.search(r'<p>(.+?)</p>', cab.group(0), re.S)
    if cab and (logo or desc):
        novo_cab, partes = cab.group(0), {}
        if logo:
            partes['logo'] = logo.group(0)
            novo_cab = novo_cab.replace(logo.group(0), '')
        if desc:
            partes['desc'] = desc.group(1)
            novo_cab = novo_cab.replace(desc.group(0), '<p></p>')
        antes = antes.replace(cab.group(0), novo_cab)
        claro = AESGCM(chave).decrypt(b64d(P['iv']), b64d(P['c']), None)
        texto = gzip.decompress(claro).decode() if P.get('z') else claro.decode()
        if texto.startswith(MARCA):  # tira o bloco de uma execução anterior
            texto = texto.split(MARCA, 2)[2].lstrip('\n')
        # o bloco entra ANTES do resto, porque o manual atualiza a data "revisado em" lendo esse texto
        texto = MARCA + (
            ';(function(){var c=%s,h=document.querySelector("header h1"),p=document.querySelector("header p");'
            'if(c.logo&&h)h.insertAdjacentHTML("afterbegin",c.logo);if(c.desc&&p)p.innerHTML=c.desc})();'
            % json.dumps(partes, ensure_ascii=False)) + MARCA + '\n' + texto
        dados = texto.encode()
        if P.get('z'):
            dados = gzip.compress(dados, 9, mtime=0)
        iv = os.urandom(12)
        P['iv'], P['c'] = b64e(iv), b64e(AESGCM(chave).encrypt(iv, dados, None))
        feito.append('cabeçalho protegido')

    # 4. botão Sair
    css_atual = re.search(r'<style id="sair-css">.*?</style>', antes, re.S)
    if css_atual and css_atual.group(0) != SAIR_CSS:
        antes = antes.replace(css_atual.group(0), SAIR_CSS)
        feito.append('estilo do botão Sair atualizado')
    if 'id="sair"' not in antes and 'id="tg"' in antes:
        antes = re.sub(r'(<button class="tg ic" id="tg"[^>]*>.*?</button>)', lambda x: x.group(1) + SAIR, antes, count=1, flags=re.S)
        antes = antes.replace('</head>', SAIR_CSS + '</head>', 1)
        depois = depois.replace('</body>', SAIR_JS + '</body>', 1)
        feito.append('botão Sair')

    saida = antes + m.group(1) + json.dumps(P, separators=(',', ':')) + m.group(3) + depois
    if saida != html:
        open(caminho, 'w', encoding='utf-8').write(saida)
    print('%s: %s' % (os.path.relpath(caminho, RAIZ), ', '.join(feito) or 'já estava protegido'))


if __name__ == '__main__':
    senha = (os.environ.get('MANUAL_SENHA') or getpass.getpass('Senha do manual: ')).strip().upper().encode()
    for p in PAGINAS:
        c = os.path.join(RAIZ, p)
        if os.path.exists(c):
            blindar(c, senha)
