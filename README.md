# 😎lang

Este é um trabalho avaliativo desenvolvido para disciplina de compiladores. Um compilador para uma linguagem exotérica de emojis, a 😎lang.

# Sobre o compilador

## Lexer

O lexer foi implementado com ponteiros pivô e batedor manuais. Foi utilizado regex para varificar a validade de números escritos utilizando emojis. Todo o resto das verificações foi feito manualmente. Comentários são descartados já nessa etapa.

### Ordem de verificação

- Tipos com limites bem definidos - possuem 1 caracter de comprimento ou possuem um caracter específico para delimitar o início e o fim:

1. Espaços
2. Comentários
3. Separadores
4. Texto

- Tipos que podem ter comprimento variável - os ponteiros copiam o token até atingir um espaço ou um separador, e em seguida o lexer tenta classificar:

5. Operadores
6. Booleanos
7. Palavras Reservadas
8. Numeral
9. Identificadores

### Desafios

Alguns emojis são formados por 2 ou 3 caracteres, incluindo caracteres invisíveis, então analisar caracter por caracter é complicado em algumas situações. Por esse motivo, para a maioria de tipos de token, é necessários separá-los por espaços, pelo menos por enquanto. Quero tentar resolver essa situação posteriormente.

# Sobre a linguagem

## Formato do arquivo

O arquivo escrito deve ter extensão .😎

Quando escrever um código na linguagem 😎lang, inicie com `🚀` e finalize com `🏁`. Tudo o que for escrito após o sinalizador de fim de código será ignorado.

## Estruturas de dados

A palavra que forma a declaração de uma variável se inicia em `📦`, que  indica a declaração de uma variável. Em seguida, pode ser incluído `🤏`, que indica que é uma variação pequena daquele tipo. E por fim,`🔢` indica que é algum tipo de numeral, `🔤` indica que é algum tipo de texto e `🔘` indica que é tipo booleano. As palavras finais ficam assim:

`📦🔢` ➡️ Variável de tipo inteiro

`📦🤏🔢` ➡️ Variável de tipo float

`📦🔤` ➡️ Variável de tipo string

`📦🤏🔤` ➡️ Variável de tipo caracter

`📦🔘` ➡️ Variável de tipo booleano

## Representação de dados

### Tipos numéricos

Valores numéricos podem ser formados por uma combinação de qualquer quantidade de algarismos numéricos em emoji, além de poder incluir 1 ponto em qualquer posição (excento na última) e poder ser iniciado em menos para represnetar um valor negativo.

- Algarismos numéricos: `0️⃣`, `1️⃣`, `2️⃣`, `3️⃣`, `4️⃣`, `5️⃣`, `6️⃣`, `7️⃣`, `8️⃣`, `9️⃣`

- Ponto: `⏺️`

- Menos: `➖`

*Exemplos de valores válidos:* `2️⃣5️⃣` (25), `8️⃣⏺️9️⃣4️⃣` (8.94), `⏺️7️⃣2️⃣3️⃣` (0.723)


### Tipos de texto

O início e o fim de um valor de texto são demarcador por um balão de fala: `💬`. Dentro disso, pode conter qualquer coisa, incluindo quebra de linha. (Exceto outro balão de fala, já que isso demarca o fim do valor)

*Exemplos de valores válidos:* `💬B💬`, `💬Texto💬`, `💬😎\n✨💬`

### Tipo booleano

Os valores permitidos para este tipo são apenas verdadeiro: `⭕` e falso `❌`

*Valores válidos:* `⭕`, `❌`

## Operadores

`➕` ➡️ Soma

`➖` ➡️ Subtração

`✖️` ➡️ Multiplicação

`➗` ➡️ Divisão

`〰️` ➡️ Resto

`🟰` ➡️ Igualdade

`🚫` ➡️ Diferença

`↗️` ➡️ Potência

`⬆️` ➡️ Maior que

`⬆️🟰` ➡️ Maior ou igual

`⬇️` ➡️ Menor que

`⬇️🟰` ➡️ Menor ou igual

`🚫` ➡️ Negação

`🤞` ➡️ E

`✌️` ➡️ Ou

`👉` ➡️ Atribuição

`❔` e `❕` ➡️ Operador ternário

## Palavras reservadas

`🚀` ➡️ Início do código

`🏁` ➡️ Fim do código

`❓` ➡️ if

`⁉️` ➡️ elif/else if

`❗` ➡️ else

`🔁` ➡️ for

`⏹️` ➡️ break

`▶️` ➡️ continue

`🖨️` ➡️ print

`🎤` ➡️ scan

`🧩` ➡️ definir função

`🔙` ➡️ return

## Comentários

### Comentários curtos

São iniciados com o balão de pensamento: `💭` e finalizam na próxima quebra de linha.

`💭 Este é um comentário curto`

### Comentários longos

São iniciados em `🫃` e finalizados em `👶`.

```
🫃 Este é um 
comentário
longo 👶
```

### Comentários finais

Tudo o que é escrito após o marcador de fim de código (`🏁`) é ignorado, então isso pode ser considerado como um tipo de comentário.