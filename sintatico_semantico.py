from token_classe import Token
import arvore_sintatica as ast
import tabela_simbolos as tab

FUNCOES = {"PRINT", "SCAN"}
ATRIBUICOES = {
    "MAIS_IGUAL": "MAIS",
    "MENOS_IGUAL": "MENOS",
    "VEZES_IGUAL": "VEZES",
    "DIVIDIDO_IGUAL": "DIVIDIDO",
    "POTENCIA_IGUAL": "POTENCIA"}

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.erros = []
        self.warnings = []
        self.arvore = ast.No
        self.tabela_simbolos = tab.TabelaSimbolos()

    def imprimeArvore(self, level=0):
        ast.print_ast(self.arvore, level)
    
    def imprimeTipoAtual(self): # para debug
        print(self.tokens[0].tipo)
    
    def tipoAtual(self):
        return self.tokens[0].tipo

    def valorAtual(self):
        return self.tokens[0].token

    def posAtual(self):
        return [self.tokens[0].linha, self.tokens[0].coluna]

    def noValorAtual(self):
        if self.matchTipo("NUMERAL"):
            return ast.Numero(self.valorAtual(), self.posAtual())
        if self.matchTipo("IDENTIFICADOR"):
            return ast.Identificador(self.valorAtual(), self.posAtual())
        if self.matchTipo("BOOLEANO"):
            return ast.Booleano(self.valorAtual(), self.posAtual())
        if self.matchTipo("TEXTO"):
            return ast.String(self.valorAtual(), self.posAtual())
        if self.matchGrupo(FUNCOES):
            return self.funcao()
        
        return False
    
    def imprimeErros(self):
        for erro in self.erros:
            print(f"⚠️  Erro!⚠️   {erro[0]} 📍 {erro[1]}")

    def imprimeWarnings(self):
        for w in self.warnings:
            print("⚠️  Warning!⚠️   ", w)


    def erro(self, categoria="", tipo="NAO ESPECIFICADO"):
        self.erros.append([f"Erro {categoria}: {tipo}", [self.tokens[0].linha, self.tokens[0].coluna]])
        print(f"⚠️  Erro {categoria}!⚠️   {tipo} 📍 {[self.tokens[0].linha, self.tokens[0].coluna]}")
        return
    
    def warning(self, tipo="NAO ESPECIFICADO"):
        self.warnings.append([f"Warning: {tipo}", [self.tokens[0].linha, self.tokens[0].coluna]])
        print(f"⚠️  Warning!⚠️   {tipo} 📍 {[self.tokens[0].linha, self.tokens[0].coluna]}")
        return

    def matchClasse(self, classe):
        return self.tokens[0].classe == classe
    
    def matchTipo(self, tipo):
        return self.tokens[0].tipo == tipo
    
    def matchGrupo(self, grupo):
        return self.tokens[0].tipo in grupo

    def pop(self):
        self.tokens.pop(0)

    def ehValor(self):
        return self.matchClasse("LITERAL") or self.matchClasse("BOOLEANO") or self.matchClasse("IDENTIFICADOR") or self.matchGrupo(FUNCOES)

    def panic_mode(self):
        linha_atual = self.tokens[0].linha
        
        while(len(self.tokens) > 0 and not self.matchTipo("FIM")):
            # token seguro:
            if self.matchTipo("FECHA_CHAVE") or self.matchTipo("PONTO_VIRGULA") or self.matchTipo("FECHA_PARENTESES") or self.matchTipo("ABRE_CHAVE"):
                return
            
            # inicio de outra linha:
            if self.tokens[0].linha != linha_atual:
                return
            
            self.pop()

    def panic_parenteses(self):
        linha_atual = self.tokens[0].linha
        
        while(len(self.tokens) > 0 and not self.matchTipo("FIM")):
            # token seguro:
            if self.matchTipo("FECHA_CHAVE") or self.matchTipo("ABRE_CHAVE") or self.matchTipo("FECHA_PARENTESES"):
                return
            
            # inicio de outra linha:
            if self.tokens[0].linha != linha_atual:
                return

            self.pop()
            


    def bloco(self):
        if self.matchTipo("ABRE_CHAVE"):
            self.tabela_simbolos.abrir_escopo()
            pos = self.posAtual()
            self.pop()

            arvore = ast.Bloco(self.bloco_(), pos)
            return arvore
            
        return False
        
    def bloco_(self):
        self.imprimeTipoAtual()

        if self.matchTipo("FECHA_CHAVE"):
            self.tabela_simbolos.fechar_escopo()
            self.pop()
            return []
        
        if self.matchTipo("ABRE_CHAVE"):

            return [self.bloco()] + self.bloco_()
        
        if self.matchGrupo(tab.TIPOS):
            novos = self.declaracao()
            if not novos: return self.bloco_()
            return novos + self.bloco_()
        
        if self.matchTipo("IF"):
            cond = self.condicao()
            if not cond: return self.bloco_()
            return [cond] + self.bloco_()

        if self.matchTipo("FOR"):
            loop = self.loop()
            if not loop: return self.bloco_()
            return [loop] + self.bloco_()

        if self.matchGrupo(FUNCOES):
            funcao = self.funcao()
            if not funcao: return self.bloco_()
            return [funcao] + self.bloco_()
        
        if self.matchGrupo("IDENTIFICADOR"):
            atri = self.atribuicao()
            if not atri: return self.bloco_()
            return [atri] + self.bloco_()

        if self.matchTipo("FIM"):
            self.erro("SINTATICO", "TOKEN DE FIM DE CODIGO INESPERADO")
            return []

        if self.matchTipo("ELSE") or self.matchTipo("ELIF"):
            self.erro("SINTATICO", "BLOCO ELSE FORA DE CONDICAO")

        self.erro("SINTATICO", "TOKEN DESCONHECIDO")
        self.panic_mode()

        if self.matchTipo("FECHA_PARENTESES"):
            self.erro("SINTATICO", "TOKEN INESPERADO. PARENTESES FECHADO SEM ABERTURA")
            self.pop()
            return self.bloco_()

        if self.matchTipo("ABRE_CHAVE"):
            return [self.bloco()] + self.bloco_()

        return []


    def parametros(self):
        if self.matchTipo("FECHA_PARENTESES"):
            return []
        
        valor = self.expressao()
        if not valor:
            self.erro("SINTATICO", "PARAMETROS MAL FORMATADOS")
            self.panic_parenteses()
            return []
        
        if self.matchTipo("VIRGULA"):
            self.pop()
            return [valor] + self.parametros()
        
        if self.matchTipo("ABRE_CHAVE") or self.matchTipo("FECHA_CHAVE"):
            self.erro("SINTATICO", "PARAMETROS MAL FORMATADOS")
        
        return [valor]



    def funcao(self):
        if not self.matchGrupo(FUNCOES): return False
        nome = self.valorAtual()
        pos = self.posAtual()
        self.pop()

        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
        else:
            self.erro("SINTATICO", "FUNCAO MAL FORMATADA. ESPERAVA (")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return ast.ChamadaFuncao(nome, [], pos)

        parametros = self.parametros()

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("SINTATICO", "FUNCAO MAL FORMATADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()

        return ast.ChamadaFuncao(nome, parametros, pos)
    

    def condicao(self):
        if not self.matchTipo("IF"): return False
        self.pop()
        
        return self.condicao_()

    def condicao_(self):
        pos = self.posAtual()

        if not self.matchTipo("ABRE_PARENTESES"):
            self.erro("SINTATICO", "CONDICAO MAL FORMADA. ESPERAVA (")
            return []
        self.pop()

        condicao = self.condicao_cond()

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()

        else:
            self.erro("SINTATICO", "CONDICAO MAL FORMADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()

        cond_then = False

        if self.matchTipo("ABRE_CHAVE"):
            cond_then = self.bloco()
            if not cond_then:
                self.erro("SINTATICO", "BLOCO THEN FALTANTE")
        else:
            self.erro("SINTATICO", "BLOCO THEN FALTANTE")
        
        if not condicao and not cond_then:
            return []

        cond_else = self.condicao_else()
        return ast.Condicao(condicao, cond_then, cond_else, pos)


    def condicao_cond(self):
        if self.matchTipo("FECHA_PARENTESES"):
            self.erro("SINTATICO", "CONDICAO VAZIA. ESPERAVA UMA EXPESSAO")
            return False

        condicao = self.expressao()
        if not condicao:
            self.erro("SINTATICO", "CONDICAO MAL FORMADA")
        return condicao
    
    def condicao_else(self):
        if self.matchTipo("ELIF"):
            self.pop()
            return ast.Bloco([self.condicao_()])
        
        if self.matchTipo("ELSE"):
            self.pop()

            if not self.matchTipo("ABRE_CHAVE"):
                self.erro("SINTATICO", "BLOCO ELSE FALTANTE")
                return []
            
            return self.bloco()
        
        else:
            self.erro("SINTATICO", "ESTRUTURA DE DECISAO MAL FORMATADA")
            return []

    def loop(self):
        if not self.matchTipo("FOR"):
            return False
        pos = self.posAtual()
        self.pop()
        
        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA (")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()
            return []

        if self.matchGrupo(tab.TIPOS) or self.matchTipo("DOIS_PONTOS"):
            resul = self.loop_for()
            if not resul: return []
            resul.pos = pos
            return resul

        elif self.ehValor():
            resul = self.loop_while()
            if not resul: return []
            resul.pos = pos
            return resul

        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM PARAMETROS MAL FORMULADOS")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()

        return []

    def loop_while(self):
        param = []
        if self.ehValor():
            param = self.expressao()
            if not param:
                self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM CONDICAO MAL FORMULADA")
                self.panic_parenteses()
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                return[]

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()
            if not self.matchTipo("ABRE_CHAVE"): return []

        if not self.matchTipo("ABRE_CHAVE"):
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CORPO")
            return []

        corpo = self.bloco()
        if not corpo:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CORTPO")

        return ast.Loop(param, corpo, None)

    def loop_for(self):
        param1 = self.loop_for_1()
        if self.matchTipo("DOIS_PONTOS"):
            self.pop()
        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA :")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return []
        
        param2 = self.loop_for_2()
        if not param2:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM CONDICAO DE PARADA MAL FORMULADA")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return []

        elif not self.matchTipo("DOIS_PONTOS"):
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA :")
            if not self.matchTipo("FECHA_PARENTESES"):
                self.panic_parenteses()

        self.pop()

        param3 = self.loop_for_3()
        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()

        if not self.matchTipo("ABRE_CHAVE"):
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CORPO")
            return []

        corpo = self.bloco()
        corpo = ast.Bloco(param1 + corpo.statements + param3, None)
        return ast.Loop(param2, corpo, None)

    def loop_for_1(self):
        if self.matchTipo("DOIS_PONTOS") or self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.matchGrupo(tab.TIPOS):
            decl = self.declaracao()
            if not decl: return [False]
            return decl + self.loop_for_1()
        
        elif self.matchTipo("PONTO_VIRGULA"):
            self.pop()
            return self.loop_for_1()
        
        self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
        return []
    
    def loop_for_2(self):
        if self.matchTipo("DOIS_PONTOS") or self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.ehValor():
            expr = self.expressao()
            if not expr: return False
            return [expr] + self.loop_for_2()
        
        self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
        return []

    def loop_for_3(self):
        if self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.ehValor():
            expr = self.atribuicao()
            if not expr: return False
            return [expr] + self.loop_for_3()
        
        elif self.matchGrupo(FUNCOES):
            fun = self.funcao()
            if not fun: return False
            return [fun] + self.loop_for_3()
        
        elif self.matchTipo("PONTO_VIRGULA"):
            self.pop()
            return self.loop_for_3()
        
        self.erro("SINTATICO", "ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
        return []


    def declaracao(self):
        if not self.matchGrupo(tab.TIPOS):
            return False
        tipo = self.tipoAtual()
        pos = self.posAtual()
        self.pop()

        if not self.matchTipo("IDENTIFICADOR"):
            self.erro("SINTATICO", "DECLARACAO MAL FORMATADA. IDENTIFICADOR ESPERADO")
            return False
        nome = self.valorAtual()
        comandos = []
        comandos.append(ast.Declaracao(ast.Identificador(nome, None), ast.Tipo(tipo, None), pos))
        self.pop()

        if self.matchTipo("ATRIBUICAO"):
            self.pop()
            pos = self.posAtual()
            valor = self.expressao()
            comandos.append(ast.Atribuicao(ast.Identificador(nome, None), valor, pos))
        
        if self.matchTipo("VIRGULA"):
            self.pop()
            novos = self.declaracao()
            comandos.append(novos)

        return comandos
       
    def atribuicao(self):
        if not self.matchGrupo("IDENTIFICADOR"):
            return False
        pos = self.posAtual()
        nome = self.valorAtual()
        self.pop()

        if not self.matchTipo("ATRIBUICAO"):
            self.erro("SINTATICO", "ATRIBUICAO MAL FORMATADA - ATRIBUICAO ESPERADA")
            return False
        self.pop()

        valor = self.expressao()
        return ast.Atribuicao(ast.Identificador(nome, None), valor, pos)



    def expressao(self): # virgula
        no = [self.expressao1()]

        if self.tipoAtual() == "VIRGULA":
            self.pop()
            return no + self.expressao()

        return no


    def expressao1(self): # atribuicao
        pos = self.posAtual()
        esquerda = self.expressao2()
        operador = self.tipoAtual()
        direita = self.expressao1_()

        if not direita: return esquerda
        if operador != "ATRIBUICAO":
                operador = ATRIBUICOES[operador]
                direita = ast.OperacaoBin(operador, esquerda, direita, pos)
                operador = "ATRIBUICAO"
        return ast.OperacaoBin(operador, esquerda, direita, pos)

    def expressao1_(self):
        pos = self.posAtual()
        operador = self.tipoAtual()

        if operador in ["ATRIBUICAO", "MAIS_IGUAL", "MENOS_IGUAL", "VEZES_IGUAL", "DIVIDIDO_IGUAL", "POTENCIA_IGUAL"]:
            self.pop()

            esquerda = self.expressao2()
            direita = self.expressao1_()
            if not direita: return esquerda
            
            if operador != "ATRIBUICAO":
                operador = ATRIBUICOES[operador]
                direita = ast.OperacaoBin(operador, esquerda, direita, pos)
                operador = "ATRIBUICAO"
            return ast.OperacaoBin("ATRIBUICAO", esquerda, direita, pos)
            
        return []


    def expressao2(self): # ternario
        pos = self.posAtual()
        esquerda = self.expressao3()
        centro = self.expressao2_()
        if not centro: return esquerda

        direita = self.expressao2__()
        if not direita: return esquerda

        return ast.OperacaoTer("TERNARIO", esquerda, centro, direita, pos)

    def expressao2_(self):
        operador = self.tipoAtual()

        if operador == "TERNARIO1":
            self.pop()

            centro = self.expressao3()
            return centro
            
        return []
    
    def expressao2__(self):
        operador = self.tipoAtual()

        if operador == "TERNARIO2":
            self.pop()

            direita = self.expressao2()
            return direita
        
        self.erro("Sintático", "EXPRESSAO TERNARIA MAL FORMATADA. ESPERAVA ❕")
        return []


    def expressao3(self): # or
        return self.expressao4()
    
    def expressao4(self): # and
        return self.expressao5()
    
    def expressao5(self): # igual / diferente
        pos = self.posAtual()
        esquerda = self.expressao6()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="IGUAL" or operador=="DIFERENTE":
            self.pop()

            direita = self.expressao6()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao6(self): # maior / menor
        pos = self.posAtual()
        esquerda = self.expressao7()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIOR" or operador=="MENOR" or operador=="MAIOR_IGUAL" or operador=="MENOR_IGUAL":
            self.pop()

            direita = self.expressao7()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao7(self): # mais / menos
        pos = self.posAtual()
        esquerda = self.expressao8()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIS" or operador=="MENOS":
            self.pop()

            direita = self.expressao8()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao8(self): # vezes / dividido / resto
        pos = self.posAtual()
        esquerda = self.expressao9()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="VEZES" or operador=="DIVIDIDO" or operador=="RESTO":
            self.pop()

            direita = self.expressao9()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao9(self): # unarios
        pos = self.posAtual()
        operador = self.tipoAtual()

        if operador=="NAO":
            self.pop()
            
            direita = self.expressao10()
            if not direita: return False

            return ast.OperacaoUn(operador, direita, pos)
        
        return self.expressao10()
    
    def expressao10(self): # parenteses
        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
            no = self.expressao()

            if no:
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                    return no
            self.erro("SINTATICO", "EXPRESSAO MAL FORMULADA OU FALTANTE")
            return False
        
        if self.ehValor():
            no = self.noValorAtual()
            self.pop()
            print("VALOR", no)
            return no
        
        self.erro("SINTATICO", "EXPRESSAO MAL FORMULADA")
        return False



    def programa(self):
        # inicio, bloco(s), fim
        if not self.matchTipo("INICIO"):
            self.erro("SINTATICO", "SEM TOKEN DE INICIO DE PROGRAMA")
            return False
        self.pop()


        codigo = self.bloco()
        if not codigo: return False
        self.arvore=codigo

        if not self.matchTipo("FIM"):
            self.erro("SINTATICO", "SEM TOKEN DE FIM DE PROGRAMA")
            return False
        self.pop()
        
        return not len(self.erros) > 0

    def analiseSintatica(self):
        return self.programa()
        