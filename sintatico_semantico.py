from token_classe import Token
import arvore_sintatica as ast
import tabela_simbolos as tab

CONVERSAO_DE_OPERADOR = {
    "MAIS_IGUAL": "MAIS",
    "MENOS_IGUAL": "MENOS",
    "VEZES_IGUAL": "VEZES",
    "DIVIDIDO_IGUAL": "DIVIDIDO",
    "POTENCIA_IGUAL": "POTENCIA"
    }

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
        if self.matchClasse("LITERAL"):
            return ast.Literal(self.valorAtual(), self.tipoAtual(), self.posAtual())
        if self.matchClasse("IDENTIFICADOR"):
            return ast.Identificador(self.valorAtual(), self.posAtual(), None)
        
        return False
    
    def imprimeErros(self):
        for erro in self.erros:
            print(f"⚠️  Erro!⚠️   {erro[0]} 📍 {erro[1]}")

    def imprimeWarnings(self):
        for w in self.warnings:
            print(f"⚠️  Warning!⚠️   {w[0]} 📍 {w[1]}")


    def erro(self, categoria="", tipo="NAO ESPECIFICADO"):
        self.erros.append([f"Erro {categoria}: {tipo}", [self.tokens[0].linha, self.tokens[0].coluna]])
        print(f"⚠️  Erro {categoria}!⚠️   {tipo} 📍 {[self.tokens[0].linha, self.tokens[0].coluna]}")
        return
    
    def warning(self, tipo=["NAO ESPECIFICADO"]):
        for t in tipo:
            self.warnings.append([f"Warning: {t}", [self.tokens[0].linha, self.tokens[0].coluna]])
            print(f"⚠️  Warning!⚠️   {t} 📍 {[self.tokens[0].linha, self.tokens[0].coluna]}")
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
        return self.matchClasse("LITERAL") or self.matchClasse("IDENTIFICADOR")

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
            

    def abrir_escopo(self):
        return self.tabela_simbolos.abrir_escopo()
    
    def fechar_escopo(self):
        sucesso, resposta = self.tabela_simbolos.fechar_escopo()
        if not sucesso:
            self.erro("SEMANTICO", resposta)
            return
        if resposta:
            self.warning(resposta)
            return

    def adiciona_variavel(self, decla):
        sucesso, erro = self.tabela_simbolos.declaracao(decla)
        if sucesso: return
        self.erro("SEMANTICO", erro)
    
    def declara_variavel(self, declaracao):
        sucesso, erro = self.tabela_simbolos.declaracao(declaracao)
        if sucesso: return
        self.erro("SEMANTICO", erro)

    def adiciona_funcao(self, nome, params, tipo, pos):
        sucesso, erro = self.tabela_simbolos.adiciona_funcao(nome, tipo, pos)
        if sucesso: return
        self.erro("SEMANTICO", erro)
    
    def verifica_variavel(self, nome):
        sucesso, tipo = self.tabela_simbolos.verifica_variavel(nome)
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)
    
    def verifica_funcao(self, nome, params):
        sucesso, tipo = self.tabela_simbolos.verifica_funcao(nome, params)
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)

    def verifica_operacao_variaveis(self, operador, variaveis):
        sucesso, tipo = self.tabela_simbolos.verifica_operacao_variaveis(operador, variaveis)
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)
    
    def verifica_operacao_tipos(self, operador, tipos):
        sucesso, tipo = self.tabela_simbolos.verifica_operacao_tipos(operador, tipos)
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)

    def verifica_break_continue(self):
        sucesso, tipo = self.tabela_simbolos.verifica_break_continue()
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)

    def atribui_tabela(self, atribuicao):            
        sucesso, tipo = self.tabela_simbolos.atribuicao(atribuicao)
        if sucesso: return True
        self.erro("SEMANTICO", tipo)
        return False

    def resolve_expressao(self, expressao):
        sucesso, tipo = self.tabela_simbolos.resolve_expressao(expressao)
        if sucesso: return tipo
        self.erro("SEMANTICO", tipo)
        return False

    def bloco(self):
        if self.matchTipo("ABRE_CHAVE"):
            self.abrir_escopo()
            pos = self.posAtual()
            self.pop()

            arvore = ast.Bloco(self.bloco_(), pos)
            self.fechar_escopo()
            return arvore
            
        return False
        
    def bloco_(self):

        if self.matchTipo("FECHA_CHAVE"):
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

        if self.matchClasse("IDENTIFICADOR"):
            expressao = self.expressao()
            if not expressao: return self.bloco_()
            return expressao + self.bloco_()

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
        
        if self.matchTipo("FECHA_PARENTESES"):
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA UMA EXPRESSAO")
            self.pop()
            return []
        
        self.abrir_escopo()
        valor1 = self.loop_()
        
        if self.matchTipo("FECHA_PARENTESES"): # WHILE
            self.pop()

            if len(valor1) < 1:
                self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CONDICAO DE PARADA")
                self.fechar_escopo()
                return []

            if self.matchTipo("ABRE_CHAVE"):
                corpo = self.bloco()
                if corpo:
                    self.fechar_escopo()
                    return ast.Loop(valor1, corpo, pos)
                
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CORPO")
            self.fechar_escopo()
            return []
        

        if self.matchTipo("DOIS_PONTOS"): # FOR
            self.pop()

            valor2 = self.loop_()
            if len(valor2) < 1:
                self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CONDICAO DE PARADA")
                self.fechar_escopo()
                return []

            if self.matchTipo("DOIS_PONTOS"):
                self.pop()
                valor3 = self.loop_()

                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                else:
                    self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA )")
                    self.panic_parenteses()
                    if self.matchTipo("FECHA_PARENTESES"):
                        self.pop
                    self.fechar_escopo()
                    return []

            else:
                self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA :")
                self.panic_parenteses()
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop
                self.fechar_escopo()
                return []
            
            if self.matchTipo("ABRE_CHAVE"):
                self.pop()

                corpo = ast.Bloco(self.bloco_(), pos)
                if corpo:
                    novo_corpo = corpo.statements + valor3
                    loop = ast.Loop(valor2, novo_corpo, pos)
                    bloco = ast.Bloco(valor1 + [loop], corpo.pos)
                    self.fechar_escopo()
                    return bloco
                
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO SEM CORPO")

        self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA UMA EXPRESSAO")
        self.fechar_escopo()
        return []        

    def loop_(self):
        if self.matchGrupo(tab.TIPOS):
            return self.declaracao()
        
        elif self.ehValor():
            return self.expressao()
        
        else:
            self.erro("SINTATICO", "ESTRUTURA DE REPETICAO MAL FORMATADA. ESPERAVA UMA EXPRESSAO")
            return [False]


    def quebra_declaracoes(self, v, tipo):

        if len(v) < 1:
            return []

        print('coiso ',v)
        pos = v[0].pos

        if isinstance(v[0], ast.OperacaoBin) and v[0].operador == "ATRIBUICAO":
            identificador = v[0].esquerda
            valor = v[0].direita
            
            declaracao = ast.Declaracao(identificador, tipo, pos)
            atribuicao = ast.OperacaoBin("ATRIBUICAO", identificador, valor, v[0].pos, None)
            self.declara_variavel(declaracao)
            self.atribui_tabela(atribuicao)

            return [declaracao, atribuicao] + self.quebra_declaracoes(v[1:], tipo)

        if isinstance(v[0], ast.Identificador):
            self.declara_variavel(v[0], tipo, pos)
            return [ast.Declaracao(v[0], tipo, v[0].pos)] + self.quebra_declaracoes(v[1:], tipo)
        return self.quebra_declaracoes(v[1:], tipo)

    def declaracao(self):
        if not self.matchGrupo(tab.TIPOS):
            return False
        tipo = self.tipoAtual()
        self.pop()

        if not self.matchGrupo("IDENTIFICADOR"):
            self.erro("SINTATICO", "DECLARACAO SEM IDENTIFICADOR")
            return[]
        
        comandos = self.expressao(tipo)
        return comandos


    def expressao(self, decla=False): # virgula
        no = [self.expressao1(decla)]

        if self.tipoAtual() == "VIRGULA":
            self.pop()
            return no + self.expressao()

        return no


    def expressao1(self, decla=False): # atribuicao
        print('EXPRESSAO1 ', self.valorAtual())
        pos = self.posAtual()
        esquerda = self.expressao2()
        operador = self.tipoAtual()
        direita = self.expressao1_(decla)
        comandos = []

        if not direita: return esquerda
        if decla:
            decla = ast.Declaracao(esquerda, decla, pos)
            comandos += [decla]
            self.adiciona_variavel(decla)

        if operador != "ATRIBUICAO":
            operador = CONVERSAO_DE_OPERADOR[operador]
            direita = ast.OperacaoBin(operador, esquerda, direita, pos, None)
            operador = "ATRIBUICAO"

        atribuicao = ast.OperacaoBin(operador, esquerda, direita, pos, None)
        atribuicao = self.atribui_tabela(atribuicao)
        if not atribuicao: return []
        comandos += [atribuicao]
        print(comandos)
        return comandos
        
    def expressao1_(self, decla=False):
        print('EXPRESSAO1- ', self.valorAtual())
        pos = self.posAtual()
        operador = self.tipoAtual()

        if operador in ["ATRIBUICAO", "MAIS_IGUAL", "MENOS_IGUAL", "VEZES_IGUAL", "DIVIDIDO_IGUAL", "POTENCIA_IGUAL"]:
            self.pop()

            esquerda = self.expressao2()
            direita = self.expressao1_()
            print('esq-dir', esquerda, direita)
            if not direita: return esquerda
            if decla: comandos += [ast.Declaracao(esquerda, decla, pos)]
            
            if operador != "ATRIBUICAO":
                operador = CONVERSAO_DE_OPERADOR[operador]
                direita = ast.OperacaoBin(operador, esquerda, direita, pos, None)
                direita = self.resolve_expressao(direita)
                if not direita: return []
                operador = "ATRIBUICAO"
            
            atribuicao = ast.OperacaoBin("ATRIBUICAO", esquerda, direita, pos, None)
            atribuicao = self.atribui_tabela(atribuicao)
            if not atribuicao: return []
            comandos += [atribuicao]
            print(comandos)
            return comandos

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
        return self.expressao3_(self.expressao4())

    def expressao3_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()
        if operador == "OR":
            self.pop()

            direita = self.expressao4()
            nova_esquerda = ast.OperacaoBin(operador, esquerda, direita, pos, None)
            return self.expressao3_(nova_esquerda)
        
        return esquerda


    def expressao4(self): # and
        return self.expressao4_(self.expressao5())

    def expressao4_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()
        if operador == "AND":
            self.pop()

            direita = self.expressao5()
            nova_esquerda = ast.OperacaoBin(operador, esquerda, direita, pos, None)
            return self.expressao4_(nova_esquerda)
        
        return esquerda


    def expressao5(self): # igual/diferente
        return self.expressao5_(self.expressao6())

    def expressao5_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()
        if operador in ["IGUAL", "DIFERENTE"]:
            self.pop()

            direita = self.expressao6()
            nova_esquerda = ast.OperacaoBin("IGUAL", esquerda, direita, pos, None)

            if operador == "DIFERENTE":
                nova_esquerda = ast.OperacaoUn("NAO", nova_esquerda, pos, None)
            return self.expressao5_(nova_esquerda)

        return esquerda
    

    def expressao6(self): # maior/menor
        return self.expressao6_(self.expressao7())

    def expressao6_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()
        if operador in ["MAIOR", "MENOR", "MAIOR_IGUAL", "MENOR_IGUAL"]:
            self.pop()

            direita = self.expressao7()

            # converter todas as operações em MAIOR:
            if operador in ["MAIOR_IGUAL", "MENOR"]:
                nova_esquerda = ast.OperacaoBin("MAIOR", direita, esquerda, pos, None)
            else:
                nova_esquerda = ast.OperacaoBin("MAIOR", esquerda, direita, pos, None)

            if operador in ["MAIOR_IGUAL", "MENOR_IGUAL"]:
                nova_esquerda = ast.OperacaoUn("NAO", nova_esquerda, pos, None)

            return self.expressao6_(nova_esquerda)
        return esquerda
    
    
    def expressao7(self): # mais/menos
        return self.expressao7_(self.expressao8())

    def expressao7_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()
        if operador in ["MAIS", "MENOS"]:
            self.pop()

            direita = self.expressao8()
            nova_esquerda = ast.OperacaoBin(operador, esquerda, direita, pos, None)
            return self.expressao7_(nova_esquerda)
        return esquerda


    def expressao8(self): # vezes/dividido/resto
        return self.expressao8_(self.expressao9())

    def expressao8_(self, esquerda):
        pos = self.posAtual()
        
        operador = self.tipoAtual()        
        if operador in ["VEZES", "DIVIDIDO", "RESTO"]:
            self.pop()

            direita = self.expressao9()
            nova_esquerda = ast.OperacaoBin(operador, esquerda, direita, pos, None)
            return self.expressao8_(nova_esquerda)
        
        return esquerda


    def expressao9(self): # potencia
        pos = self.posAtual()
        esquerda = self.expressao10()
        operador = self.tipoAtual()
        direita = self.expressao9_()

        if not direita: return esquerda
        return ast.OperacaoBin(operador, esquerda, direita, pos, None)

    def expressao9_(self):
        pos = self.posAtual()
        operador = self.tipoAtual()

        if operador == "POTENCIA":
            self.pop()

            esquerda = self.expressao10()
            direita = self.expressao9_()
            if not direita: return esquerda
            
            return ast.OperacaoBin("ATRIBUICAO", esquerda, direita, pos, None)
        return []


    def expressao10(self): # unarios
        pos = self.posAtual()
        operador = self.tipoAtual()

        if operador in ["MAIS_MAIS", "MENOS_MENOS", "NAO", "CAST_INT", "CAST_FLOAT", "CAST_STRING", "CAST_CHAR", "CAST_BOOLEANO", "MENOS"]:
            self.pop()

            direita = self.expressao10()

            if operador == "MAIS_MAIS":
                return ast.OperacaoBin("MAIS", direita, ast.Numero(1, None), pos, None)
            
            if operador == "MENOS_MENOS":
                return ast.OperacaoBin("MENOS", direita, ast.Numero(1, None), pos, None)
            
            if operador == "MENOS":
                return ast.OperacaoBin("VEZES", direita, ast.Numero(-1, None), pos, None)
            
            return ast.OperacaoUn(operador, direita, pos, None)
        
        return self.expressao11()    
    

    def expressao11(self): # parenteses/incremento-pos
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
            return self.expressao11_()
        
        self.erro("SINTATICO", "EXPRESSAO MAL FORMULADA")
        return False
    
    def expressao11_(self):
        no = self.noValorAtual()
        self.pop()

        if self.matchTipo("ABRE_PARENTESES"): # chamada de funcao
            self.pop()
            param = self.expressao()
            if param:
                if self.matchTipo("FECHA_PARENTESES"):
                    self.pop()
                    return ast.ChamadaFuncao(no, param, None)
                self.erro("SINTATICO", "EXPRESSAO MAL FORMULADA OU FALTANTE")
        # nao era chamada de funcao
        return no

        

    def programa(self):

        self.tabela_simbolos.imprimir()
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
        