"""Testes: python -m unittest -v   (requer `pip install ply` por causa do lexico.py)"""
import os
import unittest

from comum import ErroSintatico, contar_simbolo
from gramatica import Gramatica
from analisador_ll1 import AnalisadorLL1
from analisador_slr1 import AnalisadorSLR1
from fluxo_tokens import tokenizar, TERMINAIS
from lexico import codigo_fonte

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gramaticas')
G_LL1 = Gramatica.de_arquivo(os.path.join(PASTA, 'll1.txt'))
G_SLR = Gramatica.de_arquivo(os.path.join(PASTA, 'slr1.txt'))
LL1 = AnalisadorLL1(G_LL1)
SLR = AnalisadorSLR1(G_SLR)


def aceita(analisador, codigo):
    try:
        analisador.analisar(tokenizar(codigo))
        return True
    except ErroSintatico:
        return False


VALIDOS = {
    'main vazio': 'int main() { }',
    'declaracoes': 'int main() { int a, b = 2; float c = 1.5; double d[3] = {1, 2, 3}; }',
    'matematica': 'int main() { int x = 1 + 2 * 3 - 4 / 2; x = (x + 1) * -x; }',
    'logica': 'int main() { int r = 1 < 2 && 3 >= 2 || 4 != 5 && 1 == 1; }',
    'if': 'int main() { int a = 1; if (a > 0) { a = 2; } }',
    'if else': 'int main() { int a = 1; if (a > 0) { a = 2; } else { a = 3; } }',
    'else if': 'int main() { int a = 1; if (a > 0) { a = 2; } else if (a < 0) { a = 3; } else { a = 4; } }',
    'while': 'int main() { int i = 0; while (i < 10) { i = i + 1; } }',
    'for': 'int main() { int s = 0; for (int i = 0; i < 5; i = i + 1) { s = s + i; } }',
    'for sem decl': 'int main() { int i; for (i = 0; i < 5; i = i + 1) { } }',
    'funcao e chamada': 'int f(int a, float b) { return a; } int main() { int x = f(1, 2.0); f(3, 4.5); }',
    'matriz': 'int main() { int m[2][2]; m[1][0] = m[0][1] + 1; }',
    'ternario': 'int main() { int a = 1 ? 2 : 3 ? 4 : 5; }',
    'diretivas': '#include <stdio.h>\n#define PI 3.14\n#define F(a, b) a + b\nint main() { }',
    'struct': 'typedef struct { int id; double v; } Item; int main() { }',
    'bloco aninhado': 'int main() { { int a; } }',
    'comentarios': 'int main() { /* c */ int a; // l\n }',
    'exemplo do lexico.py': codigo_fonte,
}

INVALIDOS = {
    'sem ponto e virgula': 'int main() { int a }',
    'chave nao fechada': 'int main() { int a;',
    'if sem bloco': 'int main() { if (1) a = 2; }',
    'else sem if': 'int main() { else { } }',
    'parenteses': 'int main() { int a = (1 + 2; }',
    'operador solto': 'int main() { int a = 1 + ; }',
    'main com parametro': 'int main(int a) { }',
    'comando fora de funcao': 'int a = 1;',
    'tipo ausente': 'main() { }',
    'virgula extra': 'int f(int a,) { } int main() { }',
    'for incompleto': 'int main() { for (int i = 0; i < 2) { } }',
    'vazio': '',
}


class TestGramaticas(unittest.TestCase):
    def test_ll1_sem_conflitos(self):
        self.assertEqual(LL1.conflitos, [])

    def test_slr1_sem_conflitos(self):
        self.assertEqual(SLR.conflitos, [])

    def test_terminais_existem_no_lexer(self):
        self.assertFalse(set(G_LL1.terminais) - TERMINAIS)
        self.assertFalse(set(G_SLR.terminais) - TERMINAIS)

    def test_gramatica_slr_nao_e_ll1_por_recursao_esquerda(self):
        self.assertTrue(AnalisadorLL1(G_SLR).conflitos)


