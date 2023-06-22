import struct

import utili
import gui_support


class TCAN_GUI:
    def __init__(self):
        self.ButtonTcanInizio.configure(command=self._ButtonTcanInizio)
        self.ButtonTcanFine.configure(command=self._ButtonTcanFine)
        self.ButtonTcanNom.configure(command=self._ButtonTcanNom)
        self.ButtonTcanDat.configure(command=self._ButtonTcanDat)
        self.ButtonTcanTx.configure(command=self._ButtonTcanTx)
        self.ButtonTcanRx.configure(command=self._ButtonTcanRx)
        self.ButtonTcanLeggi.configure(command=self._ButtonTcanLeggi)
        self.ButtonTcanScrivi.configure(command=self._ButtonTcanScrivi)

        gui_support.tcanX.set("3")
        gui_support.nom_bs1.set(1)
        gui_support.nom_bs2.set(1)
        gui_support.nom_sjw.set(1)
        gui_support.data_bs1.set(1)
        gui_support.data_bs2.set(1)
        gui_support.data_sjw.set(1)
        gui_support.can_id_tipo.set(0)
        gui_support.fd_brs.set(0)

        self.cmd["canfd"] = self._valori_canfd

    def _valori_canfd(self, prm):
        self.ComboRegTcan["values"] = prm
        self.ComboRegTcan.current(0)
        gui_support.Messaggio.set("CAN FD REG: OK")

    @staticmethod
    def _ButtonTcanNom():
        # Nominal BT config preset - 0.5  Mbit/s @ 40 MHz
        # {.brp=1, .prop_seg=47, .phase_seg1=16, .phase_seg2=16, .sjw=16, .tdc=0};
        gui_support.nom_Fq.set(40000000)
        gui_support.nom_bs1.set(47 + 16)
        gui_support.nom_bs2.set(16)
        gui_support.nom_sjw.set(16)
        gui_support.Messaggio.set("Imposto 0.5 Mb/s")

    @staticmethod
    def _ButtonTcanDat():
        # Data Phase BT config preset - 2.0 Mbit @ 40 MHz
        # {.brp=1, .prop_seg=0, .phase_seg1=13, .phase_seg2=6, .sjw=6, .tdc=1,
        # .tdc_offset=14, .tdc_filter_window=0};
        gui_support.data_Fq.set(40000000)
        gui_support.data_bs1.set(13)
        gui_support.data_bs2.set(6)
        gui_support.data_sjw.set(6)
        gui_support.Messaggio.set("Imposto 2 Mb/s")

    def _ButtonTcanInizio(self):
        try:
            # brp max 512 -> 78125
            esito, Fqn = utili.validaCampo(gui_support.nom_Fq.get(), 80000, 40000000)
            if not esito:
                raise utili.problema("? frequenza del quanto normal ?")

            nrml = (
                int(gui_support.nom_bs1.get()) - 1,
                int(gui_support.nom_bs2.get()) - 1,
                int(gui_support.nom_sjw.get()) - 1,
                Fqn,
            )

            data = None

            if gui_support.fd_brs.get() == "1":
                # brp max 32
                esito, Fqd = utili.validaCampo(
                    gui_support.data_Fq.get(), 1250000, 40000000
                )
                if not esito:
                    raise utili.problema("? frequenza del quanto data ?")

                data = (
                    int(gui_support.data_bs1.get()) - 1,
                    int(gui_support.data_bs2.get()) - 1,
                    int(gui_support.data_sjw.get()) - 1,
                    Fqd,
                )

            quale = int(gui_support.tcanX.get())
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("tcan_inizio", quale, nrml, data))

        except utili.problema as err:
            gui_support.Messaggio.set(err)

    def _ButtonTcanFine(self):
        quale = int(gui_support.tcanX.get())
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("tcan_fine", quale))

    def _ButtonTcanRx(self):
        quale = int(gui_support.tcanX.get())
        gui_support.rx_dati.set("---")
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("tcan_rx", quale))

    def _ButtonTcanTx(self):
        try:
            esteso = gui_support.can_id_tipo.get() == "1"

            msk = (1 << 11) - 1
            if esteso:
                msk = (1 << 29) - 1

            esito, ident = utili.validaCampo(gui_support.can_id.get(), 0, msk)
            if not esito:
                raise utili.problema("? id ?")

            dati = bytearray()
            quasi = gui_support.tx_dati.get()
            if any(quasi):
                dati = utili.esa_da_stringa(quasi)

            quale = int(gui_support.tcanX.get())
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("tcan_tx", quale, esteso, ident, dati))
        except utili.problema as err:
            gui_support.Messaggio.set(err)

    def _ButtonTcanLeggi(self):
        try:
            esito, numreg = utili.validaCampo(gui_support.canfd_numreg.get(), 1, 256)
            if not esito:
                raise utili.problema("? da 1 a 256 registri ?")

            esito, dal = utili.validaCampo(gui_support.canfd_dal.get())
            if not esito:
                raise utili.problema("? registro iniziale ?")

            quale = int(gui_support.tcanX.get())
            gui_support.canfd_val.set("---")
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("tcan_regl", quale, numreg, dal))

        except utili.problema as err:
            gui_support.Messaggio.set(err)

    def _ButtonTcanScrivi(self):
        try:
            esito, reg = utili.validaCampo(gui_support.canfd_reg.get(), 0, 0x10FC)
            if not esito:
                raise utili.problema("? registro ?")

            esito, val = utili.validaCampo(gui_support.canfd_val.get(), 0, 0xFFFFFFFF)
            if not esito:
                raise utili.problema("? valore ?")

            quale = int(gui_support.tcanX.get())
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("tcan_regs", quale, reg, val))

        except utili.problema as err:
            gui_support.Messaggio.set(err)


