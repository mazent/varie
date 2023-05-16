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
