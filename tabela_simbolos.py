TIPOS = {"INT", "FLOAT", "STRING", "CHAR", "BOOLEANO"}
import arvore_sintatica as ast

OPERACOES_SEMELHANTES = {
    'MAIS':'MAIS',
    'MENOS':'MENOS',
    'VEZES':'MENOS',
    'DIVIDIDO':'DIVIDIDO',
    'RESTO':'RESTO',
    'POTENCIA':'MENOS',
    'IGUAL':'IGUAL',
    'MAIOR':'IGUAL',
    'AND':'AND',
    'OR':'AND',
    'NAO':'NAO'
    }

TABELA_OPERACOES = {
    'MAIS': {
        'INT': {
            'INT': 'INT',
            'FLOAT': 'FLOAT'},
        'FLOAT': {
            'INT': 'FLOAT',
            'FLOAT': 'FLOAT'},
        'STRING': {
            'STRING': 'STRING',
            'CHAR': 'STRING',
            'INT': 'STRING',
            'FLOAT': 'STRING'},
        'CHAR': {
            'STRING': 'STRING',
            'CHAR': 'STRING',
            'INT': 'STRING',
            'FLOAT': 'STRING'},
        },
    'MENOS': {
        'INT': {
            'INT': 'INT',
            'FLOAT': 'FLOAT'},
        'FLOAT': {
            'INT': 'FLOAT',
            'FLOAT': 'FLOAT'}
        },
    'DIVIDIDO': {
        'INT': {
            'INT': 'FLOAT',
            'FLOAT': 'FLOAT'},
        'FLOAT': {
            'INT': 'FLOAT',
            'FLOAT': 'FLOAT'}
        },
    'RESTO': {
        'INT': {
            'INT': 'INT',
            'FLOAT': 'INT'},
        'FLOAT': {
            'INT': 'INT',
            'FLOAT': 'INT'}
        },
    'IGUAL': {
        'INT': {
            'INT': 'BOOLEANO',
            'FLOAT': 'BOOLEANO'},
        'FLOAT': {
            'INT': 'BOOLEANO',
            'FLOAT': 'BOOLEANO'},
        'STRING': {
            'STRING': 'BOOLEANO',
            'CHAR': 'BOOLEANO'},
        'CHAR': {
            'STRING': 'BOOLEANO',
            'CHAR': 'BOOLEANO'}
        },
    'AND': {
        'INT': {
            'INT': 'BOOLEANO',
            'FLOAT': 'BOOLEANO'},
        'FLOAT': {
            'INT': 'BOOLEANO',
            'FLOAT': 'BOOLEANO'},
        },
    'NAO': {'BOOLEANO'}
    }    


