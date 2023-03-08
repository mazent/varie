import sys
import re


def estrai_da_py(vecchio):
    lista = []
    with open(vecchio, 'rt') as ing:
        while True:
            riga = ing.readline()
            if not any(riga):
                break

            if '.configure(command=' in riga or ".bind('<" in riga:
                lista.append(riga)
                continue

    if any(lista):
        lista.sort(key=lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)])

        with open('callback.py', 'wt') as usc:
            usc.write('def _callback(self):\n')
            for cb in lista:
                cb = cb.lstrip(' ')
                usc.write('    ' + cb)

def elimina_da_tcl(vecchio):
    nuovo = vecchio + '.nuovo'
    with open(vecchio, 'rt') as ing, open(nuovo, 'wt') as usc:
        while True:
            riga = ing.readline()
            if not any(riga):
                break
            le = riga.split(' ')
            try:
                dove = le.index('-command')
                del le[dove]
                del le[dove]
                rn = ''.join(x + ' ' for x in le)
                usc.write(rn)
            except ValueError:
                try:
                    dove = le.index('bind')
                    if dove == 0:
                        usc.write(riga)
                    else:
                        # elimino anche le due successive
                        _ = ing.readline()
                        _ = ing.readline()

                except ValueError:
                    usc.write(riga)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('passare gui.py e gui.tcl')
    else:
        estrai_da_py(sys.argv[1])
        elimina_da_tcl(sys.argv[2])