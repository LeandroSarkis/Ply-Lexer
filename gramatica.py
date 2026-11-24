"""Gramática livre de contexto + cálculo de FIRST e FOLLOW (implementação própria)."""
import re
from comum import EPSILON, FIM

_PADRAO_TERMINAL = re.compile(r'^[A-Z][A-Z0-9_]*$')


def formatar_producao(cabeca, corpo):
    return f"{cabeca} → {' '.join(corpo) if corpo else EPSILON}"


class Gramatica:
    def __init__(self, producoes, inicial):
        """producoes: lista de (cabeça, tupla_corpo); corpo vazio = ε."""
        self.producoes = [(c, tuple(b)) for c, b in producoes]
        self.inicial = inicial
        self.nao_terminais = []
        for cab, _ in self.producoes:
            if cab not in self.nao_terminais:
                self.nao_terminais.append(cab)
        if inicial not in self.nao_terminais:
            raise ValueError(f"Símbolo inicial '{inicial}' não possui produções")
        self.terminais = []
        for cab, corpo in self.producoes:
            for s in corpo:
                if s in self.nao_terminais or s in self.terminais:
                    continue
                if not _PADRAO_TERMINAL.match(s):
                    raise ValueError(
                        f"Símbolo '{s}' na produção '{formatar_producao(cab, corpo)}' "
                        f"não é terminal (MAIÚSCULAS) nem tem produções definidas")
                self.terminais.append(s)
        self.first = self._calcular_first()
        self.follow = self._calcular_follow()

    @classmethod
    def de_texto(cls, texto):
        """Formato: `A -> X Y | Z`, linhas iniciadas por `|` continuam a regra anterior,
        `ε` é a cadeia vazia e `#` inicia comentário."""
        producoes, cabeca, inicial = [], None, None
        for numero, linha in enumerate(texto.splitlines(), 1):
            linha = linha.split('#', 1)[0].strip()
            if not linha:
                continue
            if linha.startswith('|'):
                if cabeca is None:
                    raise ValueError(f"Linha {numero}: '|' sem regra anterior")
                alternativas = linha[1:]
            elif '->' in linha:
                cabeca, alternativas = [x.strip() for x in linha.split('->', 1)]
                if inicial is None:
                    inicial = cabeca
            else:
                raise ValueError(f"Linha {numero}: formato inválido: {linha!r}")
            for alt in alternativas.split('|'):
                simbolos = alt.split()
                if not simbolos:
                    raise ValueError(f"Linha {numero}: alternativa vazia (use ε)")
                if EPSILON in simbolos and simbolos != [EPSILON]:
                    raise ValueError(f"Linha {numero}: ε misturado com outros símbolos")
                producoes.append((cabeca, () if simbolos == [EPSILON] else tuple(simbolos)))
        return cls(producoes, inicial)

    @classmethod
    def de_arquivo(cls, caminho):
        with open(caminho, encoding='utf-8') as f:
            return cls.de_texto(f.read())

    def first_sequencia(self, seq, first=None):
        first = self.first if first is None else first
        resultado = set()
        for s in seq:
            if s in self.nao_terminais:
                fs = first[s]
                resultado |= fs - {EPSILON}
                if EPSILON not in fs:
                    return resultado
            else:
                resultado.add(s)
                return resultado
        resultado.add(EPSILON)
        return resultado

    def _calcular_first(self):
        first = {a: set() for a in self.nao_terminais}
        mudou = True
        while mudou:
            mudou = False
            for cab, corpo in self.producoes:
                novo = self.first_sequencia(corpo, first)
                if not novo <= first[cab]:
                    first[cab] |= novo
                    mudou = True
        return first

    def _calcular_follow(self):
        follow = {a: set() for a in self.nao_terminais}
        follow[self.inicial].add(FIM)
        mudou = True
        while mudou:
            mudou = False
            for cab, corpo in self.producoes:
                for i, s in enumerate(corpo):
                    if s not in self.nao_terminais:
                        continue
                    f = self.first_sequencia(corpo[i + 1:])
                    novo = f - {EPSILON}
                    if EPSILON in f:
                        novo |= follow[cab]
                    if not novo <= follow[s]:
                        follow[s] |= novo
                        mudou = True
        return follow
