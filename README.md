# Analisador léxico + sintático LL(1) e SLR(1)

Subconjunto de uma linguagem tipo C: `#include`/`#define`, `typedef struct`, funções,
`int main()`, declaração de variáveis (`int`, `float`, `double`, vetores/matrizes com inicializador),
atribuição, `if`/`else`/`else if`, `while`, `for`, `return`, chamadas, expressões
aritméticas, relacionais, lógicas (`&&`, `||`) e ternário.

## Estrutura

| Arquivo | Papel |
|---|---|
| `lexico.py` | Scanner (PLY — apenas `ply.lex`): lexemas, classes, expressões regulares |
| `fluxo_tokens.py` | Liga o scanner ao parser: refina `OPERADOR`/`DELIMITADOR`, reconhece `main`, `struct`, `typedef`, adiciona `$` |
| `gramaticas/ll1.txt` | GLC já transformada (sem ambiguidade, com precedência, sem recursão à esquerda, fatorada) |
| `gramaticas/slr1.txt` | GLC para o SLR(1) (recursão à esquerda mantida) |
| `gramatica.py` | Leitor de gramáticas + cálculo de **FIRST** e **FOLLOW** |
| `analisador_ll1.py` | **Tabela LL(1)** + casamento com **pilha de análise** |
| `analisador_slr1.py` | **Itens LR(0)**, **tabela SLR(1)** (ACTION/GOTO) e algoritmo shift/reduce |
| `main.py` | Executa tudo |
| `test_analisadores.py` | Testes (programas válidos/inválidos, conflitos, precedência) |
| `TRANSFORMACAO_GRAMATICA.md` | Passo a passo (a)→(d) exigido no enunciado |
| `sintatico.py` | Versão do 1º bimestre com `ply.yacc` — **não** faz parte deste trabalho |

Os algoritmos sintáticos são implementados do zero (nenhum `yacc`/gerador de parser).

## Como executar

```bash
pip install ply
python main.py                          # exemplo do lexico.py, LL(1) e SLR(1)
python main.py meu_programa.c           # analisa um arquivo
python main.py -a ll1 --passos          # pilha / entrada / ação passo a passo
python main.py --tokens                 # cadeia de tokens (classe, terminal, lexema)
python main.py --first-follow --tabela  # FIRST/FOLLOW e tabelas
python main.py -a slr1 --itens          # coleção canônica de itens LR(0)
python main.py --arvore                 # árvore de derivação
python main.py --exportar saida         # tabelas em CSV (abre no Excel)
python -m unittest -v                   # testes
```
Código de saída: `0` aceito, `1` erro léxico/sintático, `2` gramática com conflitos.

## Roteiro sugerido para a apresentação (15 min)

1. **Léxico**: `python main.py --tokens` → lexemas, classes, expressões regulares do `lexico.py`, cadeia de tokens.
2. **Gramática**: `TRANSFORMACAO_GRAMATICA.md` (ambiguidade → precedência → recursão à esquerda → fatoração).
3. **LL(1)**: `--first-follow --tabela`, depois `-a ll1 --passos` com um trecho pequeno.
4. **SLR(1)**: `-a slr1 --itens`, tabela ACTION/GOTO e `--passos`.
5. **Erros**: rodar com um programa inválido (mensagem com linha e tokens esperados).
6. Código de exemplo sem conflitos + `python -m unittest -v`.

## Limitações conhecidas

- Parada no primeiro erro (sem recuperação de erro).
- O lexer não reconhece `!`, `%`, `++`, `char`, `void`; para suportá-los, inclua no `lexico.py`,
  em `fluxo_tokens.py` e nas duas gramáticas.
- Existência de uma única `main` é verificada após a análise (aviso semântico), não pela gramática.
