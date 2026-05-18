from token import Token    

TIPOS = {"INT", "FLOAT", "STRING", "CHAR", "BOOLEANO"}

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.analise = []

    def adicionaAnalise(self, tipo="Nao especificado"):
        self.analise.append([tipo, self.tokens[0].linha, self.tokens[0].coluna])

    def imprimeErro(self, tipo="NAO ESPECIFICADO"):
        self.adicionaAnalise(f"Erro: {tipo}")
        print("⚠️  Erro Sintático!⚠️   ", tipo, " 📍 ↔️ ", self.tokens[0].linha, ",↕️ ", self.tokens[0].coluna)
        return
    
    def matchClasse(self, classe):
        return self.tokens[0].classe == classe
    
    def matchTipo(self, tipo):
        return self.tokens[0].tipo == tipo
    
    def matchGrupo(self, grupo):
        return self.tokens[0].tipo in grupo

    def pop(self):
        self.tokens.pop(0)



    def bloco(self):
        if self.matchTipo("ABRE_CHAVE"):
            self.adicionaAnalise("Bloco")
            self.pop()

            if not self.bloco_(): return False

            if self.matchTipo("FECHA_CHAVE"):
                self.pop()
                return True
            
            self.imprimeErro("BLOCO DE CHAVE NÃO FECHADO")
            return False
            
        else:
            return True
        
    def bloco_(self):
        if self.matchGrupo(TIPOS):
            if not self.declaracao(): return False
        
        self.bloco_()

        return True



    def declaracao(self):
        if not self.matchGrupo(TIPOS): return False
        self.adicionaAnalise("Declaração de variável")
        self.pop()

        if not self.matchClasse("IDENTIFICADOR"):
            self.imprimeErro("DECLARACAO MAL FORMATADA")
            return False
        self.pop()

        if not self.declaracao_(): return False # atribuicao
        if not self.declaracao__(): return False # varias variaveis
        
        if not self.matchTipo("PONTO_VIRGULA"):
            self.imprimeErro("DECLARACAO MAL FORMATADA")
            return False
        self.pop()

        print("fim declaracao")
        return True
        
    def declaracao_(self):
        if self.matchTipo("ATRIBUICAO"):
            self.adicionaAnalise("Atribuição de variável")
            self.pop()

            return self.expressao()

        return True # vazio
        
    def declaracao__(self):
        if self.matchTipo("VIRGULA"):
            self.adicionaAnalise("Várias variáveis")
            self.pop()

            if not self.matchClasse("IDENTIFICADOR"):
                self.imprimeErro("DECLARACAO MAL FORMATADA")
                return False
            self.pop()

            if not self.declaracao_(): return False # atribuicao
            if not self.declaracao__(): return False # varias variaveis

        return True # vazio


    def expressao(self):
        if not self.expressao_(): return False
        self.adicionaAnalise("Expressão")
        self.pop()
        return True

    def expressao_(self):
        if self.matchClasse("LITERAL"): return True
        if self.matchClasse("BOOLEANO"): return True
        if self.matchClasse("IDENTIFICADOR"): return True
        
        self.imprimeErro("EXPRESSAO MAL FORMATADA")
        return False


    def programa(self):
        # inicio, bloco(s), fim
        if not self.matchTipo("INICIO"):
            self.imprimeErro("SEM TOKEN DE INICIO DE PROGRAMA")
            return False
        self.adicionaAnalise("Inicio do código")
        self.pop()
        
        if not self.bloco():
            return False

        if not self.matchTipo("FIM"):
            self.imprimeErro("SEM TOKEN DE FIM DE PROGRAMA")
            return False
        self.pop()
        
        return True

    def analiseSintatica(self):
        return self.programa()