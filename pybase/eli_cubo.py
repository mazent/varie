from pathlib import Path

alias_porta = {
    "GPIOA": "GPIOA",
    "GPIOB": "GPIOB",
    "GPIOC": "GPIOC",
    "GPIOD": "GPIOD",
    "GPIOE": "GPIOE",
    "GPIOF": "GPIOF",
    "GPIOG": "GPIOG",
    "GPIOH": "GPIOH",
}
alias_pin = {
    "GPIO_PIN_0": "GPIO_PIN_0",
    "GPIO_PIN_1": "GPIO_PIN_1",
    "GPIO_PIN_2": "GPIO_PIN_2",
    "GPIO_PIN_3": "GPIO_PIN_3",
    "GPIO_PIN_4": "GPIO_PIN_4",
    "GPIO_PIN_5": "GPIO_PIN_5",
    "GPIO_PIN_6": "GPIO_PIN_6",
    "GPIO_PIN_7": "GPIO_PIN_7",
    "GPIO_PIN_8": "GPIO_PIN_8",
    "GPIO_PIN_9": "GPIO_PIN_9",
    "GPIO_PIN_10": "GPIO_PIN_10",
    "GPIO_PIN_11": "GPIO_PIN_11",
    "GPIO_PIN_12": "GPIO_PIN_12",
    "GPIO_PIN_13": "GPIO_PIN_13",
    "GPIO_PIN_14": "GPIO_PIN_14",
    "GPIO_PIN_15": "GPIO_PIN_15",
}

DISPONIBILI = {
    "GPIOA": 0x1FFF,
    "GPIOB": 0xFFE7,
    "GPIOC": 0x3FFF,
    "GPIOD": 0xFFFF,
    "GPIOE": 0xFFFF,
    "GPIOF": 0xFFFF,
    "GPIOG": 0xFFFF,
    "GPIOH": 0xFFFC,
}

lista_righe = []


# crea un file coi pin messi bene


def pin(nomef):
    # quante macro?
    macro = []
    with open(nomef, "rt") as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            riga = riga.strip()

            if "#define" in riga:
                elem = riga.split(" ")
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
    with open(nomef + ".pin", "wt") as usc:
        for elem in sorted(macro):
            usc.write("#define ")
            usc.write(elem[0])
            d1 = len(elem[0])
            diff = 1 + dim1 - d1
            s = " " * diff
            usc.write(s)
            if "_PIN_" in elem[1]:
                usc.write("( (uint32_t) {} )".format(elem[1]))
            else:
                usc.write(elem[1])
            usc.write("\n")
    # trovo alias
    for elem in macro:
        if "_Port" in elem[0]:
            alias_porta[elem[0]] = elem[1]
        if "_Pin" in elem[0]:
            alias_pin[elem[0]] = elem[1]


# costruisce la lista dei pin usati per poi ricavare quelli liberi


def salva_liberi():
    sospesi = 0
    pin_liberi = {}
    for riga in lista_righe:
        if "GPIO_InitStruct.Pin" in riga:
            sospesi = 0
            uguale = riga.find("=")
            if uguale < 0:
                print("ERRORE " + riga)
                continue
            uguale += 1
            x = riga[uguale:]
            l = x.split("|")
            for p in l:
                p = p.strip()
                p = p.strip(";")
                p = alias_pin[p]
                pin = int(p[9:])
                if pin > 15:
                    print("? pin {} ?".format(pin))
                    continue
                sospesi += 1 << pin
        if "HAL_GPIO_Init" in riga:
            tonda = riga.find("(")
            if tonda < 0:
                print("errore " + riga)
                break
            virgola = riga.find(",")
            if virgola < 0:
                print("errore " + riga)
                break
            porta = riga[tonda + 1 : virgola]
            porta = alias_porta[porta]
            if porta in pin_liberi:
                pin_liberi[porta] |= sospesi
            else:
                pin_liberi[porta] = sospesi
            sospesi = 0

    with open("liberi.txt", "wt") as usc:
        for k in sorted(pin_liberi):
            v = pin_liberi[k]
            lib = DISPONIBILI[k] & (~v)
            lista = ""
            for pos in range(16):
                bit = 1 << pos
                if bit & lib:
                    lista += " {} ".format(pos)
            usc.write(k + lista + "\n")


def liberi(nomef: str):
    def inizio(riga: str) -> int:
        global sospesi

        if "GPIO_InitStruct.Pin" in riga:
            lista_righe.append(riga)

            if ";" in riga:
                return 2

            return 1

        return 0

    def acapo(riga: str) -> int:
        ultima = len(lista_righe) - 1
        lista_righe[ultima] = lista_righe[ultima] + riga

        if ";" in riga:
            return 2

        return 1

    def fine(riga: str) -> int:
        if "HAL_GPIO_Init" in riga:
            lista_righe.append(riga)
            return 0

        return 2

    STATI = {0: inizio, 1: acapo, 2: fine}
    stato = 0
    with open(nomef, "rt") as ing:
        while True:
            riga = ing.readline()

            if len(riga) == 0:
                break

            riga = riga.strip()

            stato = STATI[stato](riga)


if __name__ == "__main__":
    p = Path(".")
    l = list(p.glob("**/*.c")) + list(p.glob("**/*.h"))

    # elimina la roba del cubo dai file .c e .h
    for f in l:
        print(f)
        righe = []
        tolte = 0
        with open(f, "rt") as ing:
            while True:
                riga = ing.readline()

                if len(riga) == 0:
                    break

                if "USER CODE" in riga:
                    tolte += 1
                    continue

                righe.append(riga)
        if tolte:
            with open(f, "wt") as usc:
                usc.writelines(righe)
        nomef = str(f)
        if "main.h" in nomef:
            pin(nomef)
        if "main.c" in nomef:
            liberi(nomef)
        if "usbd_conf.c" in nomef:
            liberi(nomef)
        if "_hal_msp.c" in nomef:
            liberi(nomef)

    salva_liberi()
