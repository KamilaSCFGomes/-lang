import re

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
    "❔" : [21, "TERNARIO1"],
    "❕" : [22, "TERNARIO2"],
    "👉" : [23, "ATRIBUICAO"]
}

SEPARADORES = {
    "(" : [30, "ABRE_PARENTESES"],
    ")" : [31, "FECHA_PARENTESES"],
    "{" : [32, "ABRE_CHAVE"],
    "}" : [33, "FECHA_CHAVE"]
}

ESPACOS = {
    "\n" : [34, "ENTER"],
    "\t" : [35, "TAB"],
    " " : [36, "ESPACO"]
}

COMENTARIOS = {
    "💭" : [40, "COMENTARIO_CURTO"],
    "🫃" : [41, "ABRE_COMENTARIO_LONGO"],
    "👶" : [42, "FECHA_COMENTARIO_LONGO"]
}

LITERAIS = {
    "💬" : [43, "TEXTO"],
    "⏺️" : [44, "NUMERAL"]
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
        return f"{self.codigo}, {self.token}, {self.classe}, {self.linha}, {self.coluna}"

class Ponteiro:
    def __init__(self, posicao=0, linha=1, coluna=1):
        self.posicao=0
        self.linha=1
        self.coluna=1

    def avancar(self):
        self.posicao+=1
        self.coluna+=1
    
    def proximaLinha(self):
        self.posicao+=1
        self.coluna=1
        self.linha+=1
        print("-linha-")

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
    
    def imprimeErro(self, token):
        if token.codigo == 0:
            print("⚠️  Erro!⚠️   ", token.token, " 📍 ↔️ ", token.linha, ",↕️ ", token.coluna)

    def fimDoArquivo(self):
        return self.batedor.posicao >= len(self.codigo)
    
    def tokenFinal(self):
        if self.codigo[self.batedor.posicao] == "🏁":
            self.adicionaToken(0, "🏁", "FIM", self.pivo.linha, self.pivo.coluna)
            return True
        return False
    
    def lidarComQuebraDeLinha(self):
        if self.codigo[self.batedor] == '\n':
            self.linha==1
            self.coluna+=1
            return True
        return False

    def adicionaToken(self, codigo, token, classe, linha, coluna):
        self.tokens.append(Token(codigo, token, classe, linha, coluna))
        print(self.tokens[-1].representa())

    def traduzNumeral(self, texto):
        final=0
        casasDecimais=0
        decimalJaFoi=False # só permite 1 ponto

        if(len(texto)<=0):
            return None
        
        while texto[0]!='⏺' and int(texto[0]) == 0: #ignora 0 à esquerda
            print("A")
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
                print("zerao")
            
            else:
                final*=10
                final += int(texto[0])
                texto = texto[3:]
               
                print("decimal")
                casasDecimais +=1

        if casasDecimais>=1:
            final = final/(10**casasDecimais)
        print(final)
        return final
    
    def ehNumeral(self):
        # os emojis de numero são compostos por 3 caracteres, exceto o ponto, que é composto por 2 caracteres
        return self.codigo[self.batedor.posicao:self.batedor.posicao+2] in ALGARISMOS or self.codigo[self.batedor.posicao:self.batedor.posicao+1] in ALGARISMOS
    
    def resolveNumeral(self):
        while self.codigo[self.batedor.posicao:self.batedor.posicao+2] in ALGARISMOS or self.codigo[self.batedor.posicao:self.batedor.posicao+1] in ALGARISMOS:
            self.batedor.avancar()
        print("n",self.codigo[self.pivo.posicao:self.batedor.posicao])
        return self.traduzNumeral(self.codigo[self.pivo.posicao:self.batedor.posicao])

    def classificaToken(self):
        texto = self.codigo[self.pivo:self.batedor]
        
        tipo = self.ehNumeral(self, texto)
        if tipo is not None:
            return tipo

        tipo = OPERADORES.get(texto)
        if tipo is not None:
            return tipo
        
        tipo = PALAVRAS_RESERVADAS.get(texto)
        if tipo is not None:
            return tipo
        
        tipo = SEPARADORES.get(texto)
        return tipo

    def resolveComentarios(self):
        if(self.codigo[self.batedor.posicao]=="💭"):
            print("comentario curto: ")
            while(self.codigo[self.batedor.posicao]!='\n'):
                print(self.codigo[self.batedor.posicao], end="")
                self.batedor.avancar()
            self.pivo.copiaPonteiro(self.batedor)
            return True
        
        elif(self.codigo[self.batedor.posicao]=="🫃"):
            print("comentario longo: ")

            while(self.codigo[self.batedor.posicao]!='👶'):
                
                print(self.codigo[self.batedor.posicao], end="")
                if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()
                else:
                    self.batedor.avancar()

                if self.fimDoArquivo():
                    self.adicionaErro("COMENTARIO LONGO NAO FECHADO")
                    return True

            self.batedor.avancar()
            self.pivo.copiaPonteiro(self.batedor)
            return True
        
    def resolveLiteral(self):
        if(self.codigo[self.batedor.posicao]=="💬"):
            print("comentario longo: ")
            self.batedor.avancar()

            while(self.codigo[self.batedor.posicao]!='💬'):
                
                print(self.codigo[self.batedor.posicao], end="")
                if(self.codigo[self.batedor.posicao] == '\n'):
                    self.batedor.proximaLinha()
                else:
                    self.batedor.avancar()

                if self.fimDoArquivo():
                    self.adicionaErro("STRING NAO FECHADA")
                    return True

            self.batedor.avancar()
            self.adicionaToken(43, self.codigo[self.pivo.posicao:self.batedor.posicao], "TEXTO", self.pivo.linha, self.pivo.coluna)
            self.pivo.copiaPonteiro(self.batedor)
            return True
        else: return False

    def resolveNaLista(self, lista, salvarToken=True):
        resultado = lista.get(self.codigo[self.pivo.posicao:self.batedor.posicao])
        print(resultado)
        if resultado == None:
            return False
        if salvarToken:
            self.adicionaToken(resultado[0], self.codigo[self.pivo.posicao:self.batedor.posicao], resultado[1], self.pivo.linha, self.pivo.coluna)
        self.pivo.copiaPonteiro(self.batedor)
        return True
    
    def ehEspaco(self):
        return ESPACOS.get(self.codigo[self.batedor.posicao]) == None

    def ehQuebra(self):
        return self.codigo[self.batedor.posicao] == '\n'

    def resolveEspacos(self):
        if self.ehEspaco():
            if(self.ehQuebra()):
                self.batedor.proximaLinha()
            else:
                self.batedor.avancar()
            self.pivo.copiaPonteiro(self.batedor)
            return True
        return False

    def resolveQuebra(self):
        if(self.codigo[self.pivo.posicao]=='\n'):
            self.batedor.proximaLinha()
            self.pivo.copiaPonteiro(self.batedor)
            return True
        return False

    def batedorEmClasse(self, CLASSE):
        return CLASSE.get(self.codigo[self.batedor.posicao])

    def proximoToken(self):
        while not self.fimDoArquivo() and not (self.batedorEmClasse(ESPACOS) or self.batedorEmClasse(SEPARADORES)):
            self.batedor.avancar()

        token = self.codigo[self.pivo.posicao:self.batedor.posicao-1]
        self.pivo.copiaPonteiro(self.batedor)
        return token

    def ignorarEspaco(self):
        if ESPACOS.get(self.codigo[self.batedor.posicao]) != None:
            print(f"era espaço: [{self.codigo[self.batedor.posicao]}]")
            if self.codigo[self.batedor.posicao]=="\n":
                print("era enter")
                self.batedor.proximaLinha()
            else:
                self.batedor.avancar()
            self.pivo.copiaPonteiro(self.batedor)
        
    def resolveSeparadores(self):
        resultado = SEPARADORES.get(self.codigo[self.batedor.posicao])
        if resultado == None:
            return False
        
        self.adicionaToken(resultado[0], self.codigo[self.batedor.posicao], resultado[1], self.batedor.linha, self.batedor.coluna)
        return True
    
    def separaProximoToken(self):
        while True:
            if self.fimDoArquivo():
                return False
            
            if ESPACOS.get(self.codigo[self.batedor.posicao]) != None:

                return




    def detectarToken(self):
        print(f"[{self.pivo.posicao}-{self.batedor.posicao}] : [{self.codigo[self.pivo.posicao:self.batedor.posicao]}]")
        self.ignorarEspaco()

        # tokens com inicio bem definido:
        if self.resolveComentarios(): return True
        if self.resolveSeparadores(): return True
        if self.resolveLiteral(): return True

        # tokens com inicio variavel:
        if self.resolveNumeral(): return True
        

        
        return True

        """
        print("espaco")
        print(self.codigo[self.pivo.posicao:self.batedor.posicao])
        if self.resolveEspacos(): return True
        print(self.codigo[self.pivo.posicao:self.batedor.posicao])
        print("comentario")
        if self.resolveComentarios(): return True
        print("separador")
        if self.resolveSeparadores(): return True
        print("passou") """
        

        tokenAtual = self.proximoToken()
        print(tokenAtual)

        if self.resolveQuebra(): return True
        
        if self.ehNumeral() and self.resolveNumeral(): return True
        self.adicionaErro()
        return False # tipo nao identificado, token mal formado


    def analiseLexica(self):
        while True:
            if(self.fimDoArquivo() or self.tokenFinal()):
                break

            # se um token foi encontrado, retorna true
            sucesso = self.detectarToken()

            # se o ultimo token for um erro:
            if len(lexer.tokens)>0 and lexer.tokens[-1].codigo == 0:
                return False
            
            if not sucesso:
                self.adicionaErro("TOKEN MAL FORMADO")
                return False
            
            self.batedor.avancar()
        
        # se rodou sem erros até o fim
        return True
    
    def imprimirTokens(self):
        for i in self.tokens:
            print(i.representa())




with open('-lang/exemplo.😎', 'r') as f:
    lexer = Lexer(f.read())
    lexer.analiseLexica()
    
    print("FIM DO LEXER")

    lexer.imprimirTokens()

    if len(lexer.tokens)>0:
        lexer.imprimeErro(lexer.tokens[-1])

    print(lexer.batedor.posicao)