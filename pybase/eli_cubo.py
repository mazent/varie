from pathlib import Path

# elimina la roba del cubo dai file c e h

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
