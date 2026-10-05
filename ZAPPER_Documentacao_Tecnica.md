# ZAPPER/BAS — documentação técnica da reconstrução

## Objetivo e preservação

Este documento descreve o comportamento observável em
[`ZAPPER_Reconstruido_Copilot.BAS`](./ZAPPER_Reconstruido_Copilot.BAS), uma
reconstrução identificada no próprio arquivo como parcial e revisada. O
programa declara autoria de Carlos Henrique Choia e Sven Bleckwedel e
referência à revista *Micro Sistemas* nº 63, de dezembro de 1986.

O fonte BASIC deve ser preservado sem alterações. Esta documentação é
complementar: não substitui o artigo original, uma listagem impressa ou a
execução no equipamento e sistema compatíveis. As descrições abaixo distinguem
o que o código mostra daquilo que ainda precisaria ser confirmado em execução.

## Visão geral

O ZAPPER/BAS é um utilitário interativo para selecionar e editar o conteúdo de
setores. A interface é escrita em BASIC; três blocos de bytes Z80 são carregados
na memória e chamados por meio de `USR`. Portanto, a listagem depende de um
ambiente compatível com os comandos BASIC, o mapa de memória, as chamadas do
sistema e o acesso ao disco esperados pelo programa.

O fonte define:

- unidades/“drives” numeradas de 0 a 3;
- trilhas numeradas de 0 a 39;
- setores numerados de 1 a 18;
- um setor apresentado como 16 linhas por 16 posições, isto é, 256 bytes;
- edição em modos decimal, ASCII e gráfico;
- confirmação antes de solicitar a gravação no disco.

Esses limites são as validações implementadas pela listagem; não constituem,
por si só, prova de que toda unidade ou imagem de disco tenha esse formato.

## Fluxo do programa

1. **Inicialização — linhas BASIC 10–80.** Limpa a tela, executa
   `CMD"B","OFF"`, lê os bytes das instruções `DATA`, copia-os para endereços
   de memória e define `USR0`, `USR1` e `USR2`.
2. **Apresentação e seleção — linhas 90–110.** Exibe o título e solicita drive,
   trilha e setor. Se algum valor estiver fora dos limites acima, retorna aos
   campos de seleção.
3. **Leitura/apresentação — linhas 120–150.** Mostra as teclas de operação,
   transfere os parâmetros selecionados para endereços usados pelas rotinas de
   máquina e chama `USR0` e `USR1`. Em seguida mostra a posição e escolhe o modo
   de edição.
4. **Navegação — linhas 160–240.** Aguarda um comando. `-` e `+` mudam um setor;
   ao cruzar o limite de setores, a trilha é ajustada. Nos extremos aceitos,
   esses comandos não avançam além das trilhas 0–39 e setores 1–18.
5. **Edição — linhas 270–540.** Apresenta o setor em uma grade e permite mover o
   cursor e alterar o byte selecionado.
6. **Confirmação — linhas 690–730.** Ao sair do editor pelo comando reconhecido
   como saída, pergunta se deve alterar o disco. `S` segue o caminho de gravação
   implementado; `N` retorna sem seguir esse caminho. Outras respostas são
   ignoradas até que se digite `S` ou `N`.
7. **Encerramento — linha 740.** Executa `CMD"B","ON"`, limpa a tela e termina.

## Teclas conforme o código

### Menu principal

Na linha 150, a cadeia `CM$="-+MXADGF"` associa as teclas às posições do
`ON...GOTO` da linha 180:

| Tecla | Ação observável |
|---|---|
| `-` | Vai ao setor anterior; ao cruzar do setor 1, passa para o setor 18 da trilha anterior, se possível. |
| `+` | Vai ao próximo setor; ao cruzar do setor 18, passa para o setor 1 da trilha seguinte, se possível. |
| `M` | Abre o editor do setor selecionado. |
| `X` | Volta aos campos de drive, trilha e setor para nova seleção. Não há incremento automático de setor nesse caminho. |
| `A` | Seleciona o modo ASCII. |
| `D` | Seleciona o modo decimal. |
| `G` | Seleciona o modo gráfico. |
| `F` | Executa `CMD"B","ON"` e encerra. |

O texto de ajuda da linha 20 chama `X` de “Pula setores”; a implementação
observável da linha 180 o encaminha à seleção das coordenadas. A documentação
registra ambos: o rótulo exibido e o comportamento efetivo no fonte.

### Editor

O texto de ajuda está na linha 30. A rotina do editor lê um valor de
`PEEK(14440)` e compara-o com os valores abaixo. Os nomes das teclas na coluna
“Ajuda” vêm do texto exibido pelo programa; a correspondência física depende do
ambiente original ou de sua configuração no emulador.

| Valor lido | Ação no fonte |
|---:|---|
| 8 | Move uma linha para cima, respeitando o limite superior. |
| 16 | Move uma linha para baixo, respeitando o limite inferior. |
| 1 | Move uma coluna para a esquerda; ao cruzar a margem, passa à linha anterior quando permitido. |
| 64 | Move uma coluna para a direita; ao cruzar a margem, passa à linha seguinte quando permitido. |
| 2 | Inicia a edição da posição atual no modo selecionado. |
| 128 | Restaura na tela o byte mantido em `Q` e vai à confirmação de gravação. |
| Outros | Atualiza a exibição do cursor/byte e continua aguardando entrada. |

O programa de ajuda denomina os controles como setas, CLEAR, ENTER e barra,
mas a listagem não documenta uma tabela de códigos de teclado do equipamento.
Por isso, não se deve presumir que esses valores numéricos correspondam às
mesmas teclas em todo emulador.

## Modos de edição

