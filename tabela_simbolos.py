TIPOS = {"INT", "FLOAT", "STRING", "CHAR", "BOOLEANO"}

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
        self.escopo_atual = 0
        self.escopo_com_loop = 0
        self.tabela = {}

    def adiciona_variavel(self, nome, categoria, tipo, pos):
        if self.tabela[nome]:
            return False, f"Declaracao duplicada. {nome} ja foi declarado como {tabela[nome]['categoria']} {tabela[nome]['tipo']} em {tabela[nome]['pos']}"
        
        self.tabela[nome] = {"tipo": tipo, "categoria": categoria, "pos": pos, "escopo": escopo_atual, "utilizada": False}
        return True, ""
    
    def adiciona_funcao(nome, categoria, params, tipo, pos):
        if self.tabela[nome]:
            return False, f"Declaracao duplicada. {nome} ja foi declarado como {tabela[nome]['categoria']} {tabela[nome]['tipo']} em {tabela[nome]['pos']}"
        
        self.tabela[nome] = {"tipo": tipo, "categoria": categoria, "params": params, "pos": pos, "escopo": escopo_atual, "utilizada": False}
        return True, ""
    

    def verifica_variavel(nome):
        try:
            if self.tabela[nome]['categoria'] == "VARIAVEL":
                return True, self.tabela[nome]['tipo']
            else:
                return False, f"esperava VARIAVEL, mas {nome} foi declarado como {self.tabela[nome]['categoria']} em {self.tabela[nome]['pos']}"
        except:
            return False, f"Variavel {nome} nao declarada"
    
    def verifica_funcao(nome, params):
        try:
            if self.tabela[nome]['categoria'] == "FUNCAO":
                for p in params:
                    print("parametro:", p)
                return True, self.tabela[nome]['tipo']
            else:
                return False, f"esperava FUNCAO, mas {nome} foi declarado como {self.tabela[nome]['categoria']} em {self.tabela[nome]['pos']}"
        except:
            return False, f"Funcao {nome} nao declarada"
    
    
    def abrir_escopo(self, loop=False):
        self.escopo_atual += 1
        if loop: self.escopo_com_loop += 1

    def fechar_escopo(self, loop=False):
        warnings = []

        for variavel in self.tabela:
            print("v:", variave['nome'], "esc:", variavel['escopo'])
            if variavel['escopo'] >= self.escopo_atual:
                if not variavel['utilizada']:
                    warnings.append(f"Variavel nao utilizada: {variavel['nome']}, declarada em {variavel['pos']}")
                print('removida')
                self.tabela.pop(variavel)

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
            a, b = self.verifica_variavel(v)
            if not a: return a, b
            tipos.append(v['tipo'])

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