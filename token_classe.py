class Token:
    def __init__(self, token, classe, tipo, linha, coluna):
        self.token = token
        self.classe = classe
        self.tipo = tipo
        self.linha = linha
        self.coluna = coluna

    def representa(self):
        return f"{self.classe},\t{self.tipo},\t{self.token},\t{self.linha}, {self.coluna}"