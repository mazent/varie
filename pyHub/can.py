import struct

import gui_support
import utili

CAN_IDSTD_MSK = (1 << 11) - 1
CAN_IDEXT_MSK = (1 << 29) - 1

DESC_MODO = [
    "Normal",
    "Bus Monitoring",
    "Internal Loopback",
    "External Loopback",
    "Restricted Operation",
]


class CAN_GUI:
    def __init__(self):
        self.ButtonCanChiudi.configure(command=self._ButtonCanChiudi)
        self.ButtonCanNom.configure(command=self._ButtonCanNom)
        self.ButtonCanFd.configure(command=self._ButtonCanFd)
        self.ButtonCanApri.configure(command=self._ButtonCanApri)
        self.ButtonCanTx.configure(command=self._ButtonCanTx)
        self.ButtonCanRx.configure(command=self._ButtonCanRx)
        self.ButtonCanCrea.configure(command=self._ButtonCanCrea)

        self.ComboCan["values"] = DESC_MODO
        self.ComboCan.current(0)

        gui_support.canX.set("1")
        gui_support.sjwd.set(1)
        gui_support.sjwn.set(1)
        gui_support.kbitd.set(2000)
        gui_support.kbitn.set(100)
        gui_support.percd.set(80)
        gui_support.percn.set(80)
        gui_support.ra.set(0)
        gui_support.fdf.set(0)
        gui_support.brs.set(0)
        gui_support.eid.set(0)
        gui_support.esi.set(0)

    @staticmethod
    def _ButtonCanCrea():
        cid = utili.numero_casuale(0xFFFFFFFF)
        if gui_support.eid.get() == "1":
            cid &= CAN_IDEXT_MSK
        else:
            cid &= CAN_IDSTD_MSK
        gui_support.id.set(cid)

    def _ButtonCanChiudi(self):
        can = int(gui_support.canX.get())
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("canc", can))

    def _ButtonCanNom(self):
        can = int(gui_support.canX.get())
        try:
            esito, sjw = utili.validaCampo(gui_support.sjwn.get(), 1, 128)
            if not esito:
                raise utili.PROBLEMA("? sjw ?")

            esito, baud = utili.validaCampo(gui_support.kbitn.get(), 1, 1000)
            if not esito:
                raise utili.PROBLEMA("? Kbit ?")

            esito, perc = utili.validaCampo(gui_support.percn.get(), 50, 95)
            if not esito:
                raise utili.PROBLEMA("? % ?")

            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("cans", can, sjw, baud, perc))
        except utili.PROBLEMA as err:
            gui_support.Messaggio.set(str(err))

    def _ButtonCanFd(self):
        can = int(gui_support.canX.get())
        try:
            esito, sjw = utili.validaCampo(gui_support.sjwn.get(), 1, 128)
            if not esito:
                raise utili.PROBLEMA("? sjw ?")

            esito, baud = utili.validaCampo(gui_support.kbitn.get(), 1, 1000)
            if not esito:
                raise utili.PROBLEMA("? Kbit ?")

            esito, perc = utili.validaCampo(gui_support.percn.get(), 50, 95)
            if not esito:
                raise utili.PROBLEMA("? % ?")

            esito, sjwd = utili.validaCampo(gui_support.sjwd.get(), 1, 16)
            if not esito:
                raise utili.PROBLEMA("? sjw ?")

            esito, baudd = utili.validaCampo(gui_support.kbitd.get(), 1, 8000)
            if not esito:
                raise utili.PROBLEMA("? Kbit ?")

            esito, percd = utili.validaCampo(gui_support.percn.get(), 50, 95)
            if not esito:
                raise utili.PROBLEMA("? % ?")

            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("canf", can, sjw, baud, perc, sjwd, baudd, percd))
        except utili.PROBLEMA as err:
            gui_support.Messaggio.set(str(err))

    def _ButtonCanApri(self):
        can = int(gui_support.canX.get())
        ra = gui_support.ra.get() == "1"
        modo = self.ComboCan.current()
        if 0 <= modo <= len(DESC_MODO):
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("cana", can, ra, modo))

    def _ButtonCanTx(self):
        can = int(gui_support.canX.get())
        fdf = gui_support.fdf.get() == "1"
        brs = gui_support.brs.get() == "1"
        eid = gui_support.eid.get() == "1"
        try:
            esito, idi = utili.validaCampo(gui_support.id.get())
            if not esito:
                raise utili.PROBLEMA("? id ?")

            msg = utili.ba_da_stringa(gui_support.tx_dati.get(), " ")
            if msg is None:
                raise utili.PROBLEMA("? dati ?")

            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("cant", can, fdf, brs, eid, idi, msg))

        except utili.PROBLEMA as err:
            gui_support.Messaggio.set(str(err))

    def _ButtonCanRx(self):
        gui_support.id.set("??")
        gui_support.rx_dati.set("??")
        can = int(gui_support.canX.get())
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("canr", can))


