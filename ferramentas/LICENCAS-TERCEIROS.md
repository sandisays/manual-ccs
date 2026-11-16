# Bibliotecas de terceiros

O `index.html` embute as bibliotecas abaixo, nas versões fixadas em `package.json` e `package-lock.json`. Os textos completos das licenças ficam em `node_modules/<pacote>/` depois de `npm ci`.

| Biblioteca | Versão | Licença | Para que serve |
| --- | --- | --- | --- |
| pdf.js (`pdfjs-dist`) | 4.10.38 | Apache-2.0 | Ler e desenhar PDFs |
| pdf-lib | 1.17.1 | MIT | Criar e alterar PDFs |
| JSZip | 3.10.2 | MIT ou GPL-3.0 (usada sob MIT) | Montar arquivos .docx e .zip |
| docx-preview | 0.3.7 | Apache-2.0 | Prévia do Word na tela Comparar |
| Tesseract.js | 7.0.0 | Apache-2.0 | OCR (reconhecimento de texto) |
| tesseract.js-core | 6.1.2 | Apache-2.0 | Motor do OCR em WebAssembly |
| Dados de idioma português (`@tesseract.js-data/por`) | 1.0.0 | MIT | Modelo de português do OCR |
| Fonte Fredoka (`@fontsource/fredoka`) | 5.3.0 | OFL-1.1 | Fonte dos títulos |
| jsQR | 1.4.0 | Apache-2.0 | Ler QR Codes |
| qrcode-generator | 2.0.4 | MIT | Gerar QR Codes |
| qpdf (via @neslinesli93/qpdf-wasm) | 0.3.1 | qpdf: Apache-2.0; empacotamento: ISC | Proteger e remover senha |
| Lista de palavras derivada do wordfreq (`src/dict.b64`, gerada por `src/dicionario.py`) | 3.1.1 | dados CC BY-SA 4.0 (Robyn Speer e colaboradores) | Dicionário do Dado fictício |

## Observação de segurança

`npm audit` sem vulnerabilidades conhecidas em 14/11/2026. O pdf.js 4.10.38 já corrige a CVE-2024-4367; as duas proteções extras continuam ativas: `isEvalSupported: false` em todas as chamadas e política de segurança (CSP) que não permite `eval`.

O pdf.js 4 é distribuído só como módulo (`.mjs`). O `build.py` converte o arquivo e o worker em scripts comuns para que a página continue funcionando aberta direto do disco, sem servidor.
