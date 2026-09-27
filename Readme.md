# PROJETO ZAPPER (1986)
## Da Engenharia de Baixo Nível no CP 500 à Emulação Moderna em Python
---

### 1. Contexto Histórico e Autoria
* **Nome do Software:** ZAPPER / BAS (Vs 1.3)
* **Plataforma Original:** Linha TRS-80 / CP 500 (Monitores de fósforo verde)
* **Sistemas Operacionais da Época:** TRSDOS / NEWDOS
* **Ano de Publicação:** Dezembro de 1986 (Revista Micro Sistemas)
* **Autor e Programador:** Carlos Choia
* **Conselheiro e Incentivador:** Sven Bleckwedel
* **Colaborador de Restauração:** Google Gemini

O Zapper nasceu da necessidade avançada da comunidade de tecnologia do Brasil nos anos 80 de ler, analisar e alterar trilhas e setores físicos diretamente nos disquetes de 5¼ polegadas, superando limitações nativas do sistema operacional.

---

### 2. Destaques da Engenharia de Software Original
Para alcançar a performance e o acesso direto ao hardware exigidos pelo utilitário, o programa utilizou uma arquitetura híbrida avançada para a época:
* **Interface e Navegação:** Escrita em BASIC clássico, utilizando comandos de posicionamento físico de tela como `PRINT@` e controle estrito de fluxo por indentação compacta via dois pontos (`:`).
* **Injeção de Código de Máquina:** Opcodes decimais específicos do processador **Zilog Z80** eram armazenados em blocos `DATA` e injetados diretamente na memória RAM física da máquina através de comandos `POKE`.
* **Chamadas de Kernel Residencial:** O desvio de fluxo para rotinas rápidas de leitura e escrita física de trilhas e setores era feito através das funções de desvio `DEFUSR0`, `DEFUSR1` e `DEFUSR2`.

---
