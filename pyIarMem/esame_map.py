import re

LWIP = [
    "err.o",
    "autoip.o",
    "dhcp.o",
    "etharp.o",
    "icmp.o",
    "ip4.o",
    "ip4_addr.o",
    "ip4_frag.o",
    "def.o",
    "inet_chksum.o",
    "init.o",
    "ip.o",
    "mem.o",
    "memp.o",
    "netif.o",
    "pbuf.o",
    "stats.o",
    "tcp.o",
    "tcp_in.o",
    "tcp_out.o",
    "timeouts.o",
    "udp.o",
    "ethernet.o",
]

PORT = [
    "drv.o",
    "lan87xx.o",
    "lwiport.o",
    "net_if.o",
    "net_op.o",
    "net_op_tcp.o",
    "net_op_udp.o",
    "tcp_eco.o",
    "udp_eco.o",
]

SEZ_ROM = [".rodata", ".text"]
SEZ_RAM = [".data", ".bss", ".ethernet", ".no_cache", ".dtcm"]


def dividi(cosa: str):
    a = cosa.strip()
    b = re.sub(" +", " ", a)
    c = b.split(" ")
    if len(c) >= 6:
        return c
    return None


def trova(sezioni: list, _riga: str, trovati: list, desiderati: list):
    for sezione in sezioni:
        if sezione in _riga:
            campi = dividi(_riga)
            if campi is not None:
                if campi[-2] in desiderati:
                    trovati.append(campi)
                    return True
    return False


def placement_summary(nomef: str, lista: list):
    _rom = []
    _ram = []
    with open(nomef, "rt") as mappa:
        while True:
            riga = mappa.readline()
            if "PLACEMENT SUMMARY" in riga:
                break

        while True:
            riga = mappa.readline()
            if len(riga) == 0:
                break
            if "Unused ranges:" in riga:
                break
            if len(riga) < 50:
                continue
            if trova(SEZ_ROM, riga, _rom, lista):
                continue
            if trova(SEZ_RAM, riga, _ram, lista):
                continue
    return _rom, _ram


def somma(_rxm: list):
    tot = 0
    for elem in _rxm:
        dim = int(elem[-3], 16)
        tot += dim
    return tot


def stampa(_rxm: list):
    x = sorted(_rxm, key=lambda elem: int(elem[-3], 16))
    for elem in x:
        print(elem)


if __name__ == "__main__":
    NOMEF = "SC756_lwip.map"

    rom, ram = placement_summary(NOMEF, LWIP)
    brom = somma(rom)
    bram = somma(ram)
    print("LWIP occupa: rom {}, ram {}".format(brom, bram))

    rom, ram = placement_summary(NOMEF, PORT)
    stampa(rom)
    stampa(ram)
    brom = somma(rom)
    bram = somma(ram)
    print("PORT occupa: rom {}, ram {}".format(brom, bram))
