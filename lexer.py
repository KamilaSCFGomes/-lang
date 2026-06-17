import re
from token_classe import Token

def ehNumero(numero):
    try:
        int(numero)
        return True
    except ValueError:
        return False


OPERADORES = {
    "➕" : ["OPERADOR", "MAIS"],
    "➕➕" : ["OPERADOR", "MAIS_MAIS"],
    "➕👉" : ["OPERADOR", "MAIS_IGUAL"],
    "➖" : ["OPERADOR", "MENOS"],
    "➖➖" : ["OPERADOR", "MENOS_MENOS"],
    "➖👉" : ["OPERADOR", "MENOS_IGUAL"],
    "✖️" : ["OPERADOR", "VEZES"],
    "✖️👉" : ["OPERADOR", "VEZES_IGUAL"],
    "➗" : ["OPERADOR", "DIVIDIDO"],
    "➗👉" : ["OPERADOR", "DIVIDIDO_IGUAL"],
    "〰️" : ["OPERADOR", "RESTO"],
    "↗️" : ["OPERADOR", "POTENCIA"],
    "↗️👉" : ["OPERADOR", "POTENCIA_IGUAL"],
    "🟰" : ["OPERADOR", "IGUAL"],
    "🚫🟰" : ["OPERADOR", "DIFERENTE"],
    "⬆️" : ["OPERADOR", "MAIOR"],
    "⬆️🟰" : ["OPERADOR", "MAIOR_IGUAL"],
    "⬇️" : ["OPERADOR", "MENOR"],
    "⬇️🟰" : ["OPERADOR", "MENOR_IGUAL"],
    "🚫" : ["OPERADOR", "NAO"],
    "🤞" : ["OPERADOR", "AND"],
    "✌️" : ["OPERADOR", "OR"],
    "❔" : ["OPERADOR", "TERNARIO1"],
    "❕" : ["OPERADOR", "TERNARIO2"],
    "👉" : ["OPERADOR", "ATRIBUICAO"],
    "💪🔢" : ["OPERADOR", "CAST_INT"],
    "💪🤏🔢" : ["OPERADOR", "CAST_FLOAT"],
    "💪🔤" : ["OPERADOR", "CAST_STRING"],
    "💪🤏🔤" : ["OPERADOR", "CAST_CHAR"],
    "💪🔘" : ["OPERADOR", "CAST_BOOLEANO"]
}

SEPARADORES = {
    "(" : ["SEPARADOR", "ABRE_PARENTESES"],
    ")" : ["SEPARADOR", "FECHA_PARENTESES"],
    "{" : ["SEPARADOR", "ABRE_CHAVE"],
    "}" : ["SEPARADOR", "FECHA_CHAVE"],
    ":" : ["SEPARADOR", "DOIS_PONTOS"],
    ";" : ["SEPARADOR", "PONTO_VIRGULA"],
    "," : ["SEPARADOR", "VIRGULA"]
}

ESPACOS = {
    "\n" : ["ESPACO", "ENTER"],
    "\t" : ["ESPACO", "TAB"],
    " " : ["ESPACO", "ESPACO"]
}

COMENTARIOS = {
    "💭" : ["COMENTARIO", "COMENTARIO_CURTO"],
    "🫃" : ["COMENTARIO", "ABRE_COMENTARIO_LONGO"],
    "👶" : ["COMENTARIO", "FECHA_COMENTARIO_LONGO"]
}

LITERAIS = {
    "💬" : ["LITERAL", "TEXTO"],
    "⏺️" : ["LITERAL", "NUMERAL"],
}

BOOLEANO = {
    "⭕" : ["LITERAL", "BOOLEANO"],
    "❌" : ["LITERAL", "BOOLEANO"]
}

