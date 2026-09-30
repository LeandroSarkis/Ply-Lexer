import sys

import ply.yacc as yacc
from lexico import analisador as lexer_base, codigo_fonte

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


class EnvoltorioLexico:
    """Envolve o lexer de lexico.py e refina a classe de tokens
    OPERADOR/DELIMITADOR em subtipos usados pela gramática, sem
    modificar o analisador léxico original."""

    def __init__(self, lexer):
        self.lexer = lexer

    def input(self, dado):
        self.lexer.input(dado)

    def token(self):
        tok = self.lexer.token()
        if tok is None:
            return None
        if tok.type == 'OPERADOR':
            tok.type = MAPA_OPERADORES[tok.value]
        elif tok.type == 'DELIMITADOR':
            tok.type = MAPA_DELIMITADORES[tok.value]
        return tok

tokens = (
    'TIPO_VARIAVEL', 'RETORNO_FUNCAO', 'PALAVRA_RESERVADA', 'IDENTIFICADOR',
    'CONSTANTE_INTEIRA', 'CONSTANTE_FLUTUANTE', 'PRE_PROCESSADOR',
    'BIBLIOTECA', 'STRING', 'P_WHILE', 'P_FOR', 'C_ELSE', 'C_IF',
) + tuple(MAPA_OPERADORES.values()) + tuple(MAPA_DELIMITADORES.values())

def p_programa(p):
    'programa : lista_declaracoes'
    p[0] = ('programa', p[1])


def p_lista_declaracoes_multi(p):
    'lista_declaracoes : lista_declaracoes declaracao_global'
    p[0] = p[1] + [p[2]]


def p_lista_declaracoes_um(p):
    'lista_declaracoes : declaracao_global'
    p[0] = [p[1]]


def p_declaracao_global(p):
    '''declaracao_global : diretiva_preprocessador
                          | definicao_struct
                          | definicao_funcao'''
    p[0] = p[1]


def p_diretiva_include(p):
    'diretiva_preprocessador : PRE_PROCESSADOR BIBLIOTECA'
    p[0] = ('include', p[2])


def p_diretiva_define_macro(p):
    ('diretiva_preprocessador : PRE_PROCESSADOR IDENTIFICADOR ABRE_PARENTESES '
     'lista_ids FECHA_PARENTESES expressao')
    p[0] = ('define_macro', p[2], p[4], p[6])


def p_diretiva_define_constante(p):
    'diretiva_preprocessador : PRE_PROCESSADOR IDENTIFICADOR valor_define'
    p[0] = ('define_constante', p[2], p[3])


def p_valor_define(p):
    '''valor_define : CONSTANTE_INTEIRA
                     | CONSTANTE_FLUTUANTE
                     | STRING'''
    p[0] = p[1]


def p_lista_ids_multi(p):
    'lista_ids : lista_ids VIRGULA IDENTIFICADOR'
    p[0] = p[1] + [p[3]]


def p_lista_ids_um(p):
    'lista_ids : IDENTIFICADOR'
    p[0] = [p[1]]


def p_lista_ids_vazia(p):
    'lista_ids : vazio'
    p[0] = []


# --- struct/typedef ---

def p_definicao_struct(p):
    ('definicao_struct : PALAVRA_RESERVADA PALAVRA_RESERVADA ABRE_CHAVES '
     'lista_campos FECHA_CHAVES IDENTIFICADOR PONTO_VIRGULA')
    p[0] = ('struct', p[6], p[4])


def p_lista_campos_multi(p):
    'lista_campos : lista_campos campo'
    p[0] = p[1] + [p[2]]


def p_lista_campos_um(p):
    'lista_campos : campo'
    p[0] = [p[1]]


def p_campo(p):
    'campo : TIPO_VARIAVEL IDENTIFICADOR PONTO_VIRGULA'
    p[0] = ('campo', p[1], p[2])


def p_definicao_funcao(p):
    ('definicao_funcao : TIPO_VARIAVEL IDENTIFICADOR ABRE_PARENTESES '
     'lista_parametros FECHA_PARENTESES bloco')
    p[0] = ('funcao', p[1], p[2], p[4], p[6])


def p_lista_parametros_multi(p):
    'lista_parametros : lista_parametros VIRGULA parametro'
    p[0] = p[1] + [p[3]]


def p_lista_parametros_um(p):
    'lista_parametros : parametro'
    p[0] = [p[1]]


def p_lista_parametros_vazia(p):
    'lista_parametros : vazio'
    p[0] = []


def p_parametro(p):
    'parametro : TIPO_VARIAVEL IDENTIFICADOR dimensoes'
    p[0] = ('parametro', p[1], p[2], p[3])


def p_dimensoes_multi_com_tamanho(p):
    'dimensoes : dimensoes ABRE_COLCHETES CONSTANTE_INTEIRA FECHA_COLCHETES'
    p[0] = p[1] + [p[3]]


def p_dimensoes_multi_sem_tamanho(p):
    'dimensoes : dimensoes ABRE_COLCHETES FECHA_COLCHETES'
    p[0] = p[1] + [None]


