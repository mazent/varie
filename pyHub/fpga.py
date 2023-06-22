import hashlib
import struct

import gui_support
import utili

DESC_IND_FPGA = [
    "0x32 protocolli",
    "0x33 instradamento PTX",
    "0x34 versione",
    "0x23 instradamento CH 1",
    "0x22 instradamento CH 2",
]

IND_FPGA = (0x32 << 1, 0x33 << 1, 0x34 << 1, 0x23 << 1, 0x22 << 1)


class FPGA_GUI:
    def __init__(self):
        self.ComboRegFpga["values"] = DESC_IND_FPGA
        self.ComboRegFpga.current(0)

        self.ButtonFpgaInvia.configure(command=self._ButtonFpgaInvia)
        self.ButtonFpgaVerifica.configure(command=self._ButtonFpgaVerifica)
        self.ButtonFpgaConfig.configure(command=self._ButtonFpgaConfig)
        self.ButtonFpgaLeggi.configure(command=self._ButtonFpgaLeggi)
        self.ButtonFpgaScrivi.configure(command=self._ButtonFpgaScrivi)

    def _ButtonFpgaInvia(self):
        filename = utili.scegli_file_esistente(self.master, [("fpga", ".bit")])

        if filename is None:
            gui_support.Messaggio.set("? hai cambiato idea ?")
        elif not any(filename):
            gui_support.Messaggio.set("? hai cambiato idea ?")
        else:
            gui_support.fileFPGA.set(filename)
            gui_support.shaFILE.set("---")
            gui_support.dimFILE.set("---")
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("invia_fpga", filename))

    def _ButtonFpgaVerifica(self):
        esito, dim = utili.validaCampo(gui_support.dimFPGA.get(), 1)
        if esito:
            gui_support.shaFPGA.set("---")
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("verifica_fpga", dim))
        else:
            gui_support.Messaggio.set("? quanti byte ?")

    def _ButtonFpgaConfig(self):
        esito, dim = utili.validaCampo(gui_support.dimFILE.get(), 1024)
        if esito:
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("programma_fpga", dim))
        else:
            gui_support.Messaggio.set("? quanti byte ?")

    def _ButtonFpgaLeggi(self):
        indice = self.ComboRegFpga.current()
        if 0 <= indice <= len(IND_FPGA):
            ind = IND_FPGA[indice]

            gui_support.valFPGA.set("---")
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("leggi_fpga", ind))
        else:
            gui_support.Messaggio.set("? cosa ?")

    def _ButtonFpgaScrivi(self):
        try:
            indice = self.ComboRegFpga.current()
            if not 0 <= indice <= len(IND_FPGA):
                raise utili.problema("? indirizzo ?")

            ind = IND_FPGA[indice]

            esito, val = utili.validaCampo(gui_support.valFPGA.get(), 0, 0xFFFF)
            if not esito:
                raise utili.problema("? valore ?")

            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("scrivi_fpga", ind, val))

        except utili.problema as err:
            gui_support.Messaggio.set(err)


class FPGA_EXE:
    def __init__(self):
        self.comando["invia_fpga"] = self._invia_fpga
        self.comando["verifica_fpga"] = self._verifica_fpga
        self.comando["programma_fpga"] = self._programma_fpga
        self.comando["leggi_fpga"] = self._leggi_fpga
        self.comando["scrivi_fpga"] = self._scrivi_fpga

    def _invia_fpga(self, prm):
        dati = None
        with open(prm[1], "rb") as ing:
            dati = ing.read()

        if dati is not None:
            gui_support.dimFILE.set(len(dati))

            asc = hashlib.sha1()
            asc.update(dati)
            gui_support.shaFILE.set(asc.hexdigest().upper())

            try:
                pos = 0
                DIM = len(dati)
                gui_support.progFPGA.set(0)

                tempo = utili.CRONOMETRO()
                tempo.conta()

                while any(dati):
                    esito, dim = self.dispo.fpga_invia(pos, dati)
                    if esito:
                        dati = dati[dim:]
                        pos += dim
                        gui_support.progFPGA.set(100 * pos // DIM)
                    else:
                        raise utili.problema("err")

                fine = tempo.durata()
                tp = int(DIM / fine)
                fine *= 1000

                gui_support.progFPGA.set(100)
                gui_support.dimFPGA.set(gui_support.dimFILE.get())
                gui_support.Messaggio.set(
                    "FPGA: OK ({} = {} B/s)".format(utili.stampaDurata(fine), tp)
                )
            except utili.problema:
                gui_support.Messaggio.set("FPGA: ERRORE")
        else:
            gui_support.Messaggio.set("FPGA: ERRORE FILE")

    def _verifica_fpga(self, prm):
        sha = self.dispo.fpga_sha1(prm[1])
        if sha is not None:
            gui_support.shaFPGA.set(sha)
            gui_support.Messaggio.set("FPGA: OK")
        else:
            gui_support.Messaggio.set("FPGA: ERRORE")

    def _programma_fpga(self, prm):
        self.dispo.Cambia(tempo=60)

        tempo = utili.CRONOMETRO()
        tempo.conta()

        if self.dispo.fpga_programma(prm[1]):
            fine = tempo.durata()
            tp = int(prm[1] / fine)
            fine *= 1000

            gui_support.Messaggio.set(
                "FPGA: OK ({} = {} B/s)".format(utili.stampaDurata(fine), tp)
            )
        else:
            gui_support.Messaggio.set("FPGA: ERRORE")

        self.dispo.Ripristina()

    def _leggi_fpga(self, prm):
        val = self.dispo.fpga_leggi(prm[1])
        if val is None:
            gui_support.Messaggio.set("FPGA: ERRORE")
        else:
            gui_support.valFPGA.set("0x{:04X}".format(val))
            gui_support.Messaggio.set("FPGA: OK")

    def _scrivi_fpga(self, prm):
        if self.dispo.fpga_scrivi(prm[1], prm[2]):
            gui_support.Messaggio.set("FPGA: OK")
        else:
            gui_support.Messaggio.set("FPGA: ERRORE")


class FPGA_DISPO:
    def __init__(self):
        pass

    def fpga_invia(self, pos, dati):
        prm = bytearray(struct.pack("<I", pos))

        # dim = min(DISPOSITIVO._DIM_DATI_CMD - 4, len(dati))
        dim = self.prot.max_dim(0x0201, dati, self.DIM_DATI_CMD)
        prm += dati[:dim]

        return self.prot.cmdPrmVoid(0x0201, prm), dim

    def fpga_sha1(self, dim):
        prm = struct.pack("<I", dim)
        rsp = self.prot.cmdPrmRsp(0x0202, prm, 20)
        try:
            val = rsp["prm"]
            sha = ""
            for ottetto in val:
                sha += "{:02X}".format(ottetto)

            return sha
        except KeyError:
            return None

    def fpga_programma(self, dim):
        prm = struct.pack("<I", dim)
        return self.prot.cmdPrmVoid(0x0203, prm)

    def fpga_leggi(self, ind):
        prm = struct.pack("<B", ind)
        rsp = self.prot.cmdPrmRsp(0x0204, prm, 2)
        try:
            tmp = rsp["prm"]

            val = struct.unpack("<H", tmp)

            return val[0]
        except KeyError:
            return None

    def fpga_scrivi(self, ind, val):
        prm = struct.pack("<BH", ind, val)
        return self.prot.cmdPrmVoid(0x0205, prm)
