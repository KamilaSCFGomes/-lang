import re

def ehNumero(numero):
    try:
        int(numero)
        return True
    except ValueError:
        return False


OPERADORES = {
    "➕" : [11, "MAIS"],
    "➖" : [12, "MENOS"],
    "✖️" : [13, "VEZES"],
    "➗" : [14, "DIVIDIDO"],
    "〰️" : [15, "RESTO"],
    "↗️" : [16, "POTENCIA"],
    "🟰" : [17, "IGUAL"],
    "⬆️" : [18, "MAIOR"],
    "⬇️" : [19, "MENOR"],
    "🚫" : [20, "NAO"],
    "🤞" : [21, "AND"],
    "✌️" : [22, "OR"],
    "❔" : [23, "TERNARIO1"],
    "❕" : [24, "TERNARIO2"],
    "👉" : [25, "ATRIBUICAO"]
}

SEPARADORES = {
    "(" : [30, "ABRE_PARENTESES"],
    ")" : [31, "FECHA_PARENTESES"],
    "{" : [32, "ABRE_CHAVE"],
    "}" : [33, "FECHA_CHAVE"],
    ":" : [34, "DOIS_PONTOS"]
}

ESPACOS = {
    "\n" : [35, "ENTER"],
    "\t" : [36, "TAB"],
    " " : [37, "ESPACO"]
}

COMENTARIOS = {
    "💭" : [40, "COMENTARIO_CURTO"],
    "🫃" : [41, "ABRE_COMENTARIO_LONGO"],
    "👶" : [42, "FECHA_COMENTARIO_LONGO"]
}

LITERAIS = {
    "💬" : [43, "TEXTO"],
    "⏺️" : [44, "NUMERAL"],
}

BOOLEANO = {
    "⭕" : [45, "VERDADEIRO"],
    "❌" : [46, "FALSO"]
}

PALAVRAS_RESERVADAS = {
    "🚀" : [50, "INICIO"],
    "🏁" : [51, "FIM"],
    "❓" : [52, "IF"],
    "⁉️" : [53, "ELIF"],
    "❗" : [54, "ELSE"],
    "📦🔢" : [55, "INT"],
    "📦🤏🔢" : [56, "FLOAT"],
    "📦🔤" : [57, "STRING"],
    "📦🤏🔤" : [58, "CHAR"],
    "📦🔘" : [59, "BOOLEANO"],
    "🔁" : [60, "FOR"],
    "⏹️" : [61, "BREAK"],
    "▶️" : [62, "CONTINUE"],
    "🖨️" : [63, "PRINT"],
    "🎤" : [64, "SCAN"],
    "🧩" : [65, "FUNCAO"],
    "🔙" : [66, "RETURN"]
}

ALGARISMOS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "⏺️"]

class Token:
    def __init__(self, codigo, token, classe, linha, coluna):
        self.codigo = codigo
        self.token = token
        self.classe = classe
        self.linha = linha
        self.coluna = coluna

    def representa(self):
        return f"{self.codigo},\t{self.token}, {self.classe},\t{self.linha}, {self.coluna}"

class Ponteiro:
    def __init__(self, posicao=0, linha=1, coluna=1):
        self.posicao=0
        self.linha=1
        self.coluna=1

    def avancar(self):
        self.posicao+=1
        self.coluna+=1
    
    def proximaLinha(self):
        self.coluna=0
        self.linha+=1

    def copiaPonteiro(self, ponteiro):
        self.posicao = ponteiro.posicao
        self. linha = ponteiro.linha
        self.coluna = ponteiro.coluna

