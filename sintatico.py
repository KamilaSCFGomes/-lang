from token import Token    

TIPOS = {"INT", "FLOAT", "STRING", "CHAR", "BOOLEANO"}
FUNCOES = {"PRINT", "SCAN"}

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.analise = []
    
    def imprimeTipoAtual(self): # para debug
        print(self.tokens[0].tipo)

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

            return self.bloco_()
            
        return False
        
    def bloco_(self):
        if self.matchTipo("FECHA_CHAVE"):
            self.pop()
            return True
        
        if self.matchGrupo(TIPOS):
            if not self.declaracao(): return False
            return self.bloco_()
        
        if self.matchTipo("IF"):
            if not self.condicao(): return False
            return self.bloco_()
        
        if self.matchGrupo(FUNCOES):
            if not self.funcao(): return False
            return self.bloco_()

        self.imprimeErro("COMANDO NAO IDENTIFICADO")
        return False


    def valores(self):
        if self.matchClasse("LITERAL") or self.matchClasse("BOOLEANO") or self.matchClasse("IDENTIFICADOR"):
            self.pop()
            return True
        else:
            return False

    def parametros(self):
        if not self.valores():
            self.imprimeErro("PARAMETROS MAL FORMATADOS")
            return False
        return self.parametros_()
    
    def parametros_(self):
        if self.matchTipo("VIRGULA"):
            self.pop()
            return self.parametros()
        return True # vazio


    def funcao(self):
        if not self.matchGrupo(FUNCOES): return False
        self.adicionaAnalise("Função")
        self.pop()

        if not self.matchTipo("ABRE_PARENTESES"):
            self.imprimeErro("FUNCAO SEM PARAMETROS")
            return False
        self.pop()

        if not self.parametros():
            self.imprimeErro("PARAMETROS DE FUNCAO MAL FORMATADOS")
            return False
        
        if not self.matchTipo("FECHA_PARENTESES"):
            self.imprimeErro("PARAMETROS NAO FECHADOS")
            return False
        self.pop()

        if not self.matchTipo("PONTO_VIRGULA"):
            self.imprimeErro("DECLARACOA MAL FORMADA")
            return False
        self.pop()
        
        return True

    def condicao(self):
        if not self.matchTipo("IF"): return False
        self.adicionaAnalise("Condição")
        self.pop()

        return self.condicao_() and self.condicao_elif() and self.condicao_else()
    
    def condicao_(self):
        if not self.matchTipo("ABRE_PARENTESES"):
            self.imprimeErro("FALTA EXPRESSAO APOS CONDICAO")
            return False
        self.pop()

        if not self.expressao(): return False

        if not self.matchTipo("FECHA_PARENTESES"):
            self.imprimeErro("EXPRESSAO NAO FECHADA EM CONDICAO")
            return False
        self.pop()

        return self.bloco()
    
    def condicao_elif(self):
        if self.matchTipo("ELIF"):
            self.adicionaAnalise("Else if")
            self.pop()
            return self.condicao_() and self.condicao_elif()
        else:
            return True # vazio

    def condicao_else(self):
        if self.matchTipo("ELSE"):
            self.adicionaAnalise("Else")
            self.pop()
            return self.bloco()
        else:
            return True # vazio

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
        self.adicionaAnalise("Expressão")
        return self.expressao_1()
    
    def expressao_1(self):
        return self.expressao_2() and self.expressao_1_()
    
    def expressao_1_(self):
        if self.matchTipo("OR"):
            self.pop()
            return self.expressao_2() and self.expressao_1_()
        else: return True # vazio
    
    def expressao_2(self):
        return self.expressao_3() and self.expressao_2_()
    
    def expressao_2_(self):
        if self.matchTipo("AND"):
            self.pop()
            return self.expressao_3() and self.expressao_2_()
        else: return True # vazio
    
    def expressao_3(self):
        return self.expressao_4() and self.expressao_3_()
    
    def expressao_3_(self):
        if self.matchTipo("NAO"):
            self.pop()
            return self.expressao_4() and self.expressao_3_()
        else: return True # vazio
    
    def expressao_4(self):
        return self.expressao_5() and self.expressao_4_()
    
    def expressao_4_(self):
        if self.matchTipo("IGUAL") or self.matchTipo("MAIOR") or self.matchTipo("MENOR"):
            self.pop()
            return self.expressao_5() and self.expressao_4_()
        else: return True # vazio
    
    def expressao_5(self):
        return self.expressao_6() and self.expressao_5_()
    
    def expressao_5_(self):
        if self.matchTipo("MAIS") or self.matchTipo("MENOS"):
            self.pop()
            return self.expressao_6() and self.expressao_5_()
        else: return True # vazio
    
    def expressao_6(self):
        return self.expressao_7() and self.expressao_6_()
    
    def expressao_6_(self):
        if self.matchTipo("VEZES") or self.matchTipo("DIVIDIDO") or self.matchTipo("RESTO"):
            self.pop()
            return self.expressao_7() and self.expressao_6_()
        else: return True # vazio
    
    def expressao_7(self):
        return self.expressao_8() and self.expressao_7_()
    
    def expressao_7_(self):
        if self.matchTipo("POTENCIA"):
            self.pop()
            return self.expressao_8() and self.expressao_7_()
        else: return True # vazio
    
    def expressao_8(self):
        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
            if not self.expressao_1(): return False
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()
                return True
            return False
        return self.expressao_a()

    def expressao_a(self):
        if self.valores():
            return True
        self.imprimeErro("EXPRESSAO MAL FORMATADA")
        return False
    


    def programa(self):
        # inicio, bloco(s), fim
        if not self.matchTipo("INICIO"):
            self.imprimeErro("SEM TOKEN DE INICIO DE PROGRAMA")
            return False
        self.adicionaAnalise("Inicio do código")
        self.pop()
        
        if not self.bloco(): return False

        if not self.matchTipo("FIM"):
            self.imprimeErro("SEM TOKEN DE FIM DE PROGRAMA")
            return False
        self.pop()
        
        return True

    def analiseSintatica(self):
        return self.programa()