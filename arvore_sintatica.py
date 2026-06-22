from dataclasses import dataclass
from typing import Optional

class No:
    pass

@dataclass
class Literal(No):
    valor: int
    tipo: str
    pos: Optional[[]]

@dataclass
class Tipo(No):
    tipo: str
    pos: Optional[[]]

@dataclass
class Identificador(No):
    nome: str
    pos: Optional[[]]

@dataclass
class Declaracao(No):
    nome: Identificador
    tipo: Tipo
    pos: Optional[[]]

@dataclass
class OperacaoBin(No):
    operador: str
    esquerda: No
    direita: No
    pos: Optional[[]]
    tipo: Optional[str]

@dataclass
class OperacaoUn(No):
    operador: str
    operando: No
    pos: Optional[[]]
    tipo: Optional[str]

@dataclass
class OperacaoTer(No):
    operador: str
    esquerda: No
    centro: No
    direita: No
    pos: Optional[[]]

@dataclass
class Bloco(No):
    statements: list
    pos: Optional[[]]

@dataclass
class Condicao(No):
    condicao: No
    then_branch: Bloco
    else_branch: Optional[Bloco]
    pos: Optional[[]]

@dataclass
class ForStatement(No):
    inicio: No
    condicao: No
    fim: No
    corpo: Bloco
    pos: Optional[[]]

@dataclass
class Loop(No):
    condicao: No
    bloco: Bloco
    pos: Optional[[]]

@dataclass
class DeclaracaoFuncao(No):
    nome: str
    params: list
    corpo: Bloco
    pos: Optional[[]]

@dataclass
class ChamadaFuncao(No):
    nome: str
    argumentos: list
    pos: Optional[[]]

@dataclass
class PalavraReservada(No):
    nome: str
    pos: Optional[[]]


def print_ast(no, level=0):
    indentacao = "      " * level

    print(f"{indentacao}└─ {type(no).__name__}:", end="")

    # Imprime a posição se existir e não for None
    if hasattr(no, 'pos') and getattr(no, 'pos') is not None:
        print(f" ── {getattr(no, 'pos')}")
    else:
        print("")

    for key, value in vars(no).items():
        if key == 'pos':
            continue

        if isinstance(value, No):
            print(f"{indentacao}   └─ {key}:")
            print_ast(value, level + 1)

        elif isinstance(value, list):
            print(f"{indentacao}   └─ {key}:")
            for item in value:
                if isinstance(item, No):
                    print_ast(item, level + 1)

        else:
            print(f"{indentacao}   └─ {key}: {value}")