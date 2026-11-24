"""Estruturas comuns aos analisadores LL(1) e SLR(1)."""
from collections import namedtuple

EPSILON = 'ε'
FIM = '$'

# tipo   = terminal usado pela gramática (ex.: OP_SOMA)
# classe = classe de lexema original do analisador léxico (ex.: OPERADOR)
Token = namedtuple('Token', 'tipo lexema linha classe')


class ErroSintatico(Exception):
    pass


class No:
    """Nó da árvore de derivação (terminais têm lexema; não-terminais têm filhos)."""
    __slots__ = ('simbolo', 'lexema', 'filhos')

    def __init__(self, simbolo, lexema=None, filhos=None):
        self.simbolo = simbolo
        self.lexema = lexema
        self.filhos = filhos if filhos is not None else []


def _rotulo(no):
    if no.lexema is not None:
        return f"{no.simbolo}  '{no.lexema}'"
    if not no.filhos:
        return f"{no.simbolo} → {EPSILON}"
    return no.simbolo


def arvore_para_linhas(raiz):
    """Árvore no estilo do comando `tree` (iterativo, sem limite de recursão)."""
    linhas = []
    pilha = [(raiz, '', True, True)]
    while pilha:
        no, prefixo, ultimo, eh_raiz = pilha.pop()
        conector = '' if eh_raiz else ('└── ' if ultimo else '├── ')
        linhas.append(prefixo + conector + _rotulo(no))
        novo = prefixo + ('' if eh_raiz else ('    ' if ultimo else '│   '))
        n = len(no.filhos)
        for k in range(n - 1, -1, -1):
            pilha.append((no.filhos[k], novo, k == n - 1, False))
    return linhas


def contar_simbolo(raiz, simbolo):
    total, pilha = 0, [raiz]
    while pilha:
        no = pilha.pop()
        if no.simbolo == simbolo:
            total += 1
        pilha.extend(no.filhos)
    return total


def formatar_passos(passos, titulos=('Passo', 'Pilha', 'Entrada', 'Ação')):
    """Imprime a tabela de execução do parser (lista de tuplas de 4 strings)."""
    larguras = [6, 58, 40, 0]
    print(f"{titulos[0]:<{larguras[0]}} {titulos[1]:<{larguras[1]}} "
          f"{titulos[2]:<{larguras[2]}} {titulos[3]}")
    print('-' * 130)
    for n, pilha, entrada, acao in passos:
        print(f"{n:<{larguras[0]}} {pilha:<{larguras[1]}} {entrada:<{larguras[2]}} {acao}")
