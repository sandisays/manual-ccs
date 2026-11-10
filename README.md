# Manual Digital CCS

Manual de certificação (SIGSIF, DCPOA, modelos de CSI, unidades e normas).

- `index.html`: o manual, com o conteúdo criptografado (AES-GCM). Abre só com a senha.
- `enc/`: prints, PDFs, a página de Newcastle e os tachamentos, também criptografados.
- `tools/trocar_senha.py`: troca a senha de entrada sem recriptografar os arquivos (pede a senha atual e a nova).

Nenhum arquivo deste repositório tem conteúdo do manual em texto aberto. Para abrir, baixe a pasta inteira e abra o `index.html` num servidor web (ou publique no Cloudflare Pages / GitHub Pages).
