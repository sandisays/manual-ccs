#!/usr/bin/env python3
"""Copia as Ferramentas PDF para dentro do manual (pasta ferramentas/).

Uso:  python3 tools/atualizar_ferramentas_pdf.py <pasta do repositório ferramentas-pdf>

O script confere o SHA-256 do index.html das Ferramentas PDF com o SHA256SUMS dela antes de
copiar. Se não bater, nada é copiado. A cópia vai para ferramentas/ e para
manual-generico/ferramentas/, junto com o arquivo VERSAO.txt (versão e SHA-256).
Depois rode tools/blindar.py, que põe o cartão "Ferramentas PDF" na aba Ferramentas,
e tools/verificar.py --senha.
"""
import hashlib, os, re, shutil, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
DESTINOS = [os.path.join(RAIZ, 'ferramentas'), os.path.join(RAIZ, 'manual-generico', 'ferramentas')]

if len(sys.argv) != 2:
    sys.exit(__doc__)
origem = os.path.abspath(sys.argv[1])
html = os.path.join(origem, 'index.html')
somas = os.path.join(origem, 'SHA256SUMS')
dados = open(html, 'rb').read()
sha = hashlib.sha256(dados).hexdigest()
esperado = open(somas, encoding='utf-8').read().split()[0]
if sha != esperado:
    sys.exit('O SHA-256 do index.html não confere com o SHA256SUMS. Nada foi copiado.')
versao = re.search(rb'vers\xc3\xa3o (\d+\.\d+\.\d+)', dados)
versao = versao.group(1).decode() if versao else 'desconhecida'
for d in DESTINOS:
    os.makedirs(d, exist_ok=True)
    shutil.copyfile(html, os.path.join(d, 'index.html'))
    for extra in ('LICENCAS-TERCEIROS.md',):
        if os.path.exists(os.path.join(origem, extra)):
            shutil.copyfile(os.path.join(origem, extra), os.path.join(d, extra))
    open(os.path.join(d, 'VERSAO.txt'), 'w', encoding='utf-8').write(
        'Ferramentas PDF %s\nSHA-256 %s\n' % (versao, sha))
print('Ferramentas PDF %s copiada (SHA-256 %s...). Agora rode tools/blindar.py.' % (versao, sha[:16]))
