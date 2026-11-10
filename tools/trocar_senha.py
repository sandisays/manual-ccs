#!/usr/bin/env python3
"""Troca a senha de entrada do Manual Digital CCS sem recriptografar os arquivos.

Uso:  python3 tools/trocar_senha.py        (pede a senha atual e a nova)
Precisa de: pip install cryptography
O conteúdo é cifrado com uma chave fixa; a senha só protege essa chave.
Trocar a senha gera um novo sal, então todos precisam entrar de novo.
"""
import base64, getpass, hashlib, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ARQ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")
html = open(ARQ, encoding="utf-8").read()
m = re.search(r'(<script id="encdata"[^>]*>)(.*?)(</script>)', html, re.S)
P = json.loads(m.group(2))
if "w" not in P:
    sys.exit("Este index.html ainda usa o formato antigo (sem chave embrulhada).")
b = base64.b64decode
norm = lambda s: s.strip().upper().encode()
deriva = lambda pw, sal: hashlib.pbkdf2_hmac("sha256", pw, sal, P["it"], 32)
try:
    chave = AESGCM(deriva(norm(getpass.getpass("Senha atual: ")), b(P["s"]))).decrypt(b(P["wi"]), b(P["w"]), None)
except Exception:
    sys.exit("Senha atual incorreta. Nada foi alterado.")
nova = norm(getpass.getpass("Senha nova: "))
if len(nova) < 8 or nova != norm(getpass.getpass("Repita a senha nova: ")):
    sys.exit("Senha nova curta (mínimo 8) ou diferente na repetição. Nada foi alterado.")
sal, iv = os.urandom(16), os.urandom(12)
P["s"] = base64.b64encode(sal).decode()
P["wi"] = base64.b64encode(iv).decode()
P["w"] = base64.b64encode(AESGCM(deriva(nova, sal)).encrypt(iv, chave, None)).decode()
html = html[: m.start(2)] + json.dumps(P, separators=(",", ":")) + html[m.end(2):]
open(ARQ, "w", encoding="utf-8").write(html)
print("Senha trocada. Publique o index.html novo (a página e o GitHub).")
