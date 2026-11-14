#!/usr/bin/env python3
"""Confere se o manual está pronto para publicar. Rode antes de cada publicação.

Uso:  python3 tools/verificar.py            (checagens que não precisam de senha)
      python3 tools/verificar.py --senha    (também abre todos os arquivos com a senha)

Confere, em index.html e manual-generico/index.html:
  1. Política de segurança (CSP) presente e sem endereços externos.
  2. Nenhum recurso carregado de fora (fontes, scripts, imagens, estilos).
  3. Nenhuma palavra reservada visível sem a senha (lista PALAVRAS abaixo).
  4. Cabeçalho sem logo nem descrição fora da parte criptografada.
  5. Todos os arquivos de enc/ no formato criptografado.
  6. Com --senha: todos os arquivos abrem com a chave atual.
"""
import base64, getpass, glob, hashlib, json, os, re, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PALAVRAS = ['seara', 'jbs']  # nomes que não podem aparecer para quem não tem a senha
problemas = []


def erro(pasta, msg):
    problemas.append('%s: %s' % (os.path.relpath(pasta, RAIZ) or '.', msg))


def conferir(pasta, senha):
    html = open(os.path.join(pasta, 'index.html'), encoding='utf-8').read()
    m = re.search(r'<script id="encdata"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return erro(pasta, 'index.html sem o bloco criptografado (encdata)')
    P = json.loads(m.group(1))
    aberto = html[:m.start()] + html[m.end():]
    sem_blob = re.sub(r'[A-Za-z0-9+/=]{300,}', '', aberto)

    csp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]*)"', aberto)
    if not csp:
        erro(pasta, 'falta a política de segurança (CSP): rode tools/blindar.py')
    elif 'http' in csp.group(1) or "default-src 'none'" not in csp.group(1):
        erro(pasta, 'CSP permite endereços externos')
    externos = re.findall(r'<(?:link|script|img|iframe|source)\b[^>]*?(?:href|src)=["\']?(https?:[^"\' >]+)', sem_blob)
    externos += re.findall(r'(?:url\(|@import\s+)["\']?(https?:[^"\')]+)', sem_blob)
    if externos:
        erro(pasta, 'carrega recurso externo: %s (rode tools/blindar.py)' % ', '.join(sorted(set(externos))[:3]))
    baixo = sem_blob.lower()
    for p in PALAVRAS:
        if re.search(r'\b%s\b' % re.escape(p), baixo):
            erro(pasta, 'a palavra "%s" aparece sem senha (rode tools/blindar.py ou ajuste o texto)' % p)
    cab = re.search(r'<header>.*?</header>', aberto, re.S)
    if cab and (re.search(r'<img class="lg"', cab.group(0)) or re.search(r'<p>[^<]+</p>', cab.group(0))):
        erro(pasta, 'logo ou descrição do cabeçalho fora da parte criptografada (rode tools/blindar.py)')

    chave = None
    if senha:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        try:
            k = hashlib.pbkdf2_hmac('sha256', senha, base64.b64decode(P['s']), P['it'], 32)
            chave = AESGCM(AESGCM(k).decrypt(base64.b64decode(P['wi']), base64.b64decode(P['w']), None))
            chave.decrypt(base64.b64decode(P['iv']), base64.b64decode(P['c']), None)
        except Exception:
            erro(pasta, 'a senha não abre o index.html')
            chave = None

    itens = []
    for f in glob.glob(os.path.join(pasta, 'enc', '*')):
        nome = os.path.basename(f)
        if f.endswith('.json'):
            try:
                itens += [(nome + ':' + k, v) for k, v in json.load(open(f, encoding='utf-8')).items()]
            except Exception:
                erro(pasta, 'enc/%s não é um pacote válido' % nome)
        elif f.endswith('.txt'):
            itens.append((nome, open(f, encoding='utf-8').read()))
        else:
            erro(pasta, 'enc/%s não está criptografado (extensão inesperada)' % nome)
    for nome, texto in itens:
        try:
            bruto = base64.b64decode(texto.strip(), validate=True)
            assert len(bruto) > 28
            if chave:
                chave.decrypt(bruto[:12], bruto[12:], None)
        except Exception:
            erro(pasta, 'enc/%s %s' % (nome, 'não abre com a chave atual' if chave else 'não está no formato criptografado'))
    print('%s: %d arquivos em enc/ conferidos%s' % (os.path.relpath(pasta, RAIZ) or '.', len(itens), ' e abertos com a senha' if chave else ''))


if __name__ == '__main__':
    senha = None
    if '--senha' in sys.argv:
        senha = (os.environ.get('MANUAL_SENHA') or getpass.getpass('Senha do manual: ')).strip().upper().encode()
    for pasta in (RAIZ, os.path.join(RAIZ, 'manual-generico')):
        if os.path.exists(os.path.join(pasta, 'index.html')):
            conferir(pasta, senha)
    if problemas:
        print('\nNÃO PUBLICAR. Problemas encontrados:')
        for p in problemas:
            print('  -', p)
        sys.exit(1)
    print('OK: pode publicar.')
