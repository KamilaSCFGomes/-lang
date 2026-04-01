# 😎lang
Este é um trabalho avaliativo para disciplina de compiladores. Um compilador para uma linguagem exotérica, 😎lang.

## Estruturas de dados

A palavra que forma a declaração de uma variável se inicia em `📦`, que  indica a declaração de uma variável. Em seguida, pode ser incluído `🤏`, que indica que é uma variação pequena daquele tipo. E por fim,`🔢` indica que é algum tipo de numeral, `🔤` indica que é algum tipo de texto e `🔘` indica que é tipo booleano. As palavras finais ficam assim:

`📦🔢` ➡️ Variável de tipo inteiro

`📦🤏🔢` ➡️ Variável de tipo float

`📦🔤` ➡️ Variável de tipo string

`📦🤏🔤` ➡️ Variável de tipo caracter

`📦🔘` ➡️ Variável de tipo booleano

## Representação de dados

### Tipos numéricos

Valores numéricos podem ser formados por uma combinação de qualquer quantidade de algarismos numéricos em emoji, além de poder incluir 1 ponto em qualquer posição (incluindo na primeira ou última posição) e poder ser iniciado em menos para represnetar um valor negativo.

- Algarismos numéricos: `0️⃣`, `1️⃣`, `2️⃣`, `3️⃣`, `4️⃣`, `5️⃣`, `6️⃣`, `7️⃣`, `8️⃣`, `9️⃣`

- Ponto: `⏺️`

- Menos: `➖`

*Exemplos de valores válidos:* `2️⃣5️⃣` (25), `8️⃣⏺️9️⃣4️⃣` (8.94), `⏺️7️⃣2️⃣3️⃣` (0.723)


### Tipos de texto

O início e o fim de um valor de texto são demarcador por um balão de fala: `💬`. Dentro disso, pode conter qualquer coisa, incluindo quebra de linha. (Exceto outro balão de fala, já que isso demarca o fim do valor)

*Exemplos de valores válidos:* `💬B💬`, `💬Texto💬`, `💬😎✨💬`

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

Tudo o que é escrito após o marcador de fim de código (`🏁`) é ignorado, e então pode ser considerado como comentário.