def p_dimensoes_vazia(p):
    'dimensoes : vazio'
    p[0] = []


def p_bloco(p):
    'bloco : ABRE_CHAVES lista_comandos FECHA_CHAVES'
    p[0] = ('bloco', p[2])


def p_lista_comandos_multi(p):
    'lista_comandos : lista_comandos comando'
    p[0] = p[1] + [p[2]]


def p_lista_comandos_vazia(p):
    'lista_comandos : vazio'
    p[0] = []


def p_comando_declaracao(p):
    'comando : declaracao_variavel PONTO_VIRGULA'
    p[0] = p[1]


def p_comando_atribuicao(p):
    'comando : atribuicao PONTO_VIRGULA'
    p[0] = p[1]


def p_comando_return(p):
    'comando : RETORNO_FUNCAO expressao PONTO_VIRGULA'
    p[0] = ('return', p[2])


def p_comando_chamada(p):
    'comando : chamada_funcao PONTO_VIRGULA'
    p[0] = p[1]


def p_comando_outros(p):
    '''comando : comando_if
                | comando_while
                | comando_for
                | bloco'''
    p[0] = p[1]


def p_declaracao_variavel(p):
    'declaracao_variavel : TIPO_VARIAVEL lista_declaradores'
    p[0] = ('declaracao', p[1], p[2])


def p_lista_declaradores_multi(p):
    'lista_declaradores : lista_declaradores VIRGULA declarador'
    p[0] = p[1] + [p[3]]


def p_lista_declaradores_um(p):
    'lista_declaradores : declarador'
    p[0] = [p[1]]


def p_declarador_sem_valor(p):
    'declarador : IDENTIFICADOR dimensoes'
    p[0] = ('declarador', p[1], p[2], None)


def p_declarador_com_valor(p):
    'declarador : IDENTIFICADOR dimensoes OP_ATRIBUICAO valor_inicial'
    p[0] = ('declarador', p[1], p[2], p[4])


def p_valor_inicial_expressao(p):
    'valor_inicial : expressao'
    p[0] = p[1]


def p_valor_inicial_array(p):
    'valor_inicial : ABRE_CHAVES lista_valores FECHA_CHAVES'
    p[0] = ('inicializador_array', p[2])


def p_lista_valores_multi(p):
    'lista_valores : lista_valores VIRGULA valor_inicial'
    p[0] = p[1] + [p[3]]


def p_lista_valores_um(p):
    'lista_valores : valor_inicial'
    p[0] = [p[1]]


def p_atribuicao(p):
    'atribuicao : IDENTIFICADOR indices OP_ATRIBUICAO expressao'
    p[0] = ('atribuicao', p[1], p[2], p[4])


def p_indices_multi(p):
    'indices : indices ABRE_COLCHETES expressao FECHA_COLCHETES'
    p[0] = p[1] + [p[3]]


def p_indices_vazia(p):
    'indices : vazio'
    p[0] = []


def p_comando_if(p):
    'comando_if : C_IF ABRE_PARENTESES expressao FECHA_PARENTESES bloco'
    p[0] = ('if', p[3], p[5], None)


def p_comando_if_else(p):
    ('comando_if : C_IF ABRE_PARENTESES expressao FECHA_PARENTESES bloco '
     'C_ELSE bloco')
    p[0] = ('if', p[3], p[5], p[7])


def p_comando_while(p):
    'comando_while : P_WHILE ABRE_PARENTESES expressao FECHA_PARENTESES bloco'
    p[0] = ('while', p[3], p[5])


def p_comando_for(p):
    ('comando_for : P_FOR ABRE_PARENTESES for_init PONTO_VIRGULA expressao '
     'PONTO_VIRGULA atribuicao FECHA_PARENTESES bloco')
    p[0] = ('for', p[3], p[5], p[7], p[9])


def p_for_init(p):
    '''for_init : declaracao_variavel
                | atribuicao'''
    p[0] = p[1]


def p_chamada_funcao(p):
    'chamada_funcao : IDENTIFICADOR ABRE_PARENTESES lista_argumentos FECHA_PARENTESES'
    p[0] = ('chamada', p[1], p[3])


def p_lista_argumentos_multi(p):
    'lista_argumentos : lista_argumentos VIRGULA argumento'
    p[0] = p[1] + [p[3]]


def p_lista_argumentos_um(p):
    'lista_argumentos : argumento'
    p[0] = [p[1]]


def p_lista_argumentos_vazia(p):
    'lista_argumentos : vazio'
    p[0] = []


def p_argumento(p):
    'argumento : expressao'
    p[0] = p[1]


def p_expressao_ternaria(p):
    ('expressao : expressao_ou OP_TERNARIO expressao DOIS_PONTOS '
     'expressao')
    p[0] = ('ternario', p[1], p[3], p[5])


def p_expressao_simples(p):
    'expressao : expressao_ou'
    p[0] = p[1]


def p_expressao_ou(p):
    'expressao_ou : expressao_ou OP_OU_LOGICO expressao_e'
    p[0] = ('binop', '||', p[1], p[3])