class CAN_EXE:
    def __init__(self):
        self.comando["canc"] = self._can_chiudi
        self.comando["cans"] = self._can_std
        self.comando["canf"] = self._can_fd
        self.comando["cana"] = self._can_apri
        self.comando["cant"] = self._can_trasm
        self.comando["canr"] = self._can_ricev

    def _can_chiudi(self, prm):
        if self.dispo.can_chiudi(prm[1]):
            gui_support.Messaggio.set("Chiusura CAN: BENE")
        else:
            gui_support.Messaggio.set("Chiusura CAN: MALE")

    def _can_std(self, prm):
        if self.dispo.can_std(prm[1], prm[2], prm[3], prm[4]):
            gui_support.Messaggio.set("Imposta CAN: BENE")
        else:
            gui_support.Messaggio.set("Imposta CAN: MALE")

    def _can_fd(self, prm):
        if self.dispo.can_fd(prm[1], prm[2], prm[3], prm[4], prm[5], prm[6], prm[7]):
            gui_support.Messaggio.set("Imposta CAN: BENE")
        else:
            gui_support.Messaggio.set("Imposta CAN: MALE")

    def _can_apri(self, prm):
        if self.dispo.can_apri(prm[1], prm[2], prm[3]):
            gui_support.Messaggio.set("Apri CAN: BENE")
        else:
            gui_support.Messaggio.set("Apri CAN: MALE")

    def _can_trasm(self, prm):
        if self.dispo.can_tx(prm[1], prm[2], prm[3], prm[4], prm[5], prm[6]):
            gui_support.Messaggio.set("Trasmissione CAN: BENE")
        else:
            gui_support.Messaggio.set("Trasmissione CAN: MALE")

    def _can_ricev(self, prm):
        roba = self.dispo.can_rx(prm[1])
        if roba is None:
            gui_support.Messaggio.set("Ricezione CAN: MALE")
        else:
            try:
                gui_support.fdf.set(roba["fdf"])
                gui_support.esi.set(roba["esi"])
                gui_support.eid.set(roba["eid"])
                gui_support.id.set("0x{:08X}".format(roba["id"]))
                gui_support.rx_dati.set(utili.stringa_da_ba(roba["msg"], " "))
            except KeyError:
                gui_support.id.set("")
                gui_support.rx_dati.set("nessun messaggio")
            gui_support.Messaggio.set("Ricezione CAN: BENE")


class CAN_DISPO:
    def __init__(self):
        pass

    def can_chiudi(self, quale):
        return self.prot.cmdPrmVoid(0x0C01, bytes([quale]))

    def can_std(self, quale, sjw, baud, perc):
        if not 1 <= sjw <= 128:
            return False
        sjw -= 1
        if not 1 <= baud <= 1000:
            return False
        if not 50 <= perc <= 95:
            return False
        perc -= 50
        prm = struct.pack("<BBH", quale, sjw << 1, baud + (perc << 10))
        return self.prot.cmdPrmVoid(0x0C02, prm)

    def can_fd(self, quale, sjwn, baudn, percn, sjwd, baudd, percd):
        if not 1 <= sjwn <= 128:
            return False
        sjwn -= 1
        if not 1 <= baudn <= 1000:
            return False
        if not 50 <= percn <= 95:
            return False
        percn -= 50
        if not 1 <= sjwd <= 16:
            return False
        sjwd -= 1
        if not 1 <= baudd <= 8000:
            return False
        if not 50 <= percd <= 95:
            return False
        percd -= 50
        prm = struct.pack(
            "<BBHI",
            quale,
            sjwn << 1,
            baudn + (percn << 10),
            baudd + (percd << 13) + (sjwd << 19),
        )
        return self.prot.cmdPrmVoid(0x0C03, prm)

    def can_apri(self, quale, ritra: bool, modo: int, remote=True, filtri=False):
        prm = 0
        if remote:
            # Scarta tutti i remote frame
            prm += 1 << 0
        if filtri:
            # Scarta i frame che hanno superato i filtri
            prm += 1 << 1
        if ritra:
            # Ritrasmissione automatica
            prm += 1 << 2
        prm += (modo & 7) << 3
        return self.prot.cmdPrmVoid(0x0C04, bytes([quale, prm]))

    def can_tx(self, quale, fdf, brs, eid, ide, msg):
        spie = 0
        if fdf:
            # FD Format
            spie += 1 << 0
        if brs:
            # Bit Rate Switch
            spie += 1 << 1
        if eid:
            # Extended Id
            spie += 1 << 2
        testa = struct.pack("<BBI", quale, spie, ide)
        return self.prot.cmdPrmVoid(0x0C05, testa + msg)

    def can_rx(self, quale):
        rsp = self.prot.cmdPrmRsp(0x0C06, bytes([quale]))
        try:
            dati = rsp["prm"]
            if len(dati) == 0:
                # nessun messaggio dal can
                return {}
            if len(dati) < 1 + 4:
                # ???
                return None
            # nuovo messaggio
            spie, ide = struct.unpack("<BI", dati[:5])
            fdf = (spie & (1 << 0)) == (1 << 0)
            esi = (spie & (1 << 1)) == (1 << 1)
            eid = (spie & (1 << 2)) == (1 << 2)
            msg = dati[5:]
            return {"fdf": fdf, "esi": esi, "eid": eid, "id": ide, "msg": msg}
        except KeyError:
            return None
