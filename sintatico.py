from token_classe import Token
import ArvoreSintatica as ast

TIPOS = {"INT", "FLOAT", "STRING", "CHAR", "BOOLEANO"}
FUNCOES = {"PRINT", "SCAN"}

class Sintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.erros = []
        self.arvore = ast.No

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
            print("⚠️  Erro Sintático!⚠️   ", erro[0], " 📍 ↔️ ", erro[1], ",↕️ ", erro[2])

    def erro(self, tipo="NAO ESPECIFICADO"):
        self.erros.append([f"Erro: {tipo}", self.tokens[0].linha, self.tokens[0].coluna])
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
            pos = self.posAtual()
            self.pop()

            arvore = ast.Bloco(self.bloco_(), pos)
            return arvore
            
        return False
        
    def bloco_(self):
        # self.imprimeTipoAtual()

        if self.matchTipo("FECHA_CHAVE"):
            self.pop()
            return []
        
        if self.matchTipo("ABRE_CHAVE"):
            return [self.bloco()] + self.bloco_()
        
        if self.matchGrupo(TIPOS):
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
            self.erro("TOKEN DE FIM DE CODIGO INESPERADO")
            return []

        if self.matchTipo("ELSE") or self.matchTipo("ELIF"):
            self.erro("BLOCO ELSE FORA DE CONDICAO")

        self.panic_mode()

        if self.matchTipo("FECHA_PARENTESES"):
            self.erro("TOKEN INESPERADO. PARENTESES FECHADO SEM ABERTURA")
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
            self.erro("PARAMETROS MAL FORMATADOS")
            self.panic_parenteses()
            return []
        
        if self.matchTipo("VIRGULA"):
            self.pop()
            return [valor] + self.parametros()
        
        if self.matchTipo("ABRE_CHAVE") or self.matchTipo("FECHA_CHAVE"):
            self.erro("PARAMETROS MAL FORMATADOS")
        
        return [valor]



    def funcao(self):
        if not self.matchGrupo(FUNCOES): return False
        nome = self.valorAtual()
        pos = self.posAtual()
        self.pop()

        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
        else:
            self.erro("FUNCAO MAL FORMATADA. ESPERAVA (")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return ast.ChamadaFuncao(nome, [], pos)

        parametros = self.parametros()

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("FUNCAO MAL FORMATADA. ESPERAVA )")
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
            self.erro("CONDICAO MAL FORMADA. ESPERAVA (")
            return []
        self.pop()

        condicao = self.condicao_cond()

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()

        else:
            self.erro("CONDICAO MAL FORMADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()

        cond_then = False

        if self.matchTipo("ABRE_CHAVE"):
            cond_then = self.bloco()
            if not cond_then:
                self.erro("BLOCO THEN FALTANTE")
        else:
            self.erro("BLOCO THEN FALTANTE")
        
        if not condicao and not cond_then:
            return []

        cond_else = self.condicao_else()
        return ast.Condicao(condicao, cond_then, cond_else, pos)


    def condicao_cond(self):
        if self.matchTipo("FECHA_PARENTESES"):
            self.erro("CONDICAO VAZIA. ESPERAVA UMA EXPESSÃO")
            return False

        condicao = self.expressao()
        if not condicao:
            self.erro("CONDICAO MAL FORMADA")
        return condicao
    
    def condicao_else(self):
        if self.matchTipo("ELIF"):
            self.pop()
            return ast.Bloco([self.condicao_()])
        
        if self.matchTipo("ELSE"):
            self.pop()

            if not self.matchTipo("ABRE_CHAVE"):
                self.erro("BLOCO ELSE FALTANTE")
                return []
            
            return self.bloco()
        
        else:
            self.erro("ESTRUTURA DE DECISAO MAL FORMATADA")
            return []

    def loop(self):
        if not self.matchTipo("FOR"):
            return False
        pos = self.posAtual()
        self.pop()
        
        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
        else:
            self.erro("ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA (")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()
            return []

        if self.matchGrupo(TIPOS) or self.matchTipo("DOIS_PONTOS"):
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
            self.erro("ESTRUTURA DE REPETICAO COM PARAMETROS MAL FORMULADOS")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()

        return []

    def loop_while(self):
        param = []
        if self.ehValor():
            param = self.expressao()
            if not param:
                self.erro("ESTRUTURA DE REPETICAO COM CONDICAO MAL FORMULADA")
                self.panic_parenteses()
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                return[]

        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"):
                self.pop()
            if not self.matchTipo("ABRE_CHAVE"): return []

        if not self.matchTipo("ABRE_CHAVE"):
            self.erro("ESTRUTURA DE REPETICAO SEM CORPO")
            return []

        corpo = self.bloco()
        if not corpo:
            self.erro("ESTRUTURA DE REPETICAO SEM CORTPO")

        return ast.Loop(param, corpo, None)

    def loop_for(self):
        param1 = self.loop_for_1()
        if self.matchTipo("DOIS_PONTOS"):
            self.pop()
        else:
            self.erro("ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA :")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return []
        
        param2 = self.loop_for_2()
        if not param2:
            self.erro("ESTRUTURA DE REPETICAO COM CONDICAO DE PARADA MAL FORMULADA")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()
            return []

        elif not self.matchTipo("DOIS_PONTOS"):
            self.erro("ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA :")
            if not self.matchTipo("FECHA_PARENTESES"):
                self.panic_parenteses()

        self.pop()

        param3 = self.loop_for_3()
        if self.matchTipo("FECHA_PARENTESES"):
            self.pop()
        else:
            self.erro("ESTRUTURA DE REPETICAO MAL FORMULADA. ESPERAVA )")
            self.panic_parenteses()
            if self.matchTipo("FECHA_PARENTESES"): self.pop()

        if not self.matchTipo("ABRE_CHAVE"):
            self.erro("ESTRUTURA DE REPETICAO SEM CORPO")
            return []

        corpo = self.bloco()
        corpo = ast.Bloco(param1 + corpo.statements + param3, None)
        return ast.Loop(param2, corpo, None)

    def loop_for_1(self):
        if self.matchTipo("DOIS_PONTOS") or self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.matchGrupo(TIPOS):
            decl = self.declaracao()
            if not decl: return [False]
            return decl + self.loop_for_1()
        
        elif self.matchTipo("PONTO_VIRGULA"):
            self.pop()
            return self.loop_for_1()
        
        self.erro("ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
        return []
    
    def loop_for_2(self):
        if self.matchTipo("DOIS_PONTOS") or self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.ehValor():
            expr = self.expressao()
            if not expr: return False
            return [expr] + self.loop_for_2()
        
        self.erro("ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
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
        
        self.erro("ESTRUTURA DE REPETICAO COM PARAMETRO MAL FORMULADO")
        return []


    def declaracao(self):
        if not self.matchGrupo(TIPOS):
            return False
        tipo = self.tipoAtual()
        pos = self.posAtual()
        self.pop()

        if not self.matchTipo("IDENTIFICADOR"):
            self.erro("DECLARACAO MAL FORMATADA. IDENTIFICADOR ESPERADO")
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
            self.erro("ATRIBUICAO MAL FORMATADA - ATRIBUICAO ESPERADA")
            return False
        self.pop()

        valor = self.expressao()
        return ast.Atribuicao(ast.Identificador(nome, None), valor, pos)



    def expressao(self):
        no = self.expressao1()
        return no
    
    def expressao1(self):
        esquerda = self.expressao2()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="OR":
            self.pop()

            direita = self.expressao2()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
        return esquerda
    
    def expressao2(self):
        pos = self.posAtual()
        esquerda = self.expressao3()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="AND":
            self.pop()

            direita = self.expressao3()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao3(self):
        esquerda = self.expressao4()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="IGUAL" or operador=="DIFERENTE":
            self.pop()

            direita = self.expressao4()
            if not direita: return False

            return ast.OperacaoBin(operador, esquerda, direita)
        return esquerda
    
    def expressao4(self):
        pos = self.posAtual()
        esquerda = self.expressao5()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIOR" or operador=="MENOR" or operador=="MAIOR_IGUAL" or operador=="MENOR_IGUAL":
            self.pop()

            direita = self.expressao5()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao5(self):
        pos = self.posAtual()
        esquerda = self.expressao6()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIS" or operador=="MENOS":
            self.pop()

            direita = self.expressao6()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao6(self):
        esquerda = self.expressao7()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="VEZES" or operador=="DIVIDIDO" or operador=="RESTO":
            self.pop()

            direita = self.expressao7()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
        return esquerda
    
    def expressao7(self):
        pos = self.posAtual()
        esquerda = self.expressao8()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="VEZES" or operador=="DIVIDIDO" or operador=="RESTO":
            self.pop()

            direita = self.expressao8()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita, pos)
        return esquerda
    
    def expressao8(self):
        operador = self.tipoAtual()
        if operador=="NAO" or operador=="MENOS" or operador=="MENOS1" or operador=="MAIS1":
            self.pop()

            direita = self.expressao9()
            if not direita: return False


            return ast.OperacaoUn(operador, direita)
        
        return self.expressao9()
    
    def expressao9(self):
        if self.matchTipo("ABRE_PARENTESES"):
            self.pop()
            no = self.expressao1()

            if no:
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                    return no
            self.erro("EXPRESSAO MAL FORMULADA OU FALTANTE")
            return False
        
        if self.ehValor():
            no = self.noValorAtual()
            self.pop()
            return no
        
        self.erro("EXPRESSAO MAL FORMULADA")
        return False



    def programa(self):
        # inicio, bloco(s), fim
        if not self.matchTipo("INICIO"):
            self.erro("SEM TOKEN DE INICIO DE PROGRAMA")
            return False
        self.pop()


        codigo = self.bloco()
        if not codigo: return False
        self.arvore=codigo

        if not self.matchTipo("FIM"):
            self.erro("SEM TOKEN DE FIM DE PROGRAMA")
            return False
        self.pop()
        
        return not len(self.erros) > 0

    def analiseSintatica(self):
        return self.programa()
        