class TabelaSimbolos:

    def __init__(self):
        self.escopo_atual = -1
        self.escopo_com_loop = 0
        self.tabela = {}

        self.adiciona_funcao("PRINT", "STRING", "VOID")
        self.adiciona_funcao("SCAN", "STRING", "VOID")
        self.abrir_escopo()

    def adiciona_variavel(self, nome, tipo, pos=[], categ="VARIAVEL"):
        return self.adiciona_funcao(nome, [], tipo, pos, categ)
    
    def adiciona_funcao(self, nome, params, tipo, pos=[], categ="FUNCAO"):
        if isinstance(nome, ast.Identificador):
            nome = nome.nome

        if nome in self.tabela:
            return False, f"Declaracao duplicada. {nome} ja foi declarado como {self.tabela[nome]['categ']} {self.tabela[nome]['tipo']} em {self.tabela[nome]['pos']}"
        
        self.tabela[nome] = {"tipo": tipo, "categ": categ, "params": params, "valor": False, "pos": pos, "escopo": self.escopo_atual, "usada": False}
        print(nome, "ADICIONADA!!!")
        self.imprimir_tabela()
        return True, ""

    def atribui_identificador(self, nome, valor):
        if isinstance(nome, ast.Identificador):
            nome=nome.nome
        try:
            self.tabela[nome]['valor'] = valor
            return True, ''
        except:
            return False, 'erro em atribuicao'

    def imprimir(self):
        print(f"Escopo: {self.escopo_atual}\tEscopo com loop: {self.escopo_com_loop}")
        self.imprimir_tabela()

    def imprimir_tabela(self):
        keys=['tipo', 'categ', 'pos', 'escopo', 'usada', 'valor', 'params']
        espacos= [True, True, True, True, False, False, True, False]
        print('nome', end='')
        
        for k in range(len(keys)):
            espacos[k] and print('\t', end='')
            print('\t', end='')
            print(keys[k], end='')
        print('')

        for v in self.tabela:
            print(v, end='\t')
            if len(v) < 8: print('\t', end='')

            for k in range(len(keys)):
                valor = self.tabela[v][keys[k]]
                print(valor, end='')
                if len(str(valor)) < 8: print('\t', end='')
                if len(str(valor)) < 16 and espacos[k+1]: print('\t', end='')

            print('')

    def abrir_escopo(self, loop=False):
        self.escopo_atual += 1
        if loop: self.escopo_com_loop += 1

    def fechar_escopo(self, loop=False):
        warnings = []
        remover = []
        self.imprimir_tabela()
        for variavel in self.tabela:
            if self.tabela[variavel]['escopo'] >= self.escopo_atual and not self.tabela[variavel]['usada']:
                warnings.append(f"Variavel nao usada: {variavel}, declarada em {self.tabela[variavel]['pos']}")
                remover.append(variavel)
        
        for v in remover:
            self.tabela.pop(v)

        self.escopo_atual -= 1
        if loop: self.escopo_com_loop -= 1
        if self.escopo_atual < 0 or self.escopo_com_loop < 0:
            return False, f"Fechamento de escopo inadequado"

        if len(warnings) >= 1:
            return True, warnings
        else:
            return True, ""

    def verifica_variavel(self, nome):
        if isinstance(nome, ast.Identificador):
            nome=nome.nome

        sucesso = nome in self.tabela
        if sucesso: return sucesso, ''
        else: return sucesso, f"variavel {nome} nao declarada"
    
    def valor_variavel(self, nome):
        if isinstance(nome, ast.Identificador):
            nome=nome.nome
        
        sucesso, tipo = self.verifica_variavel(nome)
        if not sucesso: return sucesso, tipo

        valor = self.tabela[nome]['valor']
        if not valor: return False, f"valor da variavel {nome} nao declarado"
        return True, valor

    def retorna_variavel(self, identificador):
        nome = identificador.nome if isinstance(identificador, ast.Identificador) else identificador
        sucesso, tipo = self.verifica_variavel(nome)
        if not sucesso: return sucesso, tipo

        return True, self.tabela[nome]


    def declaracao(self, declaracao):
        identificador = declaracao.nome
        if not isinstance(identificador, ast.Identificador):
            return False, f"declaracao sem identificador"

        nome = identificador.nome
        tipo = declaracao.tipo
        pos = declaracao.pos

        return self.adiciona_variavel(nome, tipo, pos)

    def atribuicao(self, atribuicao):
        if not isinstance(atribuicao, ast.OperacaoBin) or atribuicao.operador != "ATRIBUICAO":
            return False, "Erro de atribuicao"

        identificador = atribuicao.esquerda
        valor = atribuicao.direita

        if not isinstance(identificador, ast.Identificador):
            return False, "Atribuicao mal formatada. esperava um identificador"
        
        sucesso, variavel = self.retorna_variavel(identificador)
        if not sucesso: return sucesso, variavel

        if isinstance(valor, ast.Identificador):
            sucesso, variavel = self.retorna_valor(valor)
            if not sucesso: return sucesso, variavel
            tipo = variavel.tipo
            valor = variavel.valor
        
        elif isinstance(valor, ast.Literal):
            tipo = valor.tipo
            valor = valor.valor
            
        else:
            sucesso, valor = self.resolve_expressao(valor)
            if not sucesso: return sucesso, valor
            return self.atribuicao(valor)

        sucesso, variavel = self.retorna_variavel(identificador)
        if not sucesso: return sucesso, variavel

        tipo_var = variavel['tipo']
        if tipo != tipo_var and not (tipo == 'INT' and tipo_var == 'FLOAT'):
            return False, f"tentativa de atribuicao de tipo {tipo} a variavel {identificador.nome} de tipo {tipo_var}"

        return self.atribui_identificador(identificador, valor)

    def retorna_valor(self, no):
        if isinstance(no, ast.Literal):
            tipo = no.tipo
            valor = no.valor

        elif isinstance(no, ast.Identificador):
            sucesso, variavel = self.retorna_variavel(no)
            if not sucesso: return sucesso, variavel
            tipo = variavel['tipo']
            valor = variavel['valor']
            literal = ast.Literal(valor, tipo, None)

        else:
            return False, "Erro ao recuperar o valor de um nó"
        
        return True, {'valor':valor, 'tipo':tipo}

    def calcula_expressao(self, no):
        operador = no.operador
        pos = no.pos

        if operador == "NAO":
            valor = no.operando.valor == "True"
            return True, ast.Literal(valor, 'BOOLEANO', pos)
        
        esquerda = no.esquerda
        direita = no.direita
        if operador == "MAIOR":
            return True, ast.Literal(str(esquerda>direita), 'BOOLEANO', pos)
        
        if operador == "AND":
            return True, ast.Literal(str(esquerda and direita), 'BOOLEANO', pos)
        
        if operador == "OR":
            return True, ast.Literal(str(esquerda or direita), 'BOOLEANO', pos)
        
        
        tipo = TABELA_OPERACOES[operador][esquerda][direita]

        if operador == "MAIS":
            return True, ast.Literal(str(esquerda+direita), tipo, pos)
        
        if operador == "VEZES":
            return True, ast.Literal(str(esquerda*direita), tipo, pos)
        
        if operador == "MENOS":
            return True, ast.Literal(str(esquerda-direita), tipo, pos)
        
        if operador == "DIVIDIDO":
            return True, ast.Literal(str(esquerda/direita), tipo, pos)

    def resolve_expressao(self, no):
        print("FUNCAO EXPRESSAO")
        print("\nRESOLVE EXPRESSAO", no)
        
        if isinstance(no, ast.Identificador) or isinstance(no, ast.Literal):
            return True, no
        
        if isinstance(no, ast.OperacaoUn):
            operador = no.operador
            try: operador2 = OPERACOES_SEMELHANTES[operador]
            except: return False, f"Operador {operador} nao encontrado na tabela de expressoes"

            sucesso, operando = self.resolve_expressao(no.operando)
            if not sucesso: return sucesso, operando

            if not operador2 in TABELA_OPERACOES:
                return False, "Operador nao encontrado na tabela de expressoes"
            
            if not operando.tipo in TABELA_OPERACOES[operador]:
                return False, f"Operacao {operador} nao permitida para o tipo {operando.tipo}"
            
            return 

        if isinstance(no, ast.OperacaoBin):
            operador = no.operador
            try: operador2 = OPERACOES_SEMELHANTES[operador]
            except: return False, f"Operador {operador} nao encontrado na tabela de expressoes"

            sucesso, esquerda = self.resolve_expressao(no.esquerda)
            if not sucesso: return sucesso, esquerda

            sucesso, direita = self.resolve_expressao(no.direita)
            if not sucesso: return sucesso, direita

            print("COISOOOO",operador, esquerda, direita)

            if not operador2 in TABELA_OPERACOES:
                return False, f"Operador {operador} nao encontrado na tabela de expressoes"
            
            if not esquerda.tipo in TABELA_OPERACOES[operador2]:
                return False, f"Operacao {operador} nao permitida para o tipo {esquerda.tipo}"
            
            if not direita.tipo in TABELA_OPERACOES[operador2][esquerda.tipo]:
                return False, f"Operacao {operador} nao permitida entr os tipos {esquerda.tipo} e {direita.tipo}"
            
            
            return self.calcula_expressao(no)