- **Decimal — linhas 480–499.** Solicita um valor e o converte com `VAL`. O
  teste explícito rejeita valores maiores que 255; o byte é colocado no buffer
  do setor e apresentado na tela. A entrada passa pela rotina genérica
  550–630, cujas regras e estado compartilhado também afetam os campos de
  seleção.
- **ASCII — linha 500.** Solicita um caractere, converte-o com `ASC` e usa o
  código como byte. A rotina genérica de entrada limita e filtra os caracteres
  conforme o estado de `A(3)`.
- **Gráfico — linhas 510–540.** Usa as teclas `8`, `9`, `5`, `6`, `2` e `3`
  para alternar bits do byte. `ENTER` (código 13 na cadeia `GM$`) termina a
  composição e aplica o valor.

Os três modos atualizam a área de memória do setor e a posição visível na tela.
O fluxo de gravação no disco é separado e só é alcançado depois da confirmação.

## Interface com memória e rotinas Z80

O desassemblador, os endereços, a análise dos operandos autoalterados e a
documentação instrução por instrução estão em
[`ZAPPER_Rotinas_Z80_Assembler.md`](./ZAPPER_Rotinas_Z80_Assembler.md).

### Áreas e parâmetros conhecidos pela listagem

| Elemento | Evidência no fonte | Descrição segura |
|---|---|---|
| Bloco de bytes da linha 60 | Copiado a partir de `-18205`, 47 bytes | Código Z80 carregado na memória. |
| Bloco de bytes da linha 70 | Copiado a partir de `-32768`, 38 bytes | Código Z80 carregado na memória. |
| Bloco de bytes da linha 80 | Copiado a partir de `32755`, 13 bytes | Código Z80 carregado na memória. |
| `USR0` | Definido como `32755` | Entrada de uma rotina de máquina chamada no fluxo normal e no fluxo de confirmação. |
| `USR1` | Definido como `-18205` | Entrada de uma rotina de máquina chamada após `USR0` no fluxo normal. |
| `USR2` | Definido como `-32768` | Entrada de uma rotina de máquina chamada durante inicialização, seleção e saída do editor. |
| Parâmetros | `32756`, `32757`, `32759` | Recebem setor, trilha e drive, respectivamente, nas linhas 250 e 260. |
| Operando da chamada | `32765` (`0x7FFD`) | Recebe 117 na linha 250 e 0 na linha 260; esse endereço é o byte baixo do operando da instrução `CALL` da rotina `USR0`, portanto altera o destino da chamada. |
| Buffer do setor | `32256 + (L*16) + C` | Endereço usado para ler ou alterar cada uma das 256 posições do setor. |
| Área de exibição | A partir de `15401` | `PP` percorre as posições usadas pelo editor para mostrar o byte atual/inverso. |
| Leitura de teclado | `PEEK(14440)` | Valor consultado repetidamente pelo laço do editor. |

Os mnemônicos e os operandos autoalterados estão documentados em
[`ZAPPER_Rotinas_Z80_Assembler.md`](./ZAPPER_Rotinas_Z80_Assembler.md). O
destino externo chamado por `USR0` pode ser observado pela instrução `CALL`
após a alteração do operando; sua função específica ainda precisa ser
confirmada no sistema compatível. A sequência de chamadas não basta para
afirmar o protocolo completo de leitura e gravação no disco.

## Entrada de dados

As linhas 550–630 implementam a entrada reutilizada para drive, trilha, setor
e valores de edição. A rotina posiciona o cursor com `PRINT@`, mostra pontos
como campo de entrada, aceita caracteres conforme o seletor `A(3)`, trata
backspace e retorna o texto em `A$(1)`. Os chamadores convertem esse texto com
`VAL` ou `ASC`.

Essa rotina usa variáveis e elementos de matrizes BASIC compartilhados. Para
preservar fielmente o comportamento, uma reimplementação deve estudar seus
estados e filtros em conjunto com os chamadores, em vez de substituí-la por um
campo de entrada moderno presumindo que todas as regras são idênticas.

## Limites e pontos a verificar

- O fonte identifica-se como reconstrução parcial revisada. Comparações com a
  listagem publicada e testes na plataforma compatível continuam importantes.
- `CMD`, `PRINT@`, `PEEK`, `POKE`, `DEFUSR`, `USR` e as convenções de endereço
  não são portáveis diretamente para VB.NET ou para BASIC moderno.
- Embora a tela de título identifique “DOS500 - TRSDOS”, a listagem não
  especifica a versão/configuração exata do sistema, a imagem de disco, a
  configuração física do controlador, nem como criar uma cópia de segurança.
- A tela de fósforo verde é uma característica do monitor ou da apresentação do
  emulador; não há, no código apresentado, configuração de cor para implementá-la.
- Como o utilitário altera setores, os testes devem ser feitos em cópia da
  imagem/disco, nunca no único exemplar preservado.
- Uma versão moderna deve ser identificada como reimplementação e documentar
  eventuais diferenças de comportamento, formato de imagem e validação.

## Roteiro recomendado para documentação histórica adicional

1. Guardar cópias imutáveis do fonte, das imagens de disco e dos materiais
   publicados, anotando origem e data de cada arquivo.
2. Registrar modelo de máquina, versão do BASIC e sistema operacional usados
   para executar a reconstrução.
3. Anotar emulador, versão, configuração de teclado, unidade/disco montado e
   paleta de tela.
4. Fotografar ou capturar a tela em cada etapa: início, seleção, navegação,
   edição em cada modo e confirmação.
5. Testar leitura e gravação somente em imagem descartável e registrar os
   setores e valores de entrada/saída.
6. Manter separadas a transcrição histórica, as correções editoriais, as
   hipóteses de análise e qualquer reimplementação moderna.
