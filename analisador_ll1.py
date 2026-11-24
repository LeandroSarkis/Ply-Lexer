"""Analisador sintático preditivo LL(1) — implementação própria.

Etapas (nesta ordem): FIRST/FOLLOW (gramatica.py) -> tabela LL(1) -> pilha de análise.
"""
import csv
from comum import EPSILON, FIM, No, ErroSintatico
from gramatica import formatar_producao


class AnalisadorLL1:
    def __init__(self, gramatica):
        self.g = gramatica
        self.tabela = {}      # (não-terminal, terminal) -> índice da produção
        self.conflitos = []   # (não-terminal, terminal, [índices])
        self._construir_tabela()

    # ---------- tabela ----------
    def _construir_tabela(self):
        g = self.g
        celulas = {}
        for idx, (cab, corpo) in enumerate(g.producoes):
            f = g.first_sequencia(corpo)
            alvo = f - {EPSILON}
            if EPSILON in f:
                alvo |= g.follow[cab]
            for a in alvo:
                celulas.setdefault((cab, a), []).append(idx)
        for chave in sorted(celulas):
            idxs = celulas[chave]
            self.tabela[chave] = idxs[0]
            if len(idxs) > 1:
                self.conflitos.append((chave[0], chave[1], idxs))

    @property
    def eh_ll1(self):
        return not self.conflitos

    def descrever_conflito(self, conflito):
        nt, t, idxs = conflito
        prods = ' | '.join(formatar_producao(*self.g.producoes[i]) for i in idxs)
        return f"M[{nt}, {t}] tem {len(idxs)} produções: {prods}"

    def linhas_tabela(self):
        """Uma linha por (não-terminal, produção), listando os terminais que a selecionam."""
        linhas = []
        for nt in self.g.nao_terminais:
            por_producao = {}
            for (a, t), idx in self.tabela.items():
                if a == nt:
                    por_producao.setdefault(idx, []).append(t)
            for idx in sorted(por_producao):
                terminais = ', '.join(sorted(por_producao[idx]))
                linhas.append(f"M[{nt}, {{{terminais}}}] = "
                              f"{formatar_producao(*self.g.producoes[idx])}")
        return linhas

    def exportar_csv(self, caminho):
        colunas = sorted(self.g.terminais) + [FIM]
        with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow([''] + colunas)
            for nt in self.g.nao_terminais:
                linha = [nt]
                for t in colunas:
                    idx = self.tabela.get((nt, t))
                    linha.append('' if idx is None else formatar_producao(*self.g.producoes[idx]))
                w.writerow(linha)

    # ---------- análise ----------
    def analisar(self, tokens, passos=None):
        """Casamento (MATCH) com pilha de análise. Retorna a raiz da árvore de derivação.
        Se `passos` for uma lista, nela são registrados (n, pilha, entrada, ação)."""
        g = self.g
        raiz = No(g.inicial)
        pilha = [(FIM, None), (g.inicial, raiz)]
        i, n = 0, 0

        def registrar(acao):
            if passos is not None:
                topo_primeiro = [s for s, _ in reversed(pilha)]
                texto_pilha = ' '.join(topo_primeiro[:9]) + (' …' if len(topo_primeiro) > 9 else '')
                prox = ' '.join(t.tipo for t in tokens[i:i + 5]) + (' …' if i + 5 < len(tokens) else '')
                passos.append((n, texto_pilha, prox, acao))

        while True:
            n += 1
            simbolo, no = pilha[-1]
            tok = tokens[i]
            if simbolo == FIM:
                if tok.tipo == FIM:
                    registrar('ACEITAR')
                    return raiz
                registrar('ERRO')
                raise ErroSintatico(self._msg_inesperado(tok, ['fim do arquivo']))
            if simbolo in g.terminais:
                if simbolo == tok.tipo:
                    registrar(f"casar {simbolo}")
                    pilha.pop()
                    no.lexema = tok.lexema
                    i += 1
                    continue
                registrar('ERRO')
                raise ErroSintatico(self._msg_inesperado(tok, [simbolo]))
            idx = self.tabela.get((simbolo, tok.tipo))
            if idx is None:
                registrar('ERRO')
                esperados = sorted(t for (a, t) in self.tabela if a == simbolo)
                raise ErroSintatico(self._msg_inesperado(tok, esperados))
            corpo = g.producoes[idx][1]
            registrar(formatar_producao(simbolo, corpo))
            pilha.pop()
            filhos = [No(s) for s in corpo]
            no.filhos = filhos
            for filho in reversed(filhos):
                pilha.append((filho.simbolo, filho))

    @staticmethod
    def _msg_inesperado(tok, esperados):
        lista = ', '.join(esperados)
        if tok.tipo == FIM:
            return f"Erro sintático: fim inesperado do arquivo (esperado: {lista})"
        return (f"Erro sintático: token inesperado '{tok.lexema}' (classe {tok.tipo}) "
                f"na linha {tok.linha} (esperado: {lista})")
