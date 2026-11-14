# Manual Digital CCS

Manual de certificação (SIGSIF, DCPOA, modelos de CSI, unidades e normas).

- `index.html`: o manual, com o conteúdo criptografado (AES-GCM). Abre só com a senha.
- `enc/`: prints, PDFs, a página de Newcastle e os tachamentos, também criptografados.
- `tools/trocar_senha.py`: troca a senha de entrada sem recriptografar os arquivos (pede a senha atual e a nova).

- `tools/blindar.py`: aplica as proteções de publicação ao `index.html` (fonte embutida, política de segurança e cabeçalho dentro da parte criptografada). Rode sempre que o `index.html` for gerado de novo.
- `tools/verificar.py`: confere se está tudo pronto para publicar. Com `--senha`, também abre todos os arquivos.
- `tools/rotacionar_chave.py`: gera chave nova e recriptografa tudo. Use quando alguém que conhecia a senha sair da equipe.

Nenhum arquivo deste repositório tem conteúdo do manual em texto aberto. Para abrir, baixe a pasta inteira e abra o `index.html` num servidor web (ou publique no Cloudflare Pages / GitHub Pages).

## Antes de publicar

```
python3 tools/blindar.py      # pede a senha; não altera nada se já estiver protegido
python3 tools/verificar.py    # precisa terminar com "OK: pode publicar."
```

Regras que a verificação garante:

- A página não carrega nada de fora (sem Google Fonts, sem CDN) e funciona sem internet depois de aberta.
- Quem não tem a senha vê só o título e a tela de senha: logo, nome da empresa e descrição ficam criptografados.
- Todos os arquivos de `enc/` estão criptografados.

## Senha e chave

- A senha precisa ter pelo menos 12 caracteres; prefira uma frase de 4 ou 5 palavras.
- `trocar_senha.py` troca só a senha. Se alguém saiu da equipe ou houve suspeita de vazamento, use `rotacionar_chave.py`.
- A senha nunca é escrita em arquivo deste repositório.

## Antes de cada publicação

Rode `python3 tools/blindar.py` e depois `python3 tools/verificar.py --senha`. Só publique se o verificar terminar com "OK: pode publicar.".
