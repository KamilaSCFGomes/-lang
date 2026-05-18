import lexer as le
import sintatico as si

with open('exemplo.😎', 'r') as f:
    
    print("\t\tANALISE LÉXICA:")
    print("CLASSE,\t\tTIPO,\tTOKEN,\tLINHA, COLUNA")
    lexer = le.Lexer(f.read())
    lexer.analiseLexica()

    lexer.imprimirTokens()
    lexer.imprimeErroSeTiver()

    print("\n\n")

    print("\t\tANALISE SINTÁTICA:")
    parser = si.Sintatico(lexer.retornaTokens())
    sucesso = parser.analiseSintatica()
    print(parser.analise)