class Lexer:
    def __init__(self, codigo):
        self.pivo = Ponteiro()
        self.batedor = Ponteiro()
        self.codigo = codigo
        self.tokens = []
    
    def retornaTokens(self):
        return self.tokens
    
    def adicionaErro(self, tipo="ERRO LEXICO NAO ESPECIFICADO"):
        self.adicionaToken(0, tipo, "ERRO", self.pivo.linha, self.pivo.coluna)
    
    def imprimeErroSeTiver(self):
        if len(self.tokens)>0 and self.tokens[-1].codigo == 0:
            print("⚠️  Erro!⚠️   ", self.tokens[-1].token, " 📍 ↔️ ", self.tokens[-1].linha, ",↕️ ", self.tokens[-1].coluna)

    def fimDoArquivo(self):
        return self.batedor.posicao >= len(self.codigo)
    
    def tokenFinal(self):
        if self.codigo[self.batedor.posicao] == "🏁":
            self.adicionaToken(0, "🏁", "FIM", self.pivo.linha, self.pivo.coluna)
            return True
        return False

    def adicionaToken(self, codigo, token, classe, linha, coluna):
        self.tokens.append(Token(codigo, token, classe, linha, coluna))
        # print(self.tokens[-1].representa())

    def traduzNumeral(self, texto):
        final=0
        casasDecimais=0
        decimalJaFoi=False # só permite 1 ponto

        if(len(texto)<=0):
            return None
        
        while ehNumero(texto[0]) and int(texto[0]) == 0: #ignora 0 à esquerda
            texto=texto[3:]

        while True:
            if len(texto)<=0:
                break 

            if texto[0]=='⏺':
                if decimalJaFoi: # se tiver 2 pontos está mal formado
                    self.adicionaErro("NUMERAL MAL FORMADO")
                    return None
                decimalJaFoi=True
                texto=texto[2:]
                casasDecimais=0
            
            elif ehNumero(texto[0]):
                final*=10
                final += int(texto[0])
                texto = texto[3:]
               
                casasDecimais +=1

            else:
                break

        if casasDecimais>=1 and decimalJaFoi:
            final = final/(10**casasDecimais)
        return final
    
    def resolveNumeral(self, token):
        # confere se comeca com número
        if re.match('^(0️⃣|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣|⏺️)+', token) == None:
            return False

        # confere se é um número bem formado   
        if re.match('^(0️⃣|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣)*(⏺️)?(0️⃣|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|8️⃣|9️⃣)+$', token) == None:
            self.adicionaErro("NUMERO MAL FORMADO")
            return True
        
        # começa com numero mas não está bem formado
        numero=self.traduzNumeral(token)
        self.adicionaToken(44, numero, "NUMERAL", self.pivo.linha, self.pivo.coluna)
        return True

    def resolveComentarios(self):
        if(self.codigo[self.batedor.posicao]=="💭"):
            while(self.codigo[self.batedor.posicao]!='\n'):
                self.batedor.avancar()

            self.batedor.proximaLinha()

            # print(f"comentario: [{self.codigo[self.pivo.posicao:self.batedor.posicao]}]")
            self.pivo.copiaPonteiro(self.batedor)
            return True
        
        elif(self.codigo[self.batedor.posicao]=="🫃"):
            while(self.codigo[self.batedor.posicao]!='👶'):

                if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()
                self.batedor.avancar()
                
                if self.fimDoArquivo():
                    self.adicionaErro("COMENTARIO LONGO NAO FECHADO")
                    return True

            self.batedor.avancar()
            if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()
            # print(f"comentario: [{self.codigo[self.pivo.posicao:self.batedor.posicao]}]")
            self.pivo.copiaPonteiro(self.batedor)
            return True
        
        else:
            return False
        
    def resolveTexto(self):
        if(self.codigo[self.batedor.posicao]=="💬"):
            self.batedor.avancar()

            while(self.codigo[self.batedor.posicao]!='💬'):

                if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()
                
                self.batedor.avancar()                 

                if self.fimDoArquivo():
                    self.adicionaErro("STRING NAO FECHADA")
                    return True

            self.batedor.avancar()
            if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()

            self.adicionaToken(43, self.codigo[self.pivo.posicao:self.batedor.posicao], "TEXTO", self.pivo.linha, self.pivo.coluna)
            self.pivo.copiaPonteiro(self.batedor)
            return True

        else:
            return False

    def resolveEspacos(self):
        if ESPACOS.get(self.codigo[self.batedor.posicao]) != None:

            if self.codigo[self.batedor.posicao] == '\n':
                self.batedor.proximaLinha()
                            
            self.pivo.copiaPonteiro(self.batedor)

            return True
        return False

    def batedorEmClasse(self, CLASSE):
        return CLASSE.get(self.codigo[self.batedor.posicao])

    def verificaPalavrasReservadas(self, token):
        resultado = PALAVRAS_RESERVADAS.get(token)
        if resultado!=None:
            self.adicionaToken(resultado[0], token, resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False

    def verificaOperadores(self, token):
        resultado = OPERADORES.get(token)
        if resultado!=None:
            self.adicionaToken(resultado[0], token, resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False
    
    def verificaBooleano(self, token):
        resultado = BOOLEANO.get(token)
        if resultado!=None:
            self.adicionaToken(resultado[0], token, resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False

    def proximoToken(self):
        while not self.fimDoArquivo() and not (self.batedorEmClasse(ESPACOS) or self.batedorEmClasse(SEPARADORES)):
            self.batedor.avancar()

        if not self.fimDoArquivo() and self.codigo[self.batedor.posicao] == '\n':
            self.batedor.proximaLinha()

        token = self.codigo[self.pivo.posicao:self.batedor.posicao]
        return token
        
    def resolveSeparadores(self):
        resultado = SEPARADORES.get(self.codigo[self.batedor.posicao])
        if resultado == None:
            return False
        
        self.adicionaToken(resultado[0], self.codigo[self.batedor.posicao], resultado[1], self.batedor.linha, self.batedor.coluna)
        self.pivo.copiaPonteiro(self.batedor)
        return True
    
    def separaProximoToken(self):
        while True:
            if self.fimDoArquivo():
                return True
            
            if ESPACOS.get(self.codigo[self.batedor.posicao]) != None and SEPARADORES.get(self.codigo[self.batedor.posicao]) != None:
                return

    def resolveIdentificador(self, token):
      
        if len(token)>0:
            self.adicionaToken(45, token, "IDENTIFICADOR", self.pivo.linha, self.pivo.coluna)
            return True
        
        return False
    
    def detectarToken(self):

        if self.resolveEspacos(): return True
        
        # tokens com limite bem definido:
        if self.resolveComentarios(): return True
        if self.resolveSeparadores(): return True
        if self.resolveTexto(): return True

        # tokens com limite variavel
        token = self.proximoToken()
        if self.verificaOperadores(token): return True
        if self.verificaBooleano(token): return True
        if self.verificaPalavrasReservadas(token): return True
        if self.resolveNumeral(token): return True

        if(len(token)>0):
            self.adicionaToken(45, token, "IDENTIFICADOR", self.pivo.linha, self.pivo.coluna)
            return True
        
        self.adicionaErro("TOKEN MAL FORMADO")
        return False # tipo nao identificado, token mal formado

    def analiseLexica(self):
        while True:
            if(self.fimDoArquivo()):
                break

            # se um token foi encontrado, retorna true
            sucesso = self.detectarToken()

            if len(self.tokens)>0:
                # se o ultimo token for um erro
                if self.tokens[-1].codigo == 0:
                    return False
                
                # se o ultimo token for o fim do codigo
                if self.tokens[-1].codigo == 51:
                    return True
            
            if not sucesso:
                self.adicionaErro("TOKEN MAL FORMADO")
                return False
            
            self.batedor.avancar()
            self.pivo.copiaPonteiro(self.batedor)
        
        # se rodou sem erros até o fim
        return True
    
    def imprimirTokens(self):
        for i in self.tokens:
            print(i.representa())


with open('exemplo.😎', 'r') as f:
    lexer = Lexer(f.read())
    lexer.analiseLexica()
    
    print("COD,\tTOKEN,\tTIPO,\tLINHA,\tCOLUNA")
    lexer.imprimirTokens()
    
    lexer.imprimeErroSeTiver()