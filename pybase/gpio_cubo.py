if __name__ == "__main__":
    ris = {}
    with open("SC828.ioc", "rt") as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            if "GPIO_Label=" in riga:
                pinp = riga.find('.')
                pin = riga[:pinp]
                nomep = riga.find('=')
                nome = riga[nomep + 1:]
                nome = nome.strip()
                ris[pin] = [nome]
                continue

            if ".Signal=GPIO_Output" in riga:
                pinp = riga.find('.')
                pin = riga[:pinp]
                dati = ris[pin]
                dati.append('usc')
                ris[pin] = dati
                continue

            if ".Signal=GPIO_Input" in riga:
                pinp = riga.find('.')
                pin = riga[:pinp]
                dati = ris[pin]
                dati.append('ing')
                ris[pin] = dati
                continue

            if ".GPIO_ModeDefaultEXTI=" in riga:
                pinp = riga.find('.')
                pin = riga[:pinp]
                dati = ris[pin]
                dati.append('irq')
                ris[pin] = dati
                continue

    # print(ris)

    ing = {}
    usc = {}
    irq = {}
    for pin in ris:
        dati = ris[pin]
        if len(dati) == 1:
            continue
        if dati[1] == 'ing':
            ing[pin] = dati[0]
        if dati[1] == 'usc':
            usc[pin] = dati[0]
        if dati[1] == 'irq':
            num = int(pin[2:])
            irq[num] = [pin, dati[0]]

    if len(usc) == 0:
        print("Nessuna uscita")
    else:
        print("Uscite")
        for pin in usc:
            print("    {} {}".format(pin, usc[pin]))

    if len(ing) == 0:
        print("Nessun ingresso")
    else:
        print("Ingressi")
        for pin in ing:
            print("    {} {}".format(pin, ing[pin]))

    if len(irq) == 0:
        print("Nessuna interruzione")
    else:
        print("Interruzioni")
        for key, value in sorted(irq.items()):
            print("    {} {}".format(value[0], value[1]))
