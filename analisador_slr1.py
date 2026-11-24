"""Analisador sintático ascendente SLR(1) — implementação própria.

Etapas: gramática aumentada -> FIRST/FOLLOW -> coleção canônica de itens LR(0)
-> tabela ACTION/GOTO (usando FOLLOW para as reduções) -> algoritmo shift/reduce.
"""
import csv
from comum import FIM, No, ErroSintatico
from gramatica import Gramatica, formatar_producao


def _txt(acao):
    return 'acc' if acao[0] == 'acc' else f"{acao[0]}{acao[1]}"


class AnalisadorSLR1:
    def __init__(self, gramatica):
        self.g = gramatica
        inicial_aum = gramatica.inicial + "'"
        self.ga = Gramatica([(inicial_aum, (gramatica.inicial,))] + list(gramatica.producoes),
                            inicial_aum)
        self.prods = self.ga.producoes          # prods[0] = S' -> S
        self.por_cabeca = {}
        for i, (c, _) in enumerate(self.prods):
            self.por_cabeca.setdefault(c, []).append(i)
        self.estados = []        # cada estado = tupla ordenada de itens-núcleo (prod, ponto)
        self.transicoes = {}     # (estado, símbolo) -> estado
        self.acao = {}           # (estado, terminal) -> ('s', j) | ('r', p) | ('acc',)
        self.desvio = {}         # (estado, não-terminal) -> estado
        self.conflitos = []      # (estado, terminal, ação1, ação2, tipo)
        self._construir_colecao()
        self._construir_tabela()

    # ---------- itens LR(0) ----------
    def fecho(self, itens):
        resultado, vistos, i = list(itens), set(itens), 0
        while i < len(resultado):
            p, d = resultado[i]
            i += 1
            corpo = self.prods[p][1]
            if d < len(corpo) and corpo[d] in self.ga.nao_terminais:
                for q in self.por_cabeca[corpo[d]]:
                    if (q, 0) not in vistos:
                        vistos.add((q, 0))
                        resultado.append((q, 0))
        return resultado

    def _construir_colecao(self):
        inicio = ((0, 0),)
        self.estados = [inicio]
        indice = {inicio: 0}
        i = 0
        while i < len(self.estados):
            destinos = {}
            for p, d in self.fecho(self.estados[i]):
                corpo = self.prods[p][1]
                if d < len(corpo):
                    destinos.setdefault(corpo[d], []).append((p, d + 1))
            for simbolo, itens in destinos.items():
                nucleo = tuple(sorted(itens))
                if nucleo not in indice:
                    indice[nucleo] = len(self.estados)
                    self.estados.append(nucleo)
                self.transicoes[(i, simbolo)] = indice[nucleo]
            i += 1

    def formatar_item(self, item):
        p, d = item
        cab, corpo = self.prods[p]
        simbolos = list(corpo)
        simbolos.insert(d, '•')
        return f"{cab} → {' '.join(simbolos)}"

    def linhas_itens(self):
        linhas = []
        for i, nucleo in enumerate(self.estados):
            linhas.append(f"I{i}:")
            for item in self.fecho(nucleo):
                marca = ' ' if item in nucleo else '+'   # '+' = item adicionado pelo fecho
                linhas.append(f"  {marca} {self.formatar_item(item)}")
        return linhas

    # ---------- tabela SLR(1) ----------
    def _adicionar(self, estado, terminal, nova):
        atual = self.acao.get((estado, terminal))
        if atual is None:
            self.acao[(estado, terminal)] = nova
        elif atual != nova:
            tipo = 'reduce/reduce' if atual[0] == 'r' and nova[0] == 'r' else 'shift/reduce'
            self.conflitos.append((estado, terminal, atual, nova, tipo))

    def _construir_tabela(self):
        ga = self.ga
        for i, nucleo in enumerate(self.estados):
            for p, d in self.fecho(nucleo):
                cab, corpo = self.prods[p]
                if d < len(corpo):
                    x = corpo[d]
                    if x in ga.terminais:
                        self._adicionar(i, x, ('s', self.transicoes[(i, x)]))
                elif p == 0:
                    self._adicionar(i, FIM, ('acc',))
                else:
                    for a in sorted(ga.follow[cab]):
                        self._adicionar(i, a, ('r', p))
        for (i, x), j in self.transicoes.items():
            if x in ga.nao_terminais:
                self.desvio[(i, x)] = j

    @property
    def eh_slr1(self):
        return not self.conflitos

    def descrever_conflito(self, c):
        estado, terminal, a1, a2, tipo = c
        return (f"estado {estado}, símbolo {terminal}: {_txt(a1)} vs {_txt(a2)} ({tipo}) — "
                + '; '.join(self.formatar_item(it) for it in self.fecho(self.estados[estado])
                            if it[1] == len(self.prods[it[0]][1]) or
                            self.prods[it[0]][1][it[1]] == terminal))

    def linhas_tabela(self):
        linhas = []
        for i in range(len(self.estados)):
            acoes = [f"{t}→{_txt(a)}" for (e, t), a in sorted(self.acao.items()) if e == i]
            desvios = [f"{x}→{j}" for (e, x), j in sorted(self.desvio.items()) if e == i]
            linhas.append(f"estado {i}")
            if acoes:
                linhas.append("   ACTION: " + ', '.join(acoes))
            if desvios:
                linhas.append("   GOTO:   " + ', '.join(desvios))
        return linhas

    def exportar_csv(self, caminho):
        terminais = sorted(self.ga.terminais) + [FIM]
        nts = [a for a in self.g.nao_terminais]
        with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['estado'] + terminais + nts)
            for i in range(len(self.estados)):
                linha = [i]
                for t in terminais:
                    a = self.acao.get((i, t))
                    linha.append('' if a is None else _txt(a))
                for x in nts:
                    j = self.desvio.get((i, x))
                    linha.append('' if j is None else j)
                w.writerow(linha)

    # ---------- análise ----------
    def analisar(self, tokens, passos=None):
        """Algoritmo shift/reduce. Retorna a raiz da árvore de derivação."""
        pilha = [(0, None)]   # (estado, nó)
        i, n = 0, 0

        def registrar(acao):
            if passos is not None:
                partes = []
                for est, no in pilha:
                    if no is not None:
                        partes.append(no.simbolo)
                    partes.append(str(est))
                texto = ' '.join(partes)
                if len(texto) > 56:
                    texto = '…' + texto[-55:]
                prox = ' '.join(t.tipo for t in tokens[i:i + 4]) + (' …' if i + 4 < len(tokens) else '')
                passos.append((n, texto, prox, acao))

        while True:
            n += 1
            estado = pilha[-1][0]
            tok = tokens[i]
            acao = self.acao.get((estado, tok.tipo))
            if acao is None:
                registrar('ERRO')
                esperados = sorted(t for (e, t) in self.acao if e == estado)
                lista = ', '.join(esperados)
                if tok.tipo == FIM:
                    raise ErroSintatico(f"Erro sintático: fim inesperado do arquivo (esperado: {lista})")
                raise ErroSintatico(
                    f"Erro sintático: token inesperado '{tok.lexema}' (classe {tok.tipo}) "
                    f"na linha {tok.linha} (esperado: {lista})")
            if acao[0] == 's':
                registrar(f"empilhar (shift) → estado {acao[1]}")
                pilha.append((acao[1], No(tok.tipo, tok.lexema)))
                i += 1
            elif acao[0] == 'r':
                cab, corpo = self.prods[acao[1]]
                registrar(f"reduzir {formatar_producao(cab, corpo)}")
                k = len(corpo)
                filhos = [no for _, no in pilha[len(pilha) - k:]] if k else []
                if k:
                    del pilha[len(pilha) - k:]
                destino = self.desvio[(pilha[-1][0], cab)]
                pilha.append((destino, No(cab, filhos=filhos)))
            else:
                registrar('ACEITAR')
                return pilha[-1][1]
