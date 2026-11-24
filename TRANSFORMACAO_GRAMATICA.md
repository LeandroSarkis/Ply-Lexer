# Transformação da gramática até LL(1)

Ordem exigida no enunciado: **(a)** eliminar ambiguidade → **(b)** precedência e
associatividade → **(c)** eliminar recursão à esquerda → **(d)** fatorar.
As gramáticas finais estão em `gramaticas/ll1.txt` (LL(1)) e `gramaticas/slr1.txt` (SLR(1)).

## (a) Eliminação de ambiguidade

Forma ingênua (ambígua) das expressões:

```
E -> E + E | E - E | E * E | E / E | E == E | E < E | E && E | E || E
   | ( E ) | - E | CONST | ID
```
`1 + 2 * 3` tem duas árvores de derivação; `1 - 2 - 3` também.

Outras ambiguidades tratadas:

| Problema | Solução |
|---|---|
| *Dangling else* (`if (a) if (b) x; else y;`) | `if`/`else`/`while`/`for` exigem **bloco `{ }`**, então o `else` sempre pertence ao `if` do bloco imediatamente anterior |
| `if (...) bloco else if (...)` | `else_corpo -> bloco \| comando_if` (cadeia `else if` sem ambiguidade) |
| `lista_ids`, parâmetros e argumentos vazios | opcionalidade separada da lista (`parametros_opt -> lista_parametros \| ε`), evitando aceitar `( , a )` |

## (b) Precedência e associatividade

Um nível de não-terminal por precedência (do menor para o maior); recursão à esquerda
= associatividade à esquerda; o ternário é associativo à direita.

```
expressao  -> expr_ou ? expressao : expressao | expr_ou     (direita)
expr_ou    -> expr_ou || expr_e      | expr_e
expr_e     -> expr_e  && expr_igual  | expr_igual
expr_igual -> expr_igual (== | !=) expr_rel | expr_rel
expr_rel   -> expr_rel (< | > | <= | >=) expr_add | expr_add
expr_add   -> expr_add (+ | -) termo | termo
termo      -> termo (* | /) fator    | fator
fator      -> ( expressao ) | CONST | STRING | chamada | ID indices | - fator | + fator
```
Esta é exatamente a gramática de `slr1.txt` (recursão à esquerda é aceita por LR).

## (c) Eliminação de recursão à esquerda

Regra geral: `A -> A α | β` vira `A -> β A'` e `A' -> α A' | ε`. Exemplos:

```
expr_add  -> expr_add op_add termo | termo     ⇒   expr_add  -> termo expr_add'
                                                    expr_add' -> op_add termo expr_add' | ε
lista_comandos -> lista_comandos comando | ε   ⇒   lista_comandos -> comando lista_comandos | ε
lista_parametros -> lista_parametros , parametro | parametro
                                               ⇒   lista_parametros  -> parametro lista_parametros' | ε
                                                    lista_parametros' -> , parametro lista_parametros' | ε
dimensoes / indices / lista_declaradores / lista_valores / lista_argumentos / lista_campos / lista_ids / lista_globais: mesmo padrão
```
O mesmo procedimento vale para todos os níveis (`expr_ou`, `expr_e`, `expr_igual`, `expr_rel`, `termo`).

## (d) Fatoração à esquerda

Regra geral: `A -> α β1 | α β2` vira `A -> α A'` e `A' -> β1 | β2`.

| Antes (prefixo comum) | Depois |
|---|---|
| `comando -> atribuicao ; \| chamada ;` (ambos começam com `IDENTIFICADOR`) | `comando -> IDENTIFICADOR comando_id ;` e `comando_id -> atribuicao_resto \| ( lista_argumentos )` |
| `fator -> chamada \| IDENTIFICADOR indices` | `fator -> IDENTIFICADOR fator_id` e `fator_id -> ( lista_argumentos ) \| indices` |
| `declarador -> ID dims \| ID dims = valor` | `declarador -> ID dims declarador_init` e `declarador_init -> = valor_inicial \| ε` |
| `dim -> [ INT ] \| [ ]` | `dimensoes -> [ dimensao_resto dimensoes \| ε` e `dimensao_resto -> INT ] \| ]` |
| `if (...) bloco \| if (...) bloco else ...` | `comando_if -> if ( e ) bloco else_opcional` |
| `expr ? expr : expr \| expr` | `expressao -> expr_ou expressao_t` e `expressao_t -> ? expressao : expressao \| ε` |
| `#define` com/sem parâmetros e `#include` | `diretiva -> PRE_PROCESSADOR diretiva_resto` e `diretiva_resto -> BIBLIOTECA \| IDENTIFICADOR define_resto` |

## Verificação

O programa confirma automaticamente que `ll1.txt` não tem conflitos na tabela M[A, a] e que `slr1.txt`
não tem conflitos shift/reduce nem reduce/reduce (`python main.py`). Os testes também mostram que a
gramática do SLR **não** é LL(1) (recursão à esquerda) — por isso são duas gramáticas.
