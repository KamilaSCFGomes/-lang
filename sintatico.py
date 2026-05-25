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

    def noValorAtual(self):
        if self.matchTipo("NUMERAL"):
            return ast.Numero(self.valorAtual())
        if self.matchTipo("IDENTIFICADOR"):
            return ast.Identificador(self.valorAtual())
        if self.matchTipo("BOOLEANO"):
            return ast.Booleano(self.valorAtual())
        if self.matchTipo("TEXTO"):
            return ast.String(self.valorAtual())
        
        return False

    def adicionaErro(self, tipo="Nao especificado"):
        self.erros.append([tipo, self.tokens[0].linha, self.tokens[0].coluna])

    def erro(self, tipo="NAO ESPECIFICADO"):
        self.adicionaErro(f"Erro: {tipo}")
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
        return self.matchClasse("LITERAL") or self.matchClasse("BOOLEANO") or self.matchClasse("IDENTIFICADOR")

    def panic_mode(self):
        linha_atual = self.tokens[0].linha
        
        while(len(self.tokens) > 0 and not self.matchTipo("FIM")):
            # token seguro:
            if self.matchTipo("FECHA_CHAVE") or self.matchTipo("PONTO_VIRGULA") or self.matchTipo("FECHA_PARENTESES"):
                return
            
            # inicio de outra funcao:
            if self.matchGrupo(FUNCOES):
                return
            
            # inicio de outra linha:
            if self.tokens[0].linha != linha_atual:
                return
            
            self.pop()

    def panic_parenteses(self):
        while(len(self.tokens) > 0 and not self.matchTipo("FIM")):
            # token seguro:
            if self.matchTipo("FECHA_CHAVE") or self.matchTipo("ABRE_CHAVE") or self.matchTipo("FECHA_PARENTESES"):
                return
            
            self.pop()
            


    def bloco(self):
        if self.matchTipo("ABRE_CHAVE"):
            self.pop()

            arvore = ast.Bloco(self.bloco_())
            return arvore
            
        return False
        
    def bloco_(self):
        self.imprimeTipoAtual()

        if self.matchTipo("FECHA_CHAVE"):
            self.pop()
            return []
        
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
        
        if self.matchGrupo("IDENTIFICADOR"):
            atri = self.atribuicao()
            if not atri: return self.bloco_()
            return [atri] + self.bloco_()
        
        if self.matchGrupo(FUNCOES):
            funcao = self.funcao()
            if not funcao: return self.bloco_()
            return [funcao] + self.bloco_()

        self.erro("COMANDO NAO IDENTIFICADO")
        self.panic_mode()
        return []


    def parametros(self):
        if self.matchTipo("FECHA_PARENTESES"):
            return []
        
        valor = self.expressao()
        if not valor:
            self.erro("PARAMETROS MAL FORMATADOS")
            self.panic_mode()
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
        self.pop()

        if not self.matchTipo("ABRE_PARENTESES") and not self.matchTipo("FECHA_PARENTESES"):
            self.erro("FUNCAO SEM PARAMETROS")
            return []
        self.pop()

        parametros = self.parametros()
        
        if not self.matchTipo("FECHA_PARENTESES"):
            self.erro("PARAMETROS MAL FORMATADOS")
            self.panic_mode()
            
        if self.matchTipo("FECHA_PARENTESES"): self.pop()
        self.imprimeTipoAtual()

        return ast.ChamadaFuncao(nome, parametros)
    

    def condicao(self):
        if not self.matchTipo("IF"): return False
        self.pop()
        
        return self.condicao_()

    def condicao_(self):
        condicao = self.condicao_cond()
        if not condicao: 
            return []
        
        cond_then = self.bloco()
        if not cond_then:
            return []

        cond_else = self.condicao_else()

        return ast.Condicao(condicao, cond_then, cond_else)


    def condicao_cond(self):
        if not self.matchTipo("ABRE_PARENTESES"):
            self.erro("CONDICAO MAL FORMADA. ESPERAVA (")
            return False
        self.pop()

        condicao = self.expressao()
        if not condicao: return False

        if not self.matchTipo("FECHA_PARENTESES"):
            self.erro("CONDICAO MAL FORMADA. ESPERAVA )")
            self.panic_parenteses()
            return condicao
        self.pop()

        return condicao
    
    def condicao_else(self):
        if self.matchTipo("ELIF"):
            self.pop()
            return ast.Bloco([self.condicao_()])
        
        if self.matchTipo("ELSE"):
            self.pop()

            if not self.matchTipo("ABRE_CHAVE"):
                self.erro("BLOCO ELSE FALTANTE")
                return False
            
            return self.bloco()
        
        else: return True

    def loop(self):
        if not self.matchTipo("FOR"):
            return False
        self.pop()
        
        if not self.matchTipo("ABRE_PARENTESES"):
            self.erro("ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA (")
            return False
        self.pop()

        loop1=self.loop1()
        loop2=self.loop2()
        loop3=self.loop3()

        if not (loop1 and loop2 and loop3):
            self.erro("ESTRUTURA DE REPETICAO COM PARAMETROS MAL FORMATADOS")
            return False

        if not self.matchTipo("FECHA_PARENTESES"):
            self.erro("ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA )")
            return False
        self.pop()

        corpo = self.bloco()
        if not corpo: return False

        corpo = ast.Bloco(loop1 + corpo.statements + loop3)
        return ast.Loop(loop2, corpo)

    def loop1(self):
        if self.matchTipo("DOIS_PONTOS"):
            self.pop()
            return []
        
        elif self.matchGrupo(TIPOS):
            decl = self.declaracao()
            if not decl: return [False]
            return decl + self.loop1()
        
        elif self.matchGrupo(FUNCOES):
            fun = self.funcao()
            if not fun: return [False]
            return [fun] + self.loop1()
        
        elif self.matchTipo("PONTO_VIRGULA"):
            self.pop()
            return self.loop1()
        
        return [False]
    
    def loop2(self):
        if self.matchTipo("DOIS_PONTOS"):
            self.pop()
            return []
        
        elif self.ehValor():
            expr = self.expressao()
            if not expr: return False
            return [expr] + self.loop2()
        
        elif self.matchGrupo(FUNCOES):
            fun = self.funcao()
            if not fun: return False
            return [fun] + self.loop2()
        
        return False

    def loop3(self):
        if self.matchTipo("FECHA_PARENTESES"):
            return []
        
        elif self.ehValor():
            expr = self.atribuicao()
            if not expr: return False
            return [expr] + self.loop3()
        
        elif self.matchGrupo(FUNCOES):
            fun = self.funcao()
            if not fun: return False
            return [fun] + self.loop3()
        
        elif self.matchTipo("PONTO_VIRGULA"):
            self.pop()
            return self.loop3()
        
        return False


    def declaracao(self):
        if not self.matchGrupo(TIPOS):
            return False
        tipo = self.tipoAtual()
        self.pop()

        if not self.matchTipo("IDENTIFICADOR"):
            self.erro("DECLARACAO MAL FORMATADA. IDENTIFICADOR ESPERADO")
            return False
        nome = self.valorAtual()
        comandos = []
        comandos.append(ast.Declaracao(ast.Identificador(nome), ast.Tipo(tipo)))
        self.pop()

        if self.matchTipo("ATRIBUICAO"):
            self.pop()
            valor = self.expressao()
            comandos.append(ast.Atribuicao(ast.Identificador(nome), valor))
        
        if self.matchTipo("VIRGULA"):
            self.pop()
            novos = self.declaracao()
            comandos.append(novos)

        return comandos



    def declaracao_(self):
        if not self.matchGrupo(TIPOS): return False
        self.adicionaAnalise("Declaração de variável")
        self.pop()

        if not self.matchClasse("IDENTIFICADOR"):
            self.erro("DECLARACAO MAL FORMATADA")
            return False
        self.pop()

        if not self.atribuicao(): return False # atribuicao
        if not self.declaracao__(): return False # varias variaveis

        return True
        
    def atribuicao(self):
        if not self.matchGrupo("IDENTIFICADOR"):
            return False
        nome = self.valorAtual()
        self.pop()

        if not self.matchTipo("ATRIBUICAO"):
            self.erro("ATRIBUICAO MAL FORMATADA - ATRIBUICAO ESPERADA")
            return False
        self.pop()

        valor = self.expressao()
        return ast.Atribuicao(ast.Identificador(nome), valor)

        
    def declaracao__(self):
        if self.matchTipo("VIRGULA"):
            self.adicionaAnalise("Várias variáveis")
            self.pop()

            if not self.matchClasse("IDENTIFICADOR"):
                self.erro("DECLARACAO MAL FORMATADA")
                return False
            self.pop()

            if not self.atribuicao(): return False # atribuicao
            if not self.declaracao__(): return False # varias variaveis

        return True # vazio


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
        esquerda = self.expressao3()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="AND":
            self.pop()

            direita = self.expressao3()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
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
        esquerda = self.expressao5()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIOR" or operador=="MENOR" or operador=="MAIOR_IGUAL" or operador=="MENOR_IGUAL":
            self.pop()

            direita = self.expressao5()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
        return esquerda
    
    def expressao5(self):
        esquerda = self.expressao6()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="MAIS" or operador=="MENOS":
            self.pop()

            direita = self.expressao6()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
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
        esquerda = self.expressao8()
        if not esquerda: return False

        operador = self.tipoAtual()
        if operador=="VEZES" or operador=="DIVIDIDO" or operador=="RESTO":
            self.pop()

            direita = self.expressao8()
            if not direita: return False


            return ast.OperacaoBin(operador, esquerda, direita)
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
        
        return codigo

    def analiseSintatica(self):
        return self.programa()
        