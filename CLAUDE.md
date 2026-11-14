# Manual Digital CCS: regras para quem edita este repositório

## Antes de cada envio (commit/push no GitHub ou publicação do artifact)

Rode sempre, nesta ordem, a partir da raiz do repositório:

```
python3 tools/blindar.py
python3 tools/verificar.py --senha
```

- `blindar.py` reaplica as proteções de publicação (fonte embutida, política de segurança, cabeçalho dentro da parte criptografada). Pode rodar várias vezes: só altera o que falta.
- `verificar.py` confere se está tudo pronto. Só envie se a última linha for **"OK: pode publicar."**. Se aparecer qualquer problema, corrija e rode os dois de novo.
- Os dois pedem a senha do manual (ou leem a variável de ambiente `MANUAL_SENHA`). Nunca grave a senha em arquivo, commit ou mensagem.
- Sem a senha (por exemplo, numa tarefa agendada que só troca a linha `const PGA={...};`), rode ao menos `python3 tools/verificar.py` sem `--senha` e não envie se ele apontar problema.

## Outras regras

- Nenhum conteúdo do manual em texto aberto no repositório; prints e anexos novos vão criptografados em `enc/`.
- Nenhuma menção a IA no texto do manual.
- Commits sem a linha `Claude-Session`.
