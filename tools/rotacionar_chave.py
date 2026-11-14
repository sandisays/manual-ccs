#!/usr/bin/env python3
"""Gera uma chave nova e recriptografa TODO o manual (e a pasta manual-generico, se existir).

Quando usar: sempre que alguém que conhecia a senha sair da equipe, ou se houver suspeita
de que a senha ou a chave vazou. Trocar só a senha (trocar_senha.py) NÃO basta nesses
casos, porque a chave do conteúdo continua a mesma.

Uso:  python3 tools/rotacionar_chave.py     (pede a senha atual e a nova)
Precisa de: pip install cryptography

Atenção:
  - Todos os arquivos de enc/ são reescritos; todos precisam entrar de novo com a senha nova.
  - As versões antigas continuam no histórico do repositório, abríveis com a senha antiga.
    Para valer de verdade, publique a partir de um repositório novo (sem o histórico).
  - Antes de gravar, o script confere que conseguiu abrir todos os arquivos. Se algum falhar,
    nada é alterado.
"""
import base64, getpass, glob, hashlib, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
b64d, b64e = base64.b64decode, lambda x: base64.b64encode(x).decode()
norm = lambda s: s.strip().upper().encode()
MINIMO = 12


def deriva(senha, sal, it):
    return hashlib.pbkdf2_hmac('sha256', senha, sal, it, 32)


def abre(chave, texto_b64):
    bruto = b64d(texto_b64.strip())
    return AESGCM(chave).decrypt(bruto[:12], bruto[12:], None)


def fecha(chave, claro):
    iv = os.urandom(12)
    return b64e(iv + AESGCM(chave).encrypt(iv, claro, None))


def rotacionar(pasta, senha_atual, senha_nova):
    arq = os.path.join(pasta, 'index.html')
    html = open(arq, encoding='utf-8').read()
    m = re.search(r'(<script id="encdata"[^>]*>)(.*?)(</script>)', html, re.S)
    P = json.loads(m.group(2))
    try:
        velha = AESGCM(deriva(senha_atual, b64d(P['s']), P['it'])).decrypt(b64d(P['wi']), b64d(P['w']), None)
    except Exception:
        sys.exit('%s: senha atual incorreta. Nada foi alterado.' % arq)
    nova = os.urandom(32)

    # 1) abre tudo com a chave velha (em memória); qualquer falha interrompe sem gravar nada
    gravar = {}
    conteudo = AESGCM(velha).decrypt(b64d(P['iv']), b64d(P['c']), None)
    for f in sorted(glob.glob(os.path.join(pasta, 'enc', '*.txt'))):
        gravar[f] = fecha(nova, abre(velha, open(f, encoding='utf-8').read()))
    for f in sorted(glob.glob(os.path.join(pasta, 'enc', '*.json'))):
        pacote = json.load(open(f, encoding='utf-8'))
        gravar[f] = json.dumps({k: fecha(nova, abre(velha, v)) for k, v in pacote.items()}, separators=(',', ':'))

    # 2) index.html: conteúdo com a chave nova, chave nova embrulhada pela senha nova
    sal, wi, iv = os.urandom(16), os.urandom(12), os.urandom(12)
    P['s'], P['wi'], P['iv'] = b64e(sal), b64e(wi), b64e(iv)
    P['w'] = b64e(AESGCM(deriva(senha_nova, sal, P['it'])).encrypt(wi, nova, None))
    P['c'] = b64e(AESGCM(nova).encrypt(iv, conteudo, None))
    gravar[arq] = html[:m.start(2)] + json.dumps(P, separators=(',', ':')) + html[m.end(2):]

    for f, texto in gravar.items():
        open(f, 'w', encoding='utf-8').write(texto)
    print('%s: chave nova, %d arquivos recriptografados.' % (os.path.relpath(pasta, RAIZ) or '.', len(gravar)))


if __name__ == '__main__':
    atual = norm(os.environ.get('MANUAL_SENHA') or getpass.getpass('Senha atual: '))
    nova = norm(os.environ.get('MANUAL_SENHA_NOVA') or getpass.getpass('Senha nova (frase longa, mínimo %d caracteres): ' % MINIMO))
    if len(nova) < MINIMO:
        sys.exit('Senha nova curta (mínimo %d caracteres). Nada foi alterado.' % MINIMO)
    if not os.environ.get('MANUAL_SENHA_NOVA') and nova != norm(getpass.getpass('Repita a senha nova: ')):
        sys.exit('As senhas não conferem. Nada foi alterado.')
    for pasta in (RAIZ, os.path.join(RAIZ, 'manual-generico')):
        if os.path.exists(os.path.join(pasta, 'index.html')):
            rotacionar(pasta, atual, nova)
    print('Pronto. Rode tools/verificar.py e publique. Avise a equipe da senha nova por canal seguro.')