class TCAN_EXE:
    def __init__(self):
        self.comando["tcan_inizio"] = self._tcan_inizio
        self.comando["tcan_fine"] = self._tcan_fine
        self.comando["tcan_tx"] = self._tcan_tx
        self.comando["tcan_rx"] = self._tcan_rx
        self.comando["tcan_regl"] = self._tcan_reg_l
        self.comando["tcan_regs"] = self._tcan_reg_s

    def _tcan_inizio(self, prm):
        if self.dispo.tcan_iniz(prm[1], prm[2], prm[3]):
            gui_support.Messaggio.set("TCAN: OK")
        else:
            gui_support.Messaggio.set("TCAN: ERRORE")

    def _tcan_fine(self, prm):
        if self.dispo.tcan_fine(prm[1]):
            gui_support.Messaggio.set("TCAN: OK")
        else:
            gui_support.Messaggio.set("TCAN: ERRORE")

    def _tcan_tx(self, prm):
        if self.dispo.tcan_tx(prm[1], prm[2], prm[3], prm[4]):
            gui_support.Messaggio.set("TCAN: OK")
        else:
            gui_support.Messaggio.set("TCAN: ERRORE")

    def _tcan_rx(self, prm):
        rx = self.dispo.tcan_rx(prm[1])
        if rx is None:
            gui_support.Messaggio.set("TCAN: ERRORE")
        elif not any(rx):
            gui_support.Messaggio.set("TCAN: OK (nessun messaggio)")
        else:
            riga = ""
            can_id = rx["id"]
            if can_id & (1 << 31):
                riga += "ext {:08X}".format(can_id & _MASK_EXT)
            else:
                riga += "std {:04X}".format(can_id & _MASK_STD)

            msg = rx["msg"]
            if any(msg):
                quasi = "".join("{:02X} ".format(x) for x in msg)
                riga += " = " + quasi[: len(quasi) - 1]

            gui_support.rx_dati.set(riga)

            gui_support.Messaggio.set("TCAN: OK")

    def _tcan_reg_l(self, prm):
        val = self.dispo.tcan_reg_leggi(prm[1], prm[2], prm[3])
        if val is None:
            gui_support.Messaggio.set("TCAN REG: ERRORE")
        else:
            indir = prm[3]
            valori = []
            for elem in val:
                valori.append("{:04X} = {:08X}".format(indir, elem))
                indir += 4

            self._manda_alla_grafica(("canfd", valori))

    def _tcan_reg_s(self, prm):
        if self.dispo.tcan_reg_scrivi(prm[1], prm[2], prm[3]):
            gui_support.Messaggio.set("TCAN REG: OK")
        else:
            gui_support.Messaggio.set("TCAN REG: ERRORE")


class TCAN_DISPO:
    def __init__(self):
        pass

    def tcan_iniz(self, chi: int, nrml, data=None):
        prm = struct.pack("<4BI", chi, nrml[0], nrml[1], nrml[2], nrml[3])
        if data is not None:
            prm2 = struct.pack("<3BI", data[0], data[1], data[2], data[3])
            prm += prm2
        return self.prot.cmdPrmVoid(0x0701, prm)

    def tcan_fine(self, chi: int):
        prm = struct.pack("<B", chi)
        return self.prot.cmdPrmVoid(0x0702, prm)

    def tcan_tx(self, chi: int, esteso, ident, dati):
        if esteso:
            ident |= 1 << 31

        prm = struct.pack("<BI", chi, ident)
        if dati is not None:
            if any(dati):
                prm += dati
        return self.prot.cmdPrmVoid(0x0703, prm)

    def tcan_rx(self, chi: int):
        prm = struct.pack("<B", chi)
        risp = self.prot.cmdPrmRsp(0x0704, prm)
        try:
            rx = {}
            dati = risp["prm"]
            if not any(dati):
                # Nessun pacchetto
                pass
            else:
                xxx = struct.unpack("<I", dati[:4])
                rx["id"] = xxx[0]
                rx["msg"] = dati[4:]
            return rx
        except KeyError:
            return None

    def tcan_reg_leggi(self, chi: int, numreg, primo):
        prm = struct.pack("<B2H", chi, numreg, primo)
        rsp = self.prot.cmdPrmRsp(0x0705, prm, numreg * 4)
        try:
            val = rsp["prm"]
            lval = []

            try:
                while True:
                    x = struct.unpack("<I", val[:4])
                    lval.append(x[0])
                    val = val[4:]
            except struct.error:
                pass

            return lval

        except KeyError:
            return None

    def tcan_reg_scrivi(self, chi: int, primo, dati):
        numreg = 0
        vval = bytearray()
        for unval in dati:
            val = struct.pack("<I", unval)
            vval += val
            numreg += 1
        prm = struct.pack("<B2H", chi, numreg, primo)
        prm += vval
        return self.prot.cmdPrmVoid(0x0706, prm)
