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
    'MENOR':'IGUAL',
    'AND':'AND',
    'OR':'AND',
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
        if nome in self.tabela:
            return False, f"Declaracao duplicada. {nome} ja foi declarado como {self.tabela[nome]['categ']} {self.tabela[nome]['tipo']} em {self.tabela[nome]['pos']}"
        
        self.tabela[nome] = {"tipo": tipo, "categ": categ, "params": params, "valor": False, "pos": pos, "escopo": self.escopo_atual, "usada": False}
        print(nome, "ADICIONADA!!!")
        self.imprimir_tabela()
        return True, ""
    

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
                
    

    def verifica_variavel(self, nome):
        if isinstance(nome, ast.Identificador):
            nome = nome.nome
        try:
            print(nome, self.tabela[nome])
            if self.tabela[nome]['categ'] == "VARIAVEL":
                self.tabela[nome]['usada'] = True
                return True, self.tabela[nome]['tipo']
            else:
                return False, f"esperava VARIAVEL, mas {nome} foi declarado como {self.tabela[nome]['categ']} em {self.tabela[nome]['pos']}"
        except:
            return False, f"Variavel {nome} nao declarada"
    
    def verifica_funcao(self, nome, params):
        try:
            if self.tabela[nome]['categ'] == "FUNCAO":
                for p in params:
                    print("parametro:", p)
                return True, self.tabela[nome]['tipo']
            else:
                return False, f"esperava FUNCAO, mas {nome} foi declarado como {self.tabela[nome]['categ']} em {self.tabela[nome]['pos']}"
        except:
            return False, f"Funcao {nome} nao declarada"
    
    
    def abrir_escopo(self, loop=False):
        print(f"escopo: {self.escopo_atual} -> {self.escopo_atual+1}")
        self.escopo_atual += 1
        if loop: self.escopo_com_loop += 1

    def fechar_escopo(self, loop=False):
        warnings = []
        print(f"escopo: {self.escopo_atual} -> {self.escopo_atual-1}")

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


    def verifica_operacao_variaveis(self, operador, variaveis):
        tipos = []
        for v in variaveis:
            if isinstance(v, ast.Identificador):
                v = v.nome
            a, b = self.verifica_variavel(v)
            if not a: return a, b
            tipos.append(self.tabela[v]['tipo'])
            self.tabela[v]['usada'] = True

        return self.verifica_operacao_tipos(operador, tipos)
    
    def verifica_operacao_tipos(self, operador, tipos):
        if operador=="NAO":
            if tipos != "BOOLEANO":
                return False, f"Esperava BOOLEANO para operador {operador}, recebeu {tipos}"
            return True, "BOOLEANO"

        if operador=="ATRIBUICAO":
            if tipos[0] != tipos[1]:
                return False, f"Esperava tipos iguais para operador {operador}, recebeu {tipos}"
            return True, tipos[0]

        operador = OPERACOES_SEMELHANTES[operador]

        try:
            return True, TABELA_OPERACOES[operador][tipos[0]][tipos[1]]
        except:
            return False, f"Operacao {operador} nao permitida entre os tipos {tipos} ou ainda nao implementada"

        
    def verifica_break_continue(self):
        if self.escopo_com_loop <= 0:
            return False, f"Comando break/continue encontrado fora de estrutura de repeticao"
        else: return True, ""

    def atribuicao(self, nome, valor):

        if isinstance(nome, ast.Identificador):
            nome = nome.nome
        sucesso, tipo = self.verifica_variavel(nome)

        print(sucesso, tipo)

        if not sucesso:
            return sucesso, tipo

        if isinstance(valor, ast.Numero) and (tipo == "INT" or tipo == "FLOAT"):
            self.tabela[nome]['valor'] = valor.valor

        elif isinstance(valor, ast.String) and (tipo == "CHAR" or "STRING"):
            self.tabela[nome]['valor'] = valor.valor
        
        else:
            sucesso, tipo = self.resolve_operacao(valor)
            if not sucesso: return sucesso, tipo
            
        return True, ''

    def resolve_operacao(self, no):
        if isinstance(no, ast.OperacaoTer):
            return True, no
        
        if isinstance(no, ast.OperacaoBin):
            pos = no.pos
            operador = no.operador
            esquerda = no.esquerda
            direita = no.direita
            
            sucesso, tipo = self.verifica_operacao_variaveis(operador, [esquerda, direita])
            if not sucesso: return sucesso, tipo
            
            if isinstance(esquerda, ast.Numero): esquerda = no.esquerda.valor
            if isinstance(direita, ast.Numero): direita = no.direita.valor
            
            if operador=="ATRIBUICAO":
                return self.atribuicao(esquerda, direita)
            
            if operador=="MAIS":
                if isinstance(esquerda, ast.Numero) and isinstance(direita, ast.Numero):
                    return sucesso, ast.Numero(esquerda.valor+direita.valor, pos)
                else:
                    no.tipo = tipo
                    return sucesso, no
                
            return False, "nao sei"