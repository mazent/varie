import struct

import prot


class DISPOSITIVO:
    DIM_DATI_CMD = 500

    def __init__(self, **argo):
        self.coda = None
        try:
            self.prot = prot.PROT(porta=argo["uart"])
        except KeyError:
            try:
                self.prot = prot.PROT(vid=argo["vid"], pid=argo["pid"])
            except KeyError:
                self.prot = None

    def __del__(self):
        del self.prot

    def aPosto(self):
        # Controllo una sola volta
        if self.prot is None:
            return False

        return self.prot.a_posto()

    def Chiudi(self):
        if self.prot is not None:
            self.prot.chiudi()
            del self.prot
            self.prot = None

    def Cambia(self, baud=None, tempo=None):
        if self.prot is not None:
            self.prot.cambia(baud, tempo)

    def Ripristina(self):
        if self.prot is not None:
            self.prot.ripristina()

    # ============================================
    # Varie
    # ============================================

    def Eco(self, dati=None):
        if dati is None:
            dati = struct.pack("<I", 0xDEADBEEF)

        # dimorig = len(dati)

        dim = self.prot.max_dim(0x0001, dati, DISPOSITIVO.DIM_DATI_CMD)
        dati = dati[:dim]

        # print('eco {} -> {}'.format(dimorig, dim))

        eco = self.prot.cmdPrmRsp(0x0001, dati, len(dati))
        if eco is None:
            return False

        try:
            return eco["prm"] == dati
        except KeyError:
            return False

    def data(self):
        rsp = self.prot.cmdVoidRsp(0x0002)
        try:
            data_comp = rsp["prm"]
            return data_comp.decode("ascii")
        except KeyError:
            return ""

    def rtc_leggi(self):
        rsp = self.prot.cmdVoidRsp(0x0006, 6)
        try:
            brtc = rsp["prm"]
            a, m, g, o, mm, s = struct.unpack("<6B", brtc)
            a += 2000
            return "{:02}/{:02}/{:02} {:02}:{:02}:{:02}".format(a, m, g, o, mm, s)
        except KeyError:
            return None
