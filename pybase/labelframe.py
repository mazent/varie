# converte da TLabelframe a labelframe

if __name__ == '__main__':
    modif = False
    righe = []
    with open('gui.tcl', 'rt') as orig:
        while True:
            riga = orig.readline()
            if len(riga) == 0:
                break

            if 'TLabelframe' not in riga:
                righe.append(riga)
                continue

            # beccata! accumulo in tlf
            tlf = ''
            while True:
                tlf = tlf + ' ' + riga.strip(' \t\n\\')
                while '\\' in riga:
                    riga = orig.readline()
                    tlf = tlf + ' ' + riga.strip(' \t\n\\')

                riga = orig.readline()
                if 'vTcl:DefineAlias' in riga:
                    break

                if 'TLabelframe' in riga:
                    continue
                elif 'ttk::labelframe' in riga:
                    continue

            # cerco i pezzi
            tlf = tlf.strip()
            pezzi = tlf.split(' ')
            background = -1
            foreground = -1
            font = -1
            text = -1
            width = -1
            height = -1
            site = -1
            for i in range(len(pezzi)):
                if pezzi[i] == '-background':
                    if background < 0:
                        background = i + 1
                    continue
                if pezzi[i] == '-foreground':
                    foreground = i + 1
                    continue
                if pezzi[i] == '-font':
                    font = i + 1
                    continue
                if pezzi[i] == '-text':
                    text = i + 1
                    continue
                if pezzi[i] == '-width':
                    width = i + 1
                    continue
                if pezzi[i] == '-height':
                    height = i + 1
                    continue
                if '$site' in pezzi[i]:
                    site = i
                    continue

            if background > 0 and foreground > 0 and font > 0 and text > 0 and width > 0 and height > 0 and site > 0:
                # ok, ma il testo puo' essere: {due parole}
                testo = pezzi[text]
                if '{' in testo:
                    while True:
                        text += 1
                        testo = testo + ' ' + pezzi[text]
                        if '}' in pezzi[text]:
                            break
                righe.append('    labelframe ' + pezzi[site] + ' \\\n')
                righe.append('        -background ' + pezzi[background] + ' \\\n')
                righe.append('        -foreground ' + pezzi[foreground] + ' \\\n')
                righe.append('        -font ' + pezzi[font] + ' \\\n')
                righe.append('        -text ' + testo + ' \\\n')
                righe.append('        -width ' + pezzi[width] + ' \\\n')
                righe.append('        -height ' + pezzi[height] + ' \n')
                righe.append(riga)
                modif = True

    if modif:
        with open('nuovo_gui.tcl', 'wt') as usc:
            for riga in righe:
                usc.write(riga)
