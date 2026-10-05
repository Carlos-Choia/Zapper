# ZAPPER/BAS — reconstrução e documentação das rotinas Z80

## Escopo e grau de certeza

Este documento desassembla os bytes das linhas BASIC 60, 70 e 80 de
[`ZAPPER_Reconstruido_Copilot.BAS`](./ZAPPER_Reconstruido_Copilot.BAS), usando
a sintaxe do Zilog Z80. Os bytes foram transcritos da listagem e os mnemônicos
abaixo são a tradução dessas instruções.

## Endereços e associação com `USR`

O BASIC carrega os bytes nestes endereços e define as entradas:

| Linha `DATA` | Bytes | Endereço de carga (hex) | Entrada BASIC | Função |
|---|---:|---:|---|---|
| 60 | 47 | `B8E3` | `USR1=-18205` | Carrega o buffer na tela |
| 70 | 38 | `8000` | `USR2=-32768` | Limpa meia tela |
| 80 | 13 | `7FF3` | `USR0=32755` | lê ou grava o setor do disco usando o buffer |

Os endereços negativos são interpretados como endereços de 16 bits em
complemento de dois: `-18205` equivale a `0xB8E3` e `-32768` a `0x8000`.
Essa correspondência pressupõe as convenções de endereço do BASIC/plataforma
para a qual o fonte foi escrito.

A rotina da linha 80 termina em `7FFF`; a rotina da linha 70 começa em `8000`.
Elas ocupam, portanto, endereços contíguos, mas têm entradas `USR` distintas.

Convenções das listagens abaixo:

- `nn` indica byte imediato em hexadecimal; palavras Z80 são little-endian.
- `JR` usa deslocamento relativo com sinal, contado a partir do byte seguinte
  ao deslocamento.
- Os nomes `L60_*`, `L70_*` e `L80_*` são rótulos explicativos deste documento,
  não rótulos presentes no BASIC original.

## Linha 60 — Carrega o buffer na tela

**Entrada:** `B8E3` (`USR1`). **Tamanho:** 47 bytes (`B8E3–B911`).

```asm
B8E3  L60_START:
B8E3      LD   HL,3C28h       ; 21 28 3C
B8E6      LD   DE,0011h       ; 11 11 00
B8E9      LD   BC,002Fh       ; 01 2F 00
B8EC      LD   A,10h          ; 3E 10
B8EE  L60_MARK:
B8EE      LD   (HL),95h       ; 36 95
B8F0      ADD  HL,DE          ; 19
B8F1      LD   (HL),AAh       ; 36 AA
B8F3      ADD  HL,BC          ; 09
B8F4      DEC  A              ; 3D
B8F5      JR   NZ,L60_MARK    ; 20 F7
B8F7      LD   HL,7E00h       ; 21 00 7E
B8FA      LD   DE,3C29h       ; 11 29 3C
B8FD      LD   A,10h          ; 3E 10
B8FF  L60_ROW:
B8FF      LD   BC,0010h       ; 01 10 00
B902      LDIR                ; ED B0
B904      PUSH HL             ; E5
B905      LD   H,D             ; 62
B906      LD   L,E             ; 6B
B907      LD   DE,0030h       ; 11 30 00
B90A      ADD  HL,DE           ; 19
B90B      LD   D,H             ; 54
B90C      LD   E,L             ; 5D
B90D      POP  HL              ; E1
B90E      DEC  A               ; 3D
B90F      JR   NZ,L60_ROW     ; 20 EE
B911      RET                 ; C9
```

### Leitura instrução por instrução