def p_expressao_ou_simples(p):
    'expressao_ou : expressao_e'
    p[0] = p[1]


def p_expressao_e(p):
    'expressao_e : expressao_e OP_E_LOGICO expressao_rel'
    p[0] = ('binop', '&&', p[1], p[3])


def p_expressao_e_simples(p):
    'expressao_e : expressao_rel'
    p[0] = p[1]


def p_expressao_rel(p):
    '''expressao_rel : expressao_rel OP_IGUAL expressao_add
                      | expressao_rel OP_DIFERENTE expressao_add
                      | expressao_rel OP_MENOR expressao_add
                      | expressao_rel OP_MAIOR expressao_add
                      | expressao_rel OP_MENOR_IGUAL expressao_add
                      | expressao_rel OP_MAIOR_IGUAL expressao_add'''
    p[0] = ('binop', p[2], p[1], p[3])


def p_expressao_rel_simples(p):
    'expressao_rel : expressao_add'
    p[0] = p[1]


def p_expressao_add(p):
    '''expressao_add : expressao_add OP_SOMA termo
                      | expressao_add OP_SUBTRACAO termo'''
    p[0] = ('binop', p[2], p[1], p[3])


def p_expressao_add_simples(p):
    'expressao_add : termo'
    p[0] = p[1]


def p_termo(p):
    '''termo : termo OP_MULTIPLICACAO fator
             | termo OP_DIVISAO fator'''
    p[0] = ('binop', p[2], p[1], p[3])


def p_termo_simples(p):
    'termo : fator'
    p[0] = p[1]


def p_fator_parenteses(p):
    'fator : ABRE_PARENTESES expressao FECHA_PARENTESES'
    p[0] = p[2]


def p_fator_inteiro(p):
    'fator : CONSTANTE_INTEIRA'
    p[0] = ('const_int', p[1])


def p_fator_flutuante(p):
    'fator : CONSTANTE_FLUTUANTE'
    p[0] = ('const_float', p[1])


def p_fator_string(p):
    'fator : STRING'
    p[0] = ('const_string', p[1])


def p_fator_chamada(p):
    'fator : chamada_funcao'
    p[0] = p[1]


def p_fator_variavel(p):
    'fator : IDENTIFICADOR indices'
    p[0] = ('variavel', p[1], p[2])


def p_fator_menos_unario(p):
    'fator : OP_SUBTRACAO fator'
    p[0] = ('unario', '-', p[2])


def p_fator_mais_unario(p):
    'fator : OP_SOMA fator'
    p[0] = ('unario', '+', p[2])


def p_vazio(p):
    'vazio :'
    pass


def p_error(p):
    if p is None:
        raise SyntaxError("Erro sintático: fim inesperado do arquivo")
    raise SyntaxError(
        f"Erro sintático: token inesperado '{p.value}' "
        f"(classe {p.type}) na linha {p.lineno}"
    )


parser = yacc.yacc()

_COR_ATIVA = sys.stdout.isatty()
_ROTULO = '\033[1;36m' if _COR_ATIVA else ''
_VALOR = '\033[0;32m' if _COR_ATIVA else ''
_RESET = '\033[0m' if _COR_ATIVA else ''


def _filhos_do_no(no):
    """Achata listas dentro da tupla (ex.: lista de comandos de um bloco)
    para que virem galhos irmãos, em vez de um galho extra 'lista'."""
    filhos = []
    for item in no[1:]:
        if item is None:
            continue
        if isinstance(item, list):
            filhos.extend(f for f in item if f is not None)
        else:
            filhos.append(item)
    return filhos


def imprimir_ast(no, prefixo='', eh_ultimo=True, raiz=True):
    """Imprime a AST no estilo do comando `tree`, com galhos ├── / └──."""
    conector = '' if raiz else ('└── ' if eh_ultimo else '├── ')

    if isinstance(no, list):
        for i, item in enumerate(no):
            imprimir_ast(item, prefixo, i == len(no) - 1, raiz)
        return

    if isinstance(no, tuple) and no and isinstance(no[0], str):
        rotulo, filhos = no[0], _filhos_do_no(no)
        print(f"{prefixo}{conector}{_ROTULO}{rotulo}{_RESET}")
        novo_prefixo = prefixo + ('' if raiz else ('    ' if eh_ultimo else '│   '))
        for i, filho in enumerate(filhos):
            imprimir_ast(filho, novo_prefixo, i == len(filhos) - 1, False)
    else:
        print(f"{prefixo}{conector}{_VALOR}{no!r}{_RESET}")


if __name__ == '__main__':
    envoltorio = EnvoltorioLexico(lexer_base)
    try:
        arvore = parser.parse(codigo_fonte, lexer=envoltorio)
    except SyntaxError as erro:
        print(f"\n✗ Análise sintática interrompida: {erro}", file=sys.stderr)
        sys.exit(1)

    print("--- ANÁLISE SINTÁTICA CONCLUÍDA COM SUCESSO ---\n")
    print("--- ÁRVORE SINTÁTICA (AST) ---")
    imprimir_ast(arvore)