PALAVRAS_RESERVADAS = {
    "🚀" : ["PAL_RESERVADA", "INICIO"],
    "🏁" : ["PAL_RESERVADA", "FIM"],
    "❓" : ["PAL_RESERVADA", "IF"],
    "⁉️" : ["PAL_RESERVADA", "ELIF"],
    "❗" : ["PAL_RESERVADA", "ELSE"],
    "📦🔢" : ["PAL_RESERVADA", "INT"],
    "📦🤏🔢" : ["PAL_RESERVADA", "FLOAT"],
    "📦🔤" : ["PAL_RESERVADA", "STRING"],
    "📦🤏🔤" : ["PAL_RESERVADA", "CHAR"],
    "📦🔘" : ["PAL_RESERVADA", "BOOLEANO"],
    "🔁" : ["PAL_RESERVADA", "FOR"],
    "⏹️" : ["PAL_RESERVADA", "BREAK"],
    "▶️" : ["PAL_RESERVADA", "CONTINUE"],
    "🖨️" : ["PAL_RESERVADA", "PRINT"],
    "🎤" : ["PAL_RESERVADA", "SCAN"],
    "🧩" : ["PAL_RESERVADA", "FUNCAO"],
    "🔙" : ["PAL_RESERVADA", "RETURN"]
}

ALGARISMOS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "⏺️"]

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
    
    def adicionaErro(self, token="ERRO LEXICO NAO ESPECIFICADO"):
        self.adicionaToken(token, "ERRO", "ERRO", self.pivo.linha, self.pivo.coluna)
    
    def imprimeErroSeTiver(self):
        if len(self.tokens)>0 and self.tokens[-1].classe == "ERRO":
            print("⚠️  Erro!⚠️   ", self.tokens[-1].token, " 📍 ↔️ ", self.tokens[-1].linha, ",↕️ ", self.tokens[-1].coluna)

    def fimDoArquivo(self):
        return self.batedor.posicao >= len(self.codigo)

    def adicionaToken(self, token, classe, tipo, linha, coluna):
        self.tokens.append(Token(token, classe, tipo, linha, coluna))
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
        self.adicionaToken(numero, "LITERAL", "NUMERAL", self.pivo.linha, self.pivo.coluna)
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

            self.adicionaToken(self.codigo[self.pivo.posicao:self.batedor.posicao], "LITERAL", "TEXTO", self.pivo.linha, self.pivo.coluna)
            self.batedor.posicao-=1
            self.batedor.coluna-=1
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
            self.adicionaToken(token, resultado[0], resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False

    def verificaOperadores(self, token):
        resultado = OPERADORES.get(token)
        if resultado!=None:
            self.adicionaToken(token, resultado[0], resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False
    
    def verificaBooleano(self, token):
        resultado = BOOLEANO.get(token)
        if resultado!=None:
            self.adicionaToken(token=="⭕", resultado[0], resultado[1], self.pivo.linha, self.pivo.coluna)
            return True

        return False

    def proximoToken(self):
        while True:
            if self.fimDoArquivo() or self.batedorEmClasse(ESPACOS):
                token = self.codigo[self.pivo.posicao:self.batedor.posicao]
                break
            
            if self.batedorEmClasse(SEPARADORES) or self.codigo[self.batedor.posicao]=='💬':
                token = self.codigo[self.pivo.posicao:self.batedor.posicao]
                self.batedor.posicao-=1
                self.batedor.coluna-=1
                break

            self.batedor.avancar()

        if not self.fimDoArquivo() and self.codigo[self.batedor.posicao] == '\n':
            self.batedor.proximaLinha()            

        return token
        
    def resolveSeparadores(self):
        resultado = SEPARADORES.get(self.codigo[self.batedor.posicao])
        if resultado == None:
            return False
        
        self.adicionaToken(self.codigo[self.batedor.posicao], resultado[0], resultado[1], self.batedor.linha, self.batedor.coluna)
        self.pivo.copiaPonteiro(self.batedor)
        return True

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
            self.adicionaToken(token, "IDENTIFICADOR", "IDENTIFICADOR", self.pivo.linha, self.pivo.coluna)
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
                if self.tokens[-1].classe == "ERRO":
                    return False
                
                # se o ultimo token for o fim do codigo
                if self.tokens[-1].tipo == "FIM":
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