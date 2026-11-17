# Casos de avaliação da skill `narrar`

Cada pasta é um caso: `prompt.md` (o estado e o pedido do jogador, com dados genéricos) e `graders/*.md` (o que a resposta precisa cumprir, julgado por um modelo).

| Caso | O que confere |
|---|---|
| `narrar-cena-com-escolha` | formato da mensagem, nenhuma rolagem sem decisão, português do Brasil |
| `narrar-falha-devolve-decisao` | depois de uma falha, rerrolagem e vitória com custo são opções do jogador |
| `narrar-montagem-para-na-falha-bestial` | a montagem para e devolve a escolha |
| `narrar-regra-improvisada` | regra fora do livro não é inventada; se for usada, vira "Decisão do narrador" |

Rodar (gasta créditos: cada caso roda 3 vezes, com e sem o plugin):

```bash
claude plugin eval .                       # todos os casos
claude plugin eval . --case "narrar-falha*" --runs 1
```

Os casos não usam pasta de campanha nem o motor de dados: o estado e os resultados de rolagem vêm no próprio pedido. A checagem mecânica do mesmo contrato (palavras, opções, seletor, português de Portugal) é feita sem modelo por `python scripts/estilo.py mensagem <arquivo>` e pelos testes em `tests/test_estilo.py`.

Os resultados ficam em `evals/results/`, fora do repositório.
