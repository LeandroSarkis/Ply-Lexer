"""Executa o scanner + analisadores sintáticos LL(1) e SLR(1).

Exemplos:
    python main.py                      # usa o código de exemplo de lexico.py
    python main.py programa.c           # analisa um arquivo
    python main.py -a ll1 --passos      # só LL(1), mostrando a pilha passo a passo
    python main.py --tokens --first-follow --tabela --itens --arvore
    python main.py --exportar saida     # grava tabelas LL(1)/SLR(1) em CSV
"""
import argparse
import os
import sys

from comum import ErroSintatico, FIM, arvore_para_linhas, contar_simbolo, formatar_passos
from gramatica import Gramatica
from analisador_ll1 import AnalisadorLL1
from analisador_slr1 import AnalisadorSLR1
from fluxo_tokens import tokenizar

PASTA = os.path.dirname(os.path.abspath(__file__))


def titulo(texto):
    print(f"\n{'=' * 78}\n{texto}\n{'=' * 78}")


def mostrar_first_follow(g):
    for rotulo, conj in (('FIRST', g.first), ('FOLLOW', g.follow)):
        print(f"\n{rotulo}:")
        for nt in g.nao_terminais:
            print(f"  {rotulo}({nt}) = {{ {', '.join(sorted(conj[nt]))} }}")


def verificar_main(arvore):
    total = contar_simbolo(arvore, 'MAIN')
    if total == 1:
        print("  ✓ bloco principal 'main' encontrado")
    else:
        print(f"  ⚠ aviso semântico: esperado 1 função main, encontradas {total}")


def executar(nome, tokens, args):
    ll1 = nome == 'LL(1)'
    g = Gramatica.de_arquivo(os.path.join(PASTA, 'gramaticas', 'll1.txt' if ll1 else 'slr1.txt'))
    analisador = AnalisadorLL1(g) if ll1 else AnalisadorSLR1(g)
    titulo(f"ANALISADOR SINTÁTICO {nome}")
    print(f"Gramática: {len(g.producoes)} produções, {len(g.nao_terminais)} não-terminais, "
          f"{len(g.terminais)} terminais")

    if args.first_follow:
        mostrar_first_follow(g)

    if ll1:
        print(f"Tabela LL(1): {len(analisador.tabela)} células preenchidas")
        if analisador.conflitos:
            print(f"✗ A gramática NÃO é LL(1): {len(analisador.conflitos)} conflito(s)")
            for c in analisador.conflitos:
                print("  -", analisador.descrever_conflito(c))
            return 2
        print("✓ Sem conflitos: a gramática é LL(1)")
    else:
        print(f"Coleção canônica LR(0): {len(analisador.estados)} estados")
        if analisador.conflitos:
            print(f"✗ A gramática NÃO é SLR(1): {len(analisador.conflitos)} conflito(s)")
            for c in analisador.conflitos:
                print("  -", analisador.descrever_conflito(c))
            return 2
        print("✓ Sem conflitos: a gramática é SLR(1)")
        if args.itens:
            print("\nItens LR(0)  ('+' = item adicionado pelo fecho):")
            print('\n'.join(analisador.linhas_itens()))

    if args.tabela:
        print("\nTabela de análise:")
        print('\n'.join(analisador.linhas_tabela()))

    if args.exportar:
        os.makedirs(args.exportar, exist_ok=True)
        caminho = os.path.join(args.exportar, 'tabela_ll1.csv' if ll1 else 'tabela_slr1.csv')
        analisador.exportar_csv(caminho)
        print(f"Tabela exportada para {caminho}")

    passos = [] if args.passos else None
    try:
        arvore = analisador.analisar(tokens, passos)
    except ErroSintatico as erro:
        if passos:
            print()
            formatar_passos(passos)
        print(f"\n✗ {erro}")
        return 1

    if passos:
        print()
        formatar_passos(passos)
    print("\n✓ ANÁLISE SINTÁTICA CONCLUÍDA COM SUCESSO — entrada aceita")
    verificar_main(arvore)
    if args.arvore:
        print("\nÁrvore de derivação:")
        print('\n'.join(arvore_para_linhas(arvore)))
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arquivo', nargs='?', help='código-fonte a analisar (padrão: exemplo do lexico.py)')
    ap.add_argument('-a', '--analisador', choices=['ll1', 'slr1', 'ambos'], default='ambos')
    ap.add_argument('--tokens', action='store_true', help='mostra a cadeia de tokens')
    ap.add_argument('--first-follow', action='store_true', help='mostra FIRST e FOLLOW')
    ap.add_argument('--tabela', action='store_true', help='mostra a tabela de análise')
    ap.add_argument('--itens', action='store_true', help='mostra os itens LR(0) (SLR)')
    ap.add_argument('--passos', action='store_true', help='mostra pilha/entrada/ação passo a passo')
    ap.add_argument('--arvore', action='store_true', help='imprime a árvore de derivação')
    ap.add_argument('--exportar', metavar='PASTA', help='grava as tabelas em CSV')
    args = ap.parse_args()

    if args.arquivo:
        with open(args.arquivo, encoding='utf-8') as f:
            codigo = f.read()
    else:
        from lexico import codigo_fonte as codigo

    titulo("ANALISADOR LÉXICO")
    try:
        tokens = tokenizar(codigo)
    except SyntaxError as erro:
        print(f"✗ {erro}")
        return 1
    print(f"{len(tokens) - 1} tokens reconhecidos")
    if args.tokens:
        print(f"\n{'Linha':<6} {'Classe (léxico)':<20} {'Terminal (gramática)':<22} Lexema")
        for t in tokens[:-1]:
            print(f"{t.linha:<6} {t.classe:<20} {t.tipo:<22} {t.lexema}")
        print(f"\nCadeia de tokens: {' '.join(t.tipo for t in tokens)}")

    codigos = []
    if args.analisador in ('ll1', 'ambos'):
        codigos.append(executar('LL(1)', tokens, args))
    if args.analisador in ('slr1', 'ambos'):
        codigos.append(executar('SLR(1)', tokens, args))
    return max(codigos)


if __name__ == '__main__':
    sys.exit(main())
