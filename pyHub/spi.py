import struct

import gui_support
import utili


class SPI_GUI:
    def __init__(self):
        self.ButtonSpiApri.configure(command=self._ButtonSpiApri)
        self.ButtonSpiChiudi.configure(command=self._ButtonSpiChiudi)
        self.ButtonSpiRx.configure(command=self._ButtonSpiRx)
        self.ButtonSpiTx.configure(command=self._ButtonSpiTx)
        self.ButtonSpiTxRx.configure(command=self._ButtonSpiTxRx)

        gui_support.espi_mode.set("0xA5")

    def _ButtonSpiApri(self):
        esito, freq = utili.validaCampo(gui_support.espi_freq.get(), 1, 32000000)
        if not esito:
            gui_support.Messaggio.set("? frequenza ?")
        else:
            modo = int(gui_support.espi_mode.get(), 0)

            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("espi_apri", modo, freq))

    def _ButtonSpiChiudi(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("espi_apri", 0, 0))

    def _ButtonSpiTx(self):
        dati = utili.esa_da_stringa(gui_support.tx_dati.get())
        if any(dati):
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("espi_tx", dati))
        else:
            gui_support.Messaggio.set("? dati ?")

    def _ButtonSpiRx(self):
        esito, dim = utili.validaCampo(gui_support.espi_dim.get(), 1, 100)
        if not esito:
            gui_support.Messaggio.set("? quanti bytes ?")
        else:
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("espi_rx", dim))

    def _ButtonSpiTxRx(self):
        dati = utili.esa_da_stringa(gui_support.tx_dati.get())
        if any(dati):
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("espi_xx", dati))
        else:
            gui_support.Messaggio.set("? dati ?")


class SPI_EXE:
    def __init__(self):
        self.comando["espi_apri"] = self._espi_apri
        self.comando["espi_tx"] = self._espi_tx
        self.comando["espi_rx"] = self._espi_rx
        self.comando["espi_xx"] = self._espi_xx

    def _espi_apri(self, prm):
        if self.dispo.espi_apri(prm[1], prm[2]):
            gui_support.Messaggio.set("SPI EXT: OK")
        else:
            gui_support.Messaggio.set("SPI EXT: ERRORE")

    def _espi_tx(self, prm):
        if self.dispo.espi_tx(prm[1]):
            gui_support.Messaggio.set("SPI EXT: OK")
        else:
            gui_support.Messaggio.set("SPI EXT: ERRORE")

    def _espi_rx(self, prm):
        rx = self.dispo.espi_rx(prm[1])
        if rx is None:
            gui_support.Messaggio.set("SPI EXT: ERRORE")
        else:
            quasi = "".join("{:02X} ".format(x) for x in rx)
            gui_support.rx_dati.set(quasi[: len(quasi) - 1])
            gui_support.Messaggio.set("SPI EXT: OK")

    def _espi_xx(self, prm):
        rx = self.dispo.espi_xx(prm[1])
        if rx is None:
            gui_support.Messaggio.set("SPI EXT: ERRORE")
        else:
            quasi = "".join("{:02X} ".format(x) for x in rx)
            gui_support.rx_dati.set(quasi[: len(quasi) - 1])
            gui_support.Messaggio.set("SPI EXT: OK")


class SPI_DISPO:
    def __init__(self):
        pass

    def espi_apri(self, modo, freq):
        prm = struct.pack("<BI", modo, freq)
        return self.prot.cmdPrmVoid(0x0440, prm)

    def espi_tx(self, cosa: bytearray):
        assert isinstance(cosa, bytearray)

        return self.prot.cmdPrmVoid(0x0441, cosa)

    def espi_rx(self, quanti):
        prm = struct.pack("<B", quanti)
        rsp = self.prot.cmdPrmRsp(0x0442, prm, quanti)
        try:
            return rsp["prm"]
        except KeyError:
            return None

    def espi_xx(self, cosa: bytearray):
        rsp = self.prot.cmdPrmRsp(0x0443, cosa, len(cosa))
        try:
            return rsp["prm"]
        except KeyError:
            return None
