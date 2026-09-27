import curses
import os

# Arquivo emulado que simula as 40 trilhas e 18 setores (256 bytes por setor)
ARQUIVO_DISCO = "disco_emulado.img"
TAM_SETOR = 256
TOTAL_TRILHAS = 40
TOTAL_SETORES = 18

if not os.path.exists(ARQUIVO_DISCO):
    with open(ARQUIVO_DISCO, "wb") as f:
        f.write(b"\x00" * (TOTAL_TRILHAS * TOTAL_SETORES * TAM_SETOR))

class ZapperEmulado:
    def __init__(self):
        self.drive = 0
        self.trilha = 0
        self.setor = 1
        self.modo = "DEC"  # DEC, ASC
        self.buffer = bytearray(TAM_SETOR)
        self.cursor_l = 0
        self.cursor_c = 0

    def ler_setor_disco(self):
        posicao = (self.trilha * TOTAL_SETORES + (self.setor - 1)) * TAM_SETOR
        with open(ARQUIVO_DISCO, "rb") as f:
            f.seek(posicao)
            self.buffer = bytearray(f.read(TAM_SETOR))

    def gravar_setor_disco(self):
        posicao = (self.trilha * TOTAL_SETORES + (self.setor - 1)) * TAM_SETOR
        with open(ARQUIVO_DISCO, "r+b") as f:
            f.seek(posicao)
            f.write(self.buffer)

    def desenhar_interface(self, stdscr):
        stdscr.clear()
        
        cor_verde = curses.color_pair(1)
        cor_cursor = curses.color_pair(2)
        
        # Cabeçalho original
        stdscr.addstr(0, 0, "****************************************", cor_verde)
        stdscr.addstr(1, 0, "*   --  ZAPPER/PY - EMULADO MODERN    *", cor_verde)
        stdscr.addstr(2, 0, "*    Baseado no codigo original 1986   *", cor_verde)
        stdscr.addstr(3, 0, "****************************************", cor_verde)
        
        # Status do topo
        stdscr.addstr(5, 0, f"MODO: [{self.modo}]", cor_verde)
        stdscr.addstr(6, 0, f"Drive: {self.drive}   Trilha: {self.trilha}   Setor: {self.setor}", cor_verde)
        stdscr.addstr(7, 0, "-" * 50, cor_verde)

        # Exibir a matriz do buffer de 256 bytes
        for l in range(16):
            stdscr.addstr(9 + l, 0, f"{l*16:03d}: ", cor_verde)
            
            for c in range(16):
                idx = l * 16 + c
                val = self.buffer[idx]
                
                if self.modo == "DEC":
                    item_str = f"{val:03d} "
                else:
                    item_str = f" {chr(val) if 32 <= val <= 126 else '.'}  "
                
                if l == self.cursor_l and c == self.cursor_c:
                    stdscr.addstr(item_str, cor_cursor)
                else:
                    stdscr.addstr(item_str, cor_verde)

        # Barra de informações inferior
        idx_atual = self.cursor_l * 16 + self.cursor_c
        val_atual = self.buffer[idx_atual]
        char_atual = chr(val_atual) if 32 <= val_atual <= 126 else '.'
        stdscr.addstr(26, 0, f"Posição do Buffer: {idx_atual}  |  Valor: {val_atual} ({char_atual})", cor_verde)
        stdscr.addstr(27, 0, "[Setas] Move | [M] Muda Modo | [E] Editar | [S] Salvar | [Q] Sair", cor_verde)
        stdscr.refresh()

    def rodar(self, stdscr):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        
        curses.curs_set(0)
        self.ler_setor_disco()

        while True:
            self.desenhar_interface(stdscr)
            ch = stdscr.getch()

            if ch == curses.KEY_UP and self.cursor_l > 0:
                self.cursor_l -= 1
            elif ch == curses.KEY_DOWN and self.cursor_l < 15:
                self.cursor_l += 1
            elif ch == curses.KEY_LEFT and self.cursor_c > 0:
                self.cursor_c -= 1
            elif ch == curses.KEY_RIGHT and self.cursor_c < 15:
                self.cursor_c += 1
            
            elif ch in [ord('m'), ord('M')]:
                self.modo = "ASC" if self.modo == "DEC" else "DEC"

            elif ch in [ord('e'), ord('E')]:
                idx = self.cursor_l * 16 + self.cursor_c
                
                if self.modo == "DEC":
                    # Edição em modo Decimal
                    curses.echo()
                    stdscr.addstr(28, 0, "Novo valor Decimal (0-255): ", curses.color_pair(1))
                    stdscr.move(28, 28)
                    try:
                        entrada = stdscr.getstr().decode('utf-8')
                        nv = int(entrada)
                        if 0 <= nv <= 255:
                            self.buffer[idx] = nv
                    except ValueError:
                        pass
                    curses.noecho()
                else:
                    # Edição em modo ASCII (Digitar a letra direto)
                    stdscr.addstr(28, 0, "Digite o novo caractere ASCII: ", curses.color_pair(1))
                    stdscr.refresh()
                    # Captura uma única tecla pressionada
                    char_ch = stdscr.getch()
                    # Garante que é um caractere visível válido ou espaço
                    if 32 <= char_ch <= 126:
                        self.buffer[idx] = char_ch

            elif ch in [ord('s'), ord('S')]:
                stdscr.addstr(28, 0, "Confirmar alteração no disco virtual? (S/N): ", curses.color_pair(1))
                confirmar = stdscr.getch()
                if confirmar in [ord('s'), ord('S')]:
                    self.gravar_setor_disco()
                
            elif ch in [ord('q'), ord('Q')]:
                break

if __name__ == "__main__":
    zapper = ZapperEmulado()
    curses.wrapper(zapper.rodar)