| Endereço | Instrução | Efeito observável |
|---|---|---|
| `B8E3` | `LD HL,3C28h` | Inicializa `HL` em `0x3C28` (decimal 15.400). |
| `B8E6` | `LD DE,0011h` | Define incremento de 17 bytes para o primeiro marcador. |
| `B8E9` | `LD BC,002Fh` | Define incremento adicional de 47 bytes. |
| `B8EC` | `LD A,10h` | Prepara 16 iterações para o laço de marcadores. |
| `B8EE` | `LD (HL),95h` | Escreve `0x95` no endereço apontado por `HL`. |
| `B8F0` | `ADD HL,DE` | Avança 17 bytes. |
| `B8F1` | `LD (HL),AAh` | Escreve `0xAA` no segundo endereço da linha. |
| `B8F3` | `ADD HL,BC` | Avança mais 47 bytes: a próxima iteração começa 64 bytes depois da anterior. |
| `B8F4` | `DEC A` | Decrementa o contador. |
| `B8F5` | `JR NZ,B8EE` | Repete os dois marcadores até completar 16 iterações. O deslocamento `F7h` é −9. |
| `B8F7` | `LD HL,7E00h` | Aponta `HL` para `0x7E00` (decimal 32.256), usado como origem dos bytes. |
| `B8FA` | `LD DE,3C29h` | Define o destino inicial em `0x3C29` (decimal 15.401). |
| `B8FD` | `LD A,10h` | Define 16 linhas de cópia. |
| `B8FF` | `LD BC,0010h` | Define 16 bytes por linha. Esta instrução está dentro do laço e repõe o contador antes de cada `LDIR`. |
| `B902` | `LDIR` | Copia 16 bytes de `(HL)` para `(DE)`, incrementando os ponteiros. |
| `B904` | `PUSH HL` | Guarda a origem já avançada 16 bytes. |
| `B905–B906` | `LD H,D` / `LD L,E` | Copia o destino avançado para `HL`. |
| `B907` | `LD DE,0030h` | Carrega 48, o espaço entre o fim de uma linha de 16 bytes e o início da próxima. |
| `B90A` | `ADD HL,DE` | Avança o destino mais 48 bytes. Com os 16 bytes copiados, o passo total entre inícios de linha é 64. |
| `B90B–B90C` | `LD D,H` / `LD E,L` | Atualiza `DE` para o início da próxima linha de destino. |
| `B90D` | `POP HL` | Recupera a origem avançada, para continuar no próximo bloco de 16 bytes. |
| `B90E` | `DEC A` | Decrementa o contador de linhas. |
| `B90F` | `JR NZ,B8FF` | Repete até completar as 16 linhas, recarregando `BC` antes do próximo `LDIR`. O deslocamento `EEh` é −18. |
| `B911` | `RET` | Retorna ao BASIC. |

**Resumo do percurso:** o primeiro laço escreve 16 pares de marcadores
`95h`/`AAh` em posições separadas por 64 bytes. O segundo copia 16 blocos
consecutivos de 16 bytes desde `0x7E00` para linhas de destino com passo de
64 bytes, totalizando 256 bytes. O significado visual dos valores `95h` e
`AAh` depende do conjunto de caracteres e do mapeamento de tela da máquina.

## Linha 70 — Limpa meia tela

**Entrada:** `8000` (`USR2`). **Tamanho:** 38 bytes (`8000–8025`).

```asm
8000  L70_START:
8000      LD   A,22h          ; 3E 22
8002      LD   HL,8050h       ; 21 50 80
8005  L70_CLEAR:
8005      LD   (HL),20h       ; 36 20
8007      INC  HL             ; 23
8008      DEC  A              ; 3D
8009      JR   NZ,L70_CLEAR   ; 20 FA
800B      LD   A,0Bh          ; 3E 0B
800D      LD   DE,3D02h       ; 11 02 3D
8010  L70_COPY:
8010      LD   HL,8050h       ; 21 50 80
8013      LD   BC,0022h       ; 01 22 00
8016      LDIR                ; ED B0
8018      PUSH HL             ; E5
8019      LD   H,D             ; 62
801A      LD   L,E             ; 6B
801B      LD   DE,001Eh       ; 11 1E 00
801E      ADD  HL,DE           ; 19
801F      LD   D,H             ; 54
8020      LD   E,L             ; 5D
8021      POP  HL              ; E1
8022      DEC  A               ; 3D
8023      JR   NZ,L70_COPY    ; 20 EB
8025      RET                 ; C9
```

### Leitura instrução por instrução

