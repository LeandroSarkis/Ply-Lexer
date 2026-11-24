"""Integração com o analisador léxico (lexico.py, baseado em ply.lex).

Converte os tokens do scanner em terminais da gramática, refinando as
classes genéricas OPERADOR / DELIMITADOR / PALAVRA_RESERVADA / IDENTIFICADOR
(sem alterar o lexico.py) e acrescentando o marcador de fim de entrada '$'.
"""
import lexico
from comum import Token, FIM

MAPA_OPERADORES = {
    '+': 'OP_SOMA', '-': 'OP_SUBTRACAO',
    '*': 'OP_MULTIPLICACAO', '/': 'OP_DIVISAO',
    '==': 'OP_IGUAL', '!=': 'OP_DIFERENTE',
    '<=': 'OP_MENOR_IGUAL', '>=': 'OP_MAIOR_IGUAL',
    '<': 'OP_MENOR', '>': 'OP_MAIOR',
    '&&': 'OP_E_LOGICO', '||': 'OP_OU_LOGICO',
    '=': 'OP_ATRIBUICAO', '?': 'OP_TERNARIO',
}

MAPA_DELIMITADORES = {
    '(': 'ABRE_PARENTESES', ')': 'FECHA_PARENTESES',
    '{': 'ABRE_CHAVES', '}': 'FECHA_CHAVES',
    '[': 'ABRE_COLCHETES', ']': 'FECHA_COLCHETES',
    ';': 'PONTO_VIRGULA', ',': 'VIRGULA', ':': 'DOIS_PONTOS',
}

MAPA_PALAVRAS = {'struct': 'STRUCT', 'typedef': 'TYPEDEF'}

# Todos os terminais que este adaptador pode produzir (usado nos testes).
TERMINAIS = (
    {'TIPO_VARIAVEL', 'RETORNO_FUNCAO', 'IDENTIFICADOR', 'MAIN', 'STRUCT',
     'TYPEDEF', 'CONSTANTE_INTEIRA', 'CONSTANTE_FLUTUANTE', 'PRE_PROCESSADOR',
     'BIBLIOTECA', 'STRING', 'P_WHILE', 'P_FOR', 'C_ELSE', 'C_IF'}
    | set(MAPA_OPERADORES.values()) | set(MAPA_DELIMITADORES.values())
)


def refinar(tipo, valor):
    if tipo == 'OPERADOR':
        return MAPA_OPERADORES[valor]
    if tipo == 'DELIMITADOR':
        return MAPA_DELIMITADORES[valor]
    if tipo == 'PALAVRA_RESERVADA':
        return MAPA_PALAVRAS[valor]
    if tipo == 'IDENTIFICADOR' and valor == 'main':
        return 'MAIN'
    return tipo


def tokenizar(codigo):
    """Retorna a lista de Token (terminal, lexema, linha, classe) terminada em '$'.
    Levanta SyntaxError em caso de erro léxico (comportamento do lexico.py)."""
    scanner = lexico.analisador
    scanner.lineno = 1
    scanner.input(codigo)
    tokens = []
    for tok in scanner:
        tokens.append(Token(refinar(tok.type, tok.value), str(tok.value),
                            tok.lineno, tok.type))
    tokens.append(Token(FIM, FIM, scanner.lineno, FIM))
    return tokens
