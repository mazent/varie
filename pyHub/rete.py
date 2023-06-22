import struct

import gui_support


class RETE_GUI:
    def __init__(self):
        self.ButtonReteLeggi.configure(command=self._ButtonReteLeggi)
        self.ButtonReteId.configure(command=self._ButtonReteId)
        self.ButtonReteAccendi.configure(command=self._ButtonReteAccendi)
        self.ButtonReteSpegni.configure(command=self._ButtonReteSpegni)
        self.ButtonReteGiolli.configure(command=self._ButtonReteGiolli)

    def _ButtonReteAccendi(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("arete", True))

    def _ButtonReteSpegni(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("arete", False))

    def _ButtonReteId(self):
        gui_support.phy.set("?")
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("phy",))

    def _ButtonReteLeggi(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("phys",))

    def _ButtonReteGiolli(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("grete", 3 * 1460, 10))


class RETE_EXE:
    def __init__(self):
        self.comando["arete"] = self._rete_attiva
        self.comando["phys"] = self._stato_rete
        self.comando["phy"] = self._id_phy
        self.comando["grete"] = self._rete_giolli

    def _rete_attiva(self, prm):
        if self.dispo.rete_attiva(prm[1]):
            gui_support.Messaggio.set("Rete: BENE")
        else:
            gui_support.Messaggio.set("Rete: MALE")

    def _id_phy(self, _):
        idp = self.dispo.rete_phy_id()
        if idp is not None:
            gui_support.phy.set("{:08X}".format(idp))
            gui_support.Messaggio.set("PHY: BENE")
        else:
            gui_support.Messaggio.set("PHY: MALE")

    def _stato_rete(self, _):
        sr = self.dispo.rete_phy_stato()
        if sr is not None:
            gui_support.link.set(sr["link"])
            gui_support.mega.set(sr["mega"])
            gui_support.duplex.set(sr["duplex"])

            gui_support.Messaggio.set("Rete: BENE")
        else:
            gui_support.Messaggio.set("Rete: MALE")

    def _rete_giolli(self, prm):
        if self.dispo.rete_giolli(prm[1], prm[2]):
            gui_support.Messaggio.set("Rete: BENE")
        else:
            gui_support.Messaggio.set("Rete: MALE")


class RETE_DISPO:
    def __init__(self):
        pass

    def rete_attiva(self, attiva: bool):
        accendi = 0
        if attiva:
            accendi = 1
        return self.prot.cmdPrmVoid(0x0E01, bytes([accendi]))

    def rete_phy_id(self):
        rsp = self.prot.cmdVoidRsp(0x0E02, 4)
        try:
            dati = rsp["prm"]
            return struct.unpack("<I", dati)[0]
        except KeyError:
            return None

    def rete_phy_stato(self):
        rsp = self.prot.cmdVoidRsp(0x0E03, 1)
        try:
            dati = rsp["prm"]
            stt = dati[0]

            LINK = 1 << 0
            MEGA = 1 << 1
            DUPLEX = 1 << 2

            return {
                "link": LINK == stt & LINK,
                "mega": MEGA == stt & MEGA,
                "duplex": DUPLEX == stt & DUPLEX,
            }
        except KeyError:
            return None

    def rete_giolli(self, dim, quanti):
        prm = struct.pack("<2H", dim, quanti)
        return self.prot.cmdPrmVoid(0x0E04, prm)