| Endereço | Instrução | Efeito observável |
|---|---|---|
| `8000` | `LD A,22h` | Define 34 iterações. |
| `8002` | `LD HL,8050h` | Aponta para a área de memória `0x8050`. |
| `8005` | `LD (HL),20h` | Escreve espaço (`0x20`) nessa área. |
| `8007` | `INC HL` | Avança para o próximo endereço. |
| `8008` | `DEC A` | Decrementa o contador. |
| `8009` | `JR NZ,8005` | Repete até preencher 34 bytes com espaços; deslocamento `FAh` = −6. |
| `800B` | `LD A,0Bh` | Define 11 iterações para a cópia. |
| `800D` | `LD DE,3D02h` | Define o destino inicial `0x3D02` (decimal 15.618). |
| `8010` | `LD HL,8050h` | Reinicia a origem em `0x8050` no início de cada iteração. |
| `8013` | `LD BC,0022h` | Define o tamanho da cópia como 34 bytes. |
| `8016` | `LDIR` | Copia 34 bytes de `0x8050–0x8071` para o destino e termina com `BC=0`. |
| `8018` | `PUSH HL` | Guarda `HL` após a cópia. |
| `8019–801A` | `LD H,D` / `LD L,E` | Copia o destino após a cópia para `HL`. |
| `801B` | `LD DE,001Eh` | Define incremento adicional de 30 bytes. |
| `801E` | `ADD HL,DE` | Avança o próximo destino 30 bytes além do fim da cópia: passo total de 64. |
| `801F–8020` | `LD D,H` / `LD E,L` | Atualiza o destino para a próxima linha. |
| `8021` | `POP HL` | Restaura o valor salvo de `HL`; o próximo salto, porém, volta a carregá-lo de `0x8050`. |
| `8022` | `DEC A` | Decrementa o contador de iterações. |
| `8023` | `JR NZ,8010` | Volta ao início da preparação da linha: carrega novamente `HL` e `BC`. Deslocamento `EBh` = −21. |
| `8025` | `RET` | Retorna ao BASIC se o laço terminar. |

**Resumo do percurso:** a rotina preenche com espaços 34 bytes a partir de
`0x8050`. Em seguida, por 11 iterações, recarrega `HL=0x8050` e `BC=34`, copia
esse bloco para o destino atual com `LDIR` e avança o destino 64 bytes. O
deslocamento `EBh` leva de `8025` a `8010`, onde a execução passa tanto pela
instrução que carrega `HL` quanto pela que recarrega `BC`; portanto, cada
iteração volta a copiar 34 espaços, não a executar `LDIR` com contador zero.

## Linha 80 — lê ou grava o setor do disco usando o buffer usando chamada externa

**Entrada:** `7FF3` (`USR0`). **Tamanho:** 13 bytes (`7FF3–7FFF`).

```asm
7FF3  L80_START:
7FF3      LD   DE,0D0Dh       ; 11 0D 0D
7FF6      LD   BC,000Dh       ; 01 0D 00
7FF9      LD   HL,7E00h       ; 21 00 7E
7FFC      CALL 4675h          ; CD 75 46
7FFF      RET                 ; C9
```

### Leitura instrução por instrução

| Endereço | Instrução | Efeito observável |
|---|---|---|
| `7FF3` | `LD DE,0D0Dh` | Carrega `DE=0x0D0D`. |
| `7FF6` | `LD BC,000Dh` | Carrega `BC=13`. |
| `7FF9` | `LD HL,7E00h` | Aponta `HL` para `0x7E00`, o mesmo endereço usado como buffer pela rotina da linha 60. |
| `7FFC` | `CALL 4675h` | Chama código externo em `0x4675`; a rotina espera que ele use os registradores/estado estabelecidos pelo chamador ou pelo sistema. |
| `7FFF` | `RET` | Retorna ao BASIC após o retorno da chamada externa. |

O BASIC prepara também, antes de chamar `USR0`, os bytes nos endereços
`32756` (`0x7FF4`), `32757` (`0x7FF5`), `32759` (`0x7FF7`) e `32765`
(`0x7FFD`). Esses endereços ficam dentro da área ocupada pelas instruções desta
rotina, mas em posições que são operandos imediatos:

- `0x7FF4–0x7FF5`: operando de `LD DE,nn`;
- `0x7FF7–0x7FF8`: operando de `LD BC,nn`;
- `0x7FFD–0x7FFE`: operando do endereço de `CALL nn`.

Isso é self-modifying code: o BASIC altera os operandos da rotina antes de
executá-la. A listagem mostra os valores escritos em cada caminho:

| Caminho BASIC | `0x7FF4` (`DE`) | `0x7FF5` | `0x7FF7` (`BC`) | `0x7FFD–0x7FFE` |
|---|---:|---:|---:|---|
| Linha 250, antes do fluxo normal | `SE` | `TR` | `DR` | `117` em `0x7FFD`; byte em `0x7FFE` não escrito ali |
| Linha 260, antes da confirmação `S` | `SE` | `TR` | `DR` | `0` em `0x7FFD`; byte em `0x7FFE` não escrito ali |

Com os bytes preparados pelas linhas 250/260, a instrução `LD DE,nn` recebe
`E=SE` e `D=TR`, portanto `DE=(TR*256)+SE`. A instrução `LD BC,nn` recebe
`C=DR`; `B` permanece zero. Esses são os registradores entregues à chamada
externa, sem presumir como o sistema interpreta os parâmetros.

**Atenção:** a tabela reflete literalmente os endereços `POKE` da listagem.
Como a instrução `CALL 4675h` codifica o endereço em `0x7FFD–0x7FFE`, escrever
apenas em `0x7FFD` altera o byte baixo do destino e deixa o byte alto conforme
estava. O byte alto inicial `0x46` vem de `DATA` (`117,70` = `75h,46h`), de
modo que o destino inicial é `0x4675`; depois de `POKE 32765,117` ou `0`, o
destino codificado passa a depender do byte baixo escrito e do byte alto
preservado. Esta relação deve ser considerada ao interpretar o protocolo.

No fluxo de confirmação `S`, a linha 260 escreve `0` em `0x7FFD`, antes de
chamar `USR0`; portanto, o alvo da chamada passa a `0x4600`, se a convenção de
endereços for a indicada. No fluxo normal, a linha 250 escreve `117` (`0x75`),
formando `0x4675`. Essa leitura literal é consistente com a montagem da
instrução e deve ser validada contra o sistema original. Não há evidência
suficiente apenas no BASIC para nomear `0x4675` ou `0x4600` como funções
específicas do DOS.

## Relação com as chamadas BASIC

| Chamador BASIC | Preparação/ação visível |
|---|---|
| Linha 110 | Chama `USR2` após aceitar os valores de drive, trilha e setor. |
| Linha 130 | Executa `GOSUB 250`, chama `USR0` e depois `USR1`. |
| Linha 250 | Grava setor/trilha/drive nos operandos e escreve `117` em `32765`. |
| Linha 260 | Grava setor/trilha/drive nos mesmos operandos e escreve `0` em `32765`; usada no caminho `S`. |
| Linha 720 | Chama `USR2`, redesenha o menu, executa a preparação da linha 260 e chama `USR0`. |
| Linhas 170 e 270 | Chamam `USR2` durante a interface/editor. |

Essas relações documentam o fluxo do chamador; o efeito no disco depende da
rotina externa e da compatibilidade do ambiente.

## Como confirmar a reconstrução

1. Compare cada sequência decimal de `DATA` com uma digitalização legível da
   listagem publicada.
2. Use um desassemblador Z80 independente para confirmar os mnemônicos e alvos
   dos desvios; preserve neste arquivo tanto os bytes quanto a versão
   interpretada.
3. Em emulador compatível, use cópia da imagem de disco e monitore `PC`,
   `HL`, `DE`, `BC`, `A` e os endereços de memória `0x7FF3–0x8000`.
4. Antes de permitir qualquer gravação, teste a chamada `USR0` só em mídia
   descartável e registre o valor final dos operandos `0x7FFD–0x7FFE`.
5. Mantenha a transcrição original imutável; registre separadamente qualquer
   variante corrigida e os resultados que justificariam a correção.

## Glossário mínimo

- **Opcode:** byte ou sequência de bytes que codifica uma instrução.
- **`LDIR`:** instrução Z80 de cópia em bloco; usa `HL` como origem, `DE` como
  destino e `BC` como contador, decrementando `BC` até zero.
- **Self-modifying code:** programa que altera bytes de suas próprias
  instruções/operandos em tempo de execução.
- **Little-endian:** representação de uma palavra com o byte menos
  significativo primeiro, como `75h,46h` para `4675h`.
- **`USR`:** chamada do BASIC a uma rotina de máquina, conforme a convenção do
  BASIC e da plataforma original.
