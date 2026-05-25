from dataclasses import dataclass
from typing import Optional

class No:
    pass

@dataclass
class Numero(No):
    valor: int

@dataclass
class String(No):
    valor: str

@dataclass
class Tipo(No):
    tipo: str

@dataclass
class Booleano(No):
    valor: bool

@dataclass
class Identificador(No):
    nome: str

@dataclass
class Declaracao(No):
    nome: Identificador
    tipo: Tipo

@dataclass
class OperacaoBin(No):
    operador: str
    esquerda: No
    direita: No

@dataclass
class OperacaoUn(No):
    operador: str
    operando: No

@dataclass
class Atribuicao(No):
    alvo: Identificador
    valor: No

@dataclass
class Bloco(No):
    statements: list

@dataclass
class Condicao(No):
    condicao: No
    then_branch: Bloco
    else_branch: Optional[Bloco]

@dataclass
class ForStatement(No):
    inicio: No
    condicao: No
    fim: No
    corpo: Bloco

@dataclass
class Loop(No):
    condicao: No
    bloco: Bloco

@dataclass
class DeclaracaoFuncao(No):
    nome: str
    params: list
    corpo: Bloco

@dataclass
class ChamadaFuncao(No):
    nome: str
    argumentos: list

@dataclass
class PalavraReservada(No):
    nome: str


def print_ast(no, level=0):
    indentacao = "    " * level

    print(f"{indentacao}{type(no).__name__}:")

    for value in vars(no).values():
        if isinstance(value, No):
            print_ast(value, level + 1)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, No):
                    print_ast(item, level + 1)

        else:
            print(f"{indentacao}└─ {value}")