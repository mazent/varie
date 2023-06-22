import struct

import gui_support
import utili


class UART_GUI:
    def __init__(self):
        self.ButtonUartChiudi.configure(command=self._ButtonUartChiudi)
        self.ButtonUartApri.configure(command=self._ButtonUartApri)
        self.ButtonUartTx.configure(command=self._ButtonUartTx)
        self.ButtonUartRx.configure(command=self._ButtonUartRx)

        gui_support.uartX.set(1)

    def _ButtonUartChiudi(self):
        udiag = int(gui_support.uartX.get())
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("udc", udiag))

    def _ButtonUartApri(self):
        udiag = int(gui_support.uartX.get())
        esito, baud = utili.validaCampo(gui_support.baud.get(), 100, 115200)
        if esito:
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("uda", udiag, baud))
        else:
            gui_support.Messaggio.set("? baud ?")

    def _ButtonUartTx(self):
        udiag = int(gui_support.uartX.get())
        msg = utili.ba_da_stringa(gui_support.tx_dati.get(), " ")
        if msg is None:
            gui_support.Messaggio.set("? dati ?")
        else:
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("udt", udiag, msg))

    def _ButtonUartRx(self):
        udiag = int(gui_support.uartX.get())
        gui_support.rx_dati.set("???")
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("udr", udiag))


class UART_EXE:
    def __init__(self):
        self.comando["udc"] = self._ud_chiudi
        self.comando["uda"] = self._ud_apri
        self.comando["udt"] = self._ud_tx
        self.comando["udr"] = self._ud_rx

    def _ud_chiudi(self, prm):
        if self.dispo.udiag_chiudi(prm[1]):
            gui_support.Messaggio.set("Chiusura uart diagnosi: BENE")
        else:
            gui_support.Messaggio.set("Chiusura uart diagnosi: MALE")

    def _ud_apri(self, prm):
        if self.dispo.udiag_apri(prm[1], prm[2]):
            gui_support.Messaggio.set("Apertura uart diagnosi: BENE")
        else:
            gui_support.Messaggio.set("Apertura uart diagnosi: MALE")

    def _ud_tx(self, prm):
        if self.dispo.udiag_tx(prm[1], prm[2]):
            gui_support.Messaggio.set("Trasmissione uart diagnosi: BENE")
        else:
            gui_support.Messaggio.set("Trasmissione uart diagnosi: MALE")

    def _ud_rx(self, prm):
        roba = self.dispo.udiag_rx(prm[1])
        if roba is None:
            gui_support.Messaggio.set("Ricezione uart diagnosi: MALE")
        else:
            try:
                gui_support.rx_dati.set(utili.stringa_da_ba(roba["msg"], " "))
            except KeyError:
                gui_support.rx_dati.set("nessun messaggio")
            gui_support.Messaggio.set("Ricezione uart diagnosi: BENE")


class UART_DISPO:
    def __init__(self):
        pass

    def udiag_chiudi(self, quale):
        return self.prot.cmdPrmVoid(0x0451, bytes([quale]))

    def udiag_apri(self, quale, baud):
        prm = struct.pack("<BI", quale, baud)
        return self.prot.cmdPrmVoid(0x0452, prm)

    def udiag_tx(self, quale, msg):
        prm = bytearray([quale])
        prm += msg
        return self.prot.cmdPrmVoid(0x0453, prm)

    def udiag_rx(self, quale):
        rsp = self.prot.cmdPrmRsp(0x0454, bytes([quale]))
        try:
            dati = rsp["prm"]
            if len(dati) == 0:
                # nessun messaggio dalla uart
                return {}
            return {"msg": dati}
        except KeyError:
            return None
