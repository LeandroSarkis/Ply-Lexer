import ply.lex as lex

tokens = (
    'TIPO_VARIAVEL',
    'RETORNO_FUNCAO',
    'PALAVRA_RESERVADA',
    'IDENTIFICADOR',
    'CONSTANTE_INTEIRA',
    'CONSTANTE_FLUTUANTE',
    'OPERADOR',
    'DELIMITADOR',
    'PRE_PROCESSADOR',
    'BIBLIOTECA',
    'STRING',
    'P_WHILE',
    'P_FOR',
    'C_ELSE',
    'C_IF',
)

palavras_reservadas = {
    'int': 'TIPO_VARIAVEL',
    'float': 'TIPO_VARIAVEL',
    'double': 'TIPO_VARIAVEL',
    'return': 'RETORNO_FUNCAO',
    'if': 'C_IF',
    'else': 'C_ELSE',
    'for': 'P_FOR',
    'while': 'P_WHILE',
    'struct': 'PALAVRA_RESERVADA',
    'typedef': 'PALAVRA_RESERVADA'
}


def t_COMENTARIO_MULTILINHA(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass 

def t_COMENTARIO_LINHA(t):
    r'//.*'
    pass

def t_PRE_PROCESSADOR(t):
    r'\#(define|include)'
    return t

def t_BIBLIOTECA(t):
    r'<[a-zA-Z0-9_.]+\.h>'
    return t

def t_OPERADOR(t):
    r'==|!=|<=|>=|&&|\|\||\+|\-|\*|/|=|<|>|\?'
    return t

def t_DELIMITADOR(t):
    r'\(|\)|\{|\}|\[|\]|;|,|:'
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_CONSTANTE_FLUTUANTE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CONSTANTE_INTEIRA(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = palavras_reservadas.get(t.value, 'IDENTIFICADOR')
    return t

def t_quebra_linha(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f"Erro léxico: Caractere inválido '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

analisador = lex.lex()

if __name__ == '__main__':
    codigo_fonte = '''
    #include <stdio.h>
    #define MAX(a, b) ((a) > (b) ? (a) : (b))
    #define PI 3.14159

    /* Estrutura para testes de tipos
       e ponteiros no analisador */
    typedef struct {
        int id;
        double valor;
    } Elemento;

    int processar_dados(int matriz[2][2], float fator) {
        int resultado = 0;
        int i, j;
        
        for (i = 0; i < 2; i = i + 1) {
            for (j = 0; j < 2; j = j + 1) {
                if (matriz[i][j] != 0) {
                    resultado = resultado + (matriz[i][j] * fator);
                } else {
                    resultado = resultado - 1;
                }
            }
        }
        return resultado;
    }

    int main() {
        int dados[2][2] = {{10, 20}, {0, 40}};
        double limite = 99.95;
        
        // Chamada de Macro e Funcoes
        int maior = MAX(10, 50);
        int final = processar_dados(dados, 1.5);

        if (final == 0 || limite <= 100.0) {
            printf("Resultado do processamento: %d", final);
        }

        return 0;
    }
    '''

    analisador.input(codigo_fonte)
    print("--- TOKENS IDENTIFICADOS ---")
    for token in analisador:
        print(f"Linha {token.lineno:<3} | Classe: {token.type:<20} | Lexema: {token.value}")