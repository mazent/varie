from pathlib import Path


# elimina la roba del cubo dai file c e h

def pin(nomef):
    # quante macro?
    macro = []
    with open(nomef, 'rt') as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            riga = riga.strip()

            if '#define' in riga:
                elem = riga.split(' ')
                if len(elem) == 3:
                    macro.append([elem[1], elem[2]])
                continue

    # trovo le due dimensoni massime
    dim1 = 0
    for elem in macro:
        dim = len(elem[0])
        if dim1 < dim:
            dim1 = dim

    # salvo
    with open(nomef + '.pin', 'wt') as usc:
        for elem in macro:
            usc.write("#define ")
            usc.write(elem[0])
            d1 = len(elem[0])
            diff = 1 + dim1 - d1
            s = ' ' * diff
            usc.write(s)
            if '_PIN_' in elem[1]:
                usc.write('( (uint32_t) {} )'.format(elem[1]))
            else:
                usc.write(elem[1])
            usc.write("\n")


# costruisce la lista dei pin usati per poi ricavare quelli liberi

sospesi = 0
pin_liberi = {}


def salva_liberi():
    # global pin_liberi
    tutti = {
        'GPIOD': 0xFFFF,
        'GPIOE': 0xFFFF,
        'GPIOF': 0xFFFF,
        'GPIOG': 0xFFFF,
        'GPIOA': 0x1FFF,
        'GPIOB': 0xFFE7,
        'GPIOC': 0x3FFF,
        'GPIOH': 0x7C0C
    }

    with open('liberi.txt', 'wt') as usc:
        for k in sorted(pin_liberi):
            v = pin_liberi[k]
            lib = tutti[k] & (~v)
            lista = ''
            for pos in range(16):
                bit = 1 << pos
                if bit & lib:
                    lista += ' {} '.format(pos)
            usc.write(k + lista + '\n')


def liberi(nomef: str):
    def inizio(riga: str) -> int:
        if 'GPIO_InitStruct.Pin' in riga:
            uguale = riga.find('=')
            if uguale < 0:
                return 1
            uguale += 1
            x = riga[uguale:]
            l = x.split('|')
            for p in l:
                p = p.strip()
                p = p.strip(';')
                val = p.find('GPIO_PIN_')
                if val < 0:
                    print('errore: ' + p)
                    continue
                pin = int(p[val + 9:])
                if pin > 15:
                    print('? pin {} ?'.format(pin))
                    continue
                global sospesi
                sospesi += 1 << pin

            if ';' in riga:
                return 2

            return 1

        return 0

    def acapo(riga: str) -> int:
        l = riga.split('|')
        for p in l:
            p = p.strip()
            p = p.strip(';')
            val = p.find('GPIO_PIN_')
            if val < 0:
                continue
            pin = int(p[val + 9:])
            if pin > 15:
                print('? pin {} ?'.format(pin))
                continue
            global sospesi
            sospesi += 1 << pin

        if ';' in riga:
            return 2

        return 1

    def fine(riga: str) -> int:
        if 'HAL_GPIO_Init' in riga:
            tonda = riga.find('(')
            if tonda < 0:
                print('errore ' + riga)
                return 0
            virgola = riga.find(',')
            if virgola < 0:
                print('errore ' + riga)
                return 0
            porta = riga[tonda + 1:virgola]
            global pin_liberi, sospesi
            if porta in pin_liberi:
                pin_liberi[porta] |= sospesi
            else:
                pin_liberi[porta] = sospesi
            sospesi = 0
            return 0

        return 2

    STATI = {
        0: inizio,
        1: acapo,
        2: fine
    }
    stato = 0
    with open(nomef, 'rt') as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            riga = riga.strip()

            stato = STATI[stato](riga)


if __name__ == "__main__":
    p = Path('.')
    l = list(p.glob('**/*.c')) + list(p.glob('**/*.h'))

    for f in l:
        print(f)
        righe = []
        tolte = 0
        with open(f, 'rt') as ing:
            while True:
                riga = ing.readline()

                if len(riga) == 0:
                    break

                if 'USER CODE' in riga:
                    tolte += 1
                    continue

                righe.append(riga)
        if tolte:
            with open(f, 'wt') as usc:
                usc.writelines(righe)
        nomef = str(f)
        if 'main.h' in nomef:
            pin(nomef)
        if 'main.c' in nomef:
            liberi(nomef)
        if '_hal_msp.c' in nomef:
            liberi(nomef)

    salva_liberi()
