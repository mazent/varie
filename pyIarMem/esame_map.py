import re

BTSTACK = [
    'ad_parser.o',
    'btstack_crypto.o',
    'btstack_linked_list.o',
    'btstack_memory.o',
    'btstack_memory_pool.o',
    'btstack_run_loop.o',
    'btstack_util.o',
    'hci.o',
    'hci_cmd.o',
    'hci_dump.o',
    'hci_transport_h4.o',
    'l2cap.o',
    'l2cap_signaling.o',
    'rfcomm.o',
    'sdp_server.o',
    'sdp_util.o',
    'sdp_client.o',
    'sdp_client_rfcomm.o',
    'hfp_ag.o',
    'hfp.o',
    'hfp_gsm_model.o',
    'att_db.o',
    'att_dispatch.o',
    'att_server.o',
    'gatt_client.o',
    'sm.o',
    'patchram_BCM20710.o'
]

BTPORT = [
    'bt.port.o',
    'btport_dump_impl.o',
    'btport_tlv.o',
    'btp_hci.o',
    'btstack_chipset_bcm.o',
    'central.o',
    'client.o',
    'control.o',
    'dut.o',
    'hfp_gateway.o',
    'inquiry.o',
    'le.adv.bcm.o',
    'le.adv.btstack.o',
    'le_link_key_db.o',
    'ntf_ind.o',
    'perip.o',
    'run.loop.o',
    'spp.o',
    'spp_conn.o',
    'spp_link_key_db.o',
    'varie.o',
    'cirbu.o',
    'drv.o',
    'heap.o',
    'mail.o',
    'secure.o',
]

SEZ_ROM = ['.rodata', '.text']
SEZ_RAM = ['.data', '.bss']


def dividi(cosa: str):
    a = cosa.strip()
    b = re.sub(' +', ' ', a)
    c = b.split(' ')
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
    with open(nomef, 'rt') as mappa:
        while True:
            riga = mappa.readline()
            if 'PLACEMENT SUMMARY' in riga:
                break

        while True:
            riga = mappa.readline()
            if len(riga) == 0:
                break
            if 'Unused ranges:' in riga:
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


if __name__ == '__main__':
    NOMEF = 'tracke.map'

    rom, ram = placement_summary(NOMEF, BTSTACK)
    brom = somma(rom)
    bram = somma(ram)
    print('BTSTACK occupa: rom {}, ram {}'.format(brom, bram))

    rom, ram = placement_summary(NOMEF, BTPORT)
    brom = somma(rom)
    bram = somma(ram)
    print('BTPORT occupa: rom {}, ram {}'.format(brom, bram))
