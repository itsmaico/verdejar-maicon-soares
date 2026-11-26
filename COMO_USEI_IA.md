# Como usei a I.A.

Fiz o uso da IA `(Claude, Gemini e Chatgpt)` principalmente para tratar assuntos em que não dominava, pedi explicação e auxilio de como aplicar meus objetivos frente a problemas apresentados, como irei descrever nas próximas etapas.  Também utilizei para organização e realização de documentação, para que a estrutura do texto ficasse agradável e formatada.

# Sugestões aceitas

- Usar arquivo `.env` para evitar expor credencias no código, foi uma boa sugestão pois consegui resolver também o problema de direcionamento de porta para o postgre no docker com a variável dentro do arquivo;
- Implementar `dotenv` e `load_dotenv` no código de teste de reconciliação, o mesmo retornava erro de credencial em primeiro momento, após corrigir ficou retornando erro de conexão e resolvi apenas implementando a primeira sugestão com essa segunda também. Fazendo o direcionamento para a porta configurada no postgre docker.

# Sugestões rejeitadas

- As consultas SQL estavam retornando, onde tinha data, o horário também e não era necessário, perguntei a IA como podia resolver e ela me indicou usar TO_CHAR ao inves de DATE_TRUNC. Achei esquisito mudar a função e pesquisando lembrei da aula de SQL da trilha onde dizia que para remover hora, basta usar ::date ao final da consulta para formatar para data apenas;
- Pedi auxilio para montar a função de extração de rota HTTP, por não saber sobre, e a IA me retornou uma função com a biblioteca `requests` sem me avisar da necessidade de instala-la, por ser externa. Pesquisei novamente e resolvi usar a biblioteca padrão `urllib` mesmo que `requests` fosse menor no código, com auxilio da IA mudei as funções onde tinha `requests` pela `urllib` .

# Falhas e retrabalho

- Ao montar o README com textos e códigos soltos no arquivo, pedi a IA para organizar tudo em um arquivo só, ja formatado. No geral funcionou mas por algum motivo onde havia underline “_” a IA colocou uma barra na frente “\”. Transformando o nome “__init__.py” em “\_\_init\_\_.py”. Para evitar novos erros da IA, corrigi linha por linha do readme;
- Na etapa de usar pytest, segui parte da documentação do desafio mas tive problemas para fazer funcionar no meu VScode, recorri a IA para identificar o problema e ela insistiu em fazer novas instalações e modificar o caminho de execução do python, até fiz algumas etapas mas nada resolveu, tive que perguntar a outras IAs como resolver sem alterar caminhos e cheguei a solução de utilizar a flag de módulo `-m` para fazer o pytest rodar no meu terminal.