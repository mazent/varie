from pathlib import Path

if __name__ == "__main__":
    p = Path(".")
    l = list(p.glob("**/*.ioc"))

    f = l[0]

    ris = {}
    with open(f.name, "rt") as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            if "GPIO_Label=" in riga:
                pinp = riga.find(".")
                pin = riga[:pinp]
                nomep = riga.find("=")
                nome = riga[nomep + 1 :]
                nome = nome.strip()
                ris[pin] = [nome]
                continue

            if ".Signal=GPIO_Output" in riga:
                pinp = riga.find(".")
                pin = riga[:pinp]
                dati = ris[pin]
                dati.append("usc")
                ris[pin] = dati
                continue

            if ".Signal=GPIO_Input" in riga:
                pinp = riga.find(".")
                pin = riga[:pinp]
                dati = ris[pin]
                dati.append("ing")
                ris[pin] = dati
                continue

            if ".GPIO_ModeDefaultEXTI=" in riga or ".Signal=GPXTI" in riga:
                pinp = riga.find(".")
                pin = riga[:pinp]
                dati = ris[pin]
                if len(dati) == 1:
                    dati.append("irq")
                    ris[pin] = dati
                continue

            if ".Signal=ADC" in riga:
                pinp = riga.find(".")
                pin = riga[:pinp]
                dati = ris[pin]
                if len(dati) == 1:
                    dati.append("adc")
                    ris[pin] = dati
                continue

    # print(ris)

    ing = {}
    usc = {}
    irq = {}
    adc = {}
    for pin in ris:
        dati = ris[pin]
        if len(dati) == 1:
            continue
        if dati[1] == "ing":
            ing[pin] = dati[0]
        if dati[1] == "usc":
            usc[pin] = dati[0]
        if dati[1] == "irq":
            sep = pin.find("_")
            if sep > 0:
                pin = pin[:sep]
            num = int(pin[2:])
            irq[num] = [pin, dati[0]]
        if dati[1] == "adc":
            adc[pin] = dati[0]

    with open("gpio.txt", "wt") as gpio:
        if len(usc) == 0:
            gpio.write("Nessuna uscita\n")
        else:
            gpio.write("Uscite\n")
            for pin in usc:
                gpio.write("    {} {}\n".format(pin, usc[pin]))

        if len(ing) == 0:
            gpio.write("Nessun ingresso\n")
        else:
            gpio.write("Ingressi\n")
            for pin in ing:
                gpio.write("    {} {}\n".format(pin, ing[pin]))

        if len(irq) == 0:
            gpio.write("Nessuna interruzione\n")
        else:
            gpio.write("Interruzioni\n")
            for key, value in sorted(irq.items()):
                gpio.write("    {} {}\n".format(value[0], value[1]))

        if len(adc) == 0:
            gpio.write("Nessuna adc\n")
        else:
            gpio.write("Analogici\n")
            for pin in adc:
                gpio.write("    {} {}\n".format(pin, adc[pin]))