class TestFirstFollow(unittest.TestCase):
    def test_gramatica_classica_de_expressoes(self):
        g = Gramatica.de_texto("""
            E -> T E'
            E' -> PLUS T E' | ε
            T -> F T'
            T' -> STAR F T' | ε
            F -> LP E RP | ID
        """)
        self.assertEqual(g.first['E'], {'LP', 'ID'})
        self.assertEqual(g.first["E'"], {'PLUS', 'ε'})
        self.assertEqual(g.first["T'"], {'STAR', 'ε'})
        self.assertEqual(g.follow['E'], {'$', 'RP'})
        self.assertEqual(g.follow["E'"], {'$', 'RP'})
        self.assertEqual(g.follow['T'], {'PLUS', '$', 'RP'})
        self.assertEqual(g.follow['F'], {'STAR', 'PLUS', '$', 'RP'})

    def test_deteccao_de_conflito_ll1(self):
        g = Gramatica.de_texto("S -> A B\nA -> X | X Y\nB -> Z")   # sem fatoração
        self.assertTrue(AnalisadorLL1(g).conflitos)

    def test_deteccao_de_conflito_slr1(self):
        # Gramática clássica LALR/LR(1) mas não SLR(1)
        g = Gramatica.de_texto("S -> L EQ R | R\nL -> STAR R | ID\nR -> L")
        self.assertTrue(AnalisadorSLR1(g).conflitos)

    def test_simbolo_indefinido_e_erro(self):
        with self.assertRaises(ValueError):
            Gramatica.de_texto("S -> a B")


class TestAnalise(unittest.TestCase):
    def test_validos(self):
        for nome, codigo in VALIDOS.items():
            with self.subTest(nome=nome, parser='LL1'):
                self.assertTrue(aceita(LL1, codigo))
            with self.subTest(nome=nome, parser='SLR1'):
                self.assertTrue(aceita(SLR, codigo))

    def test_invalidos(self):
        for nome, codigo in INVALIDOS.items():
            with self.subTest(nome=nome, parser='LL1'):
                self.assertFalse(aceita(LL1, codigo))
            with self.subTest(nome=nome, parser='SLR1'):
                self.assertFalse(aceita(SLR, codigo))

    def test_erro_informa_linha(self):
        with self.assertRaises(ErroSintatico) as ctx:
            LL1.analisar(tokenizar('int main() {\n int a\n}'))
        self.assertIn('linha 3', str(ctx.exception))
        with self.assertRaises(ErroSintatico) as ctx:
            SLR.analisar(tokenizar('int main() {\n int a\n}'))
        self.assertIn('linha 3', str(ctx.exception))

    def test_main_na_arvore(self):
        for a in (LL1, SLR):
            self.assertEqual(contar_simbolo(a.analisar(tokenizar(codigo_fonte)), 'MAIN'), 1)

    def test_precedencia_e_associatividade(self):
        """1 - 2 - 3 deve agrupar à esquerda e * deve ligar mais forte que +."""
        def folhas(no):
            if no.lexema is not None:
                return [no.lexema]
            return [x for f in no.filhos for x in folhas(f)]

        def avaliar_slr(no):   # avalia a árvore SLR (recursiva à esquerda)
            if no.lexema is not None:
                return int(no.lexema) if no.lexema.isdigit() else no.lexema
            if len(no.filhos) == 1:
                return avaliar_slr(no.filhos[0])
            if len(no.filhos) == 3 and no.filhos[0].lexema == '(':
                return avaliar_slr(no.filhos[1])
            a, op, b = no.filhos
            a, b = avaliar_slr(a), avaliar_slr(b)
            return {'+': a + b, '-': a - b, '*': a * b}[op.lexema]

        for codigo, esperado in (('1 - 2 - 3', -4), ('1 + 2 * 3', 7), ('2 * 3 + 4', 10)):
            arv = SLR.analisar(tokenizar(f'#define X(a) {codigo}\nint main() {{ }}'))
            define = arv.filhos[0].filhos[0].filhos[0].filhos[0]
            expr = define.filhos[-1]
            self.assertEqual(avaliar_slr(expr), esperado, codigo)


if __name__ == '__main__':
    unittest.main()
