import lexer as le
import sintatico_semantico as si

with open('exemplo.😎', 'r') as f:
    
    print("\t\tANALISE LÉXICA:")
    print("CLASSE,\t\tTIPO,\tTOKEN,\tLINHA, COLUNA")
    lexer = le.Lexer(f.read())
    lexer.analiseLexica()

    lexer.imprimirTokens()
    lexer.imprimeErroSeTiver()

    print("\n\n")

    print("\t\tANALISE SINTÁTICA/SEMÂNTICA:")
    parser = si.Sintatico(lexer.retornaTokens())
    sucesso = parser.analiseSintatica()

    parser.imprimeArvore()
    print("\n")
    parser.imprimeErros()
    parser.imprimeWarnings()
    print(f"\n\nSucesso: {"Sim" if sucesso else "Não"}\n")