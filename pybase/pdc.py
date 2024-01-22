"""
    Pompa di Comunicazione
"""

import threading
import queue
import struct
import logging

import serial
import crcmod
import utili

_T_MAX = 3


class _PROTO:
    _INIZIO_TRAMA = 0xC5
    _FINE_TRAMA = 0xC2
    _CARATTERE_DI_FUGA = 0xCF

    @staticmethod
    def _aggiungi(dove, cosa):
        if cosa in (
            _PROTO._INIZIO_TRAMA,
            _PROTO._FINE_TRAMA,
            _PROTO._CARATTERE_DI_FUGA,
        ):
            dove.append(_PROTO._CARATTERE_DI_FUGA)
            dove.append((~cosa) & 0xFF)
        else:
            dove.append(cosa)

    def _stato_0(self, rx):
        if rx == _PROTO._INIZIO_TRAMA:
            self.diario.info("inizio pacchetto")
            self.nega = False
            self.stato = 1
        else:
            self.diario.info("inizio riga")
            self.pkt.append(rx)
            self.stato = 2

        return False

    def _stato_1(self, rx):
        if self.nega:
            rx = ~rx & 0xFF
            self.pkt.append(rx)
            self.nega = False
        elif _PROTO._INIZIO_TRAMA == rx:
            self.pkt = bytearray()
        elif _PROTO._FINE_TRAMA == rx:
            # almeno: comando + crc
            if len(self.pkt) >= 2 + 2:
                crc = crcmod.Crc(0x11021, self.crc_ini, False, 0x0000)
                crc.update(self.pkt)
                msgcrc = bytes(crc.digest())
                if msgcrc[0] == msgcrc[1] == 0:
                    # tolgo crc
                    del self.pkt[-1]
                    del self.pkt[-1]

                    intest = struct.unpack("<H", self.pkt[:2])
                    self.rsp = {"tipo": "rsp", "cmd": intest[0], "rsp": self.pkt[2:]}

                    self.diario.info("pacchetto ok")

                    return True
                else:
                    self.diario.error("crc sbagliato")
            else:
                self.diario.error("pochi byte")

        elif _PROTO._CARATTERE_DI_FUGA == rx:
            self.nega = True
        else:
            self.pkt.append(rx)

        return False

    def _stato_2(self, rx):
        if rx == 0x0D:
            return False

        if rx == 0x0A:
            try:
                self.rsp = {"tipo": "riga", "riga": str(self.pkt.decode("ascii"))}
                self.diario.info("nuova riga")
                return True
            except UnicodeDecodeError:
                self.pkt = bytearray()
                return True

        self.pkt.append(rx)
        return False

    def __init__(self, crc_iniziale, logga=False):
        self.crc_ini = crc_iniziale

        self.diario = utili.LOGGA("proto" if logga else None)

        self.nega = False

        self.esamina = bytearray()
        self.rsp = None
        self.pkt = bytearray()

        self.stati = {0: self._stato_0, 1: self._stato_1, 2: self._stato_2}
        self.stato = 0

    def da_esaminare(self, dati):
        """
        salva i dati raccolti

        :param dati: bytearray raccolti
        :return: niente
        """
        self.esamina += dati

    def risposta(self):
        """
        esamina i dati salvati estraendo la risposta al comando
        o la riga del diario

        :return: None
                    oppure
                { 'tipo': 'riga', 'riga': str }
                    oppure
                { 'tipo': 'rsp', 'cmd': intero, 'rsp': bytearray }

        """
        while len(self.esamina):
            if self.stati[self.stato](self.esamina.pop(0)):
                self.pkt = bytearray()
                self.stato = 0
                break

        if self.rsp is not None:
            rsp = dict(self.rsp)
            del self.rsp
            self.rsp = None
            return rsp

        return None

    def crea_pkt(self, msg):
        """
        impacchetta il messaggio

        :param msg: bytearray contenente il messaggio
        :return: bytearray da trasmettere
        """
        crc = crcmod.Crc(0x11021, self.crc_ini, False, 0x0000)
        crc.update(msg)
        msgcrc = bytes(crc.digest())

        # Compongo il pacchetto
        pkt = bytearray([_PROTO._INIZIO_TRAMA])

        for x in msg:
            self._aggiungi(pkt, x)

        self._aggiungi(pkt, msgcrc[0])
        self._aggiungi(pkt, msgcrc[1])

        pkt.append(_PROTO._FINE_TRAMA)

        return pkt


class PdC(threading.Thread):
    """
    Pompa di Comunicazione:
        *) serializza la trasmissione dei comandi
        *) riceve righe e risposte
    """

    def __init__(self, baud, crc_ini, logga=False, hw_flow_ctrl=True, poll=0.1, **cosa):
        self.diario = utili.LOGGA("PDC" if logga else None)

        self.poll = poll
        self.proto = _PROTO(crc_ini, logga)

        self.mutex = threading.Lock()
        self.cmd_corr = None

        self.uart = None
        if "dev" in cosa:
            # Apro come seriale
            try:
                self.uart = serial.Serial(
                    cosa["dev"],
                    baudrate=baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    rtscts=hw_flow_ctrl,
                )
            except (serial.SerialException, ValueError) as err:
                self.diario.critical(str(err))
                self.uart = None
        else:
            # Apro come usb
            try:
                self.uart = serial.serial_for_url(
                    "hwgrep://%s:%s" % (cosa["vid"], cosa["pid"]),
                    baudrate=baud,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    rtscts=hw_flow_ctrl,
                )
            except serial.SerialException as err:
                self.diario.critical(str(err))
                self.uart = None

        if self.uart is not None:
            # posso girare
            self.coda_cmd = queue.Queue()
            threading.Thread.__init__(self)
            self.start()

    def a_posto(self):
        """
        invocare dopo la creazione per verificare se la porta e' stata aperta

        :return: bool
        """
        return self.uart is not None

    def _trasmetti(self):
        # mutex acquisito dal chiamante
        msg = bytearray(struct.pack("<H", self.cmd_corr["cmd"]))
        msg += self.cmd_corr["prm"]

        pkt = self.proto.crea_pkt(msg)
        self.diario.debug("TX", pkt)

        self.uart.write(pkt)

    def run(self):
        while True:
            # attesa comandi
            self.mutex.acquire()
            if self.cmd_corr is None:
                try:
                    cmd = self.coda_cmd.get(True, self.poll)

                    if cmd["cmd"] == 0xE5C1:
                        break

                    self.cmd_corr = cmd
                    self._trasmetti()

                except queue.Empty:
                    pass
            self.mutex.release()

            # polling della seriale
            letti = bytearray()
            while self.uart.in_waiting:
                tmp = self.uart.read(self.uart.in_waiting)
                self.proto.da_esaminare(tmp)
                letti += tmp
            if any(letti):
                self.diario.debug("RX", letti)

            # esamino il raccolto
            while True:
                rsp = self.proto.risposta()
                if rsp is None:
                    break

                if rsp["tipo"] == "riga":
                    self.riga_del_diario(rsp["riga"])
                    break

                if rsp["cmd"] & 0xC000 == 0:
                    self.evento(rsp["cmd"], rsp["rsp"])
                    break

                self.mutex.acquire()
                if self.cmd_corr is not None:
                    self.cmd_corr["rsp"].put_nowait(rsp)
                    self.cmd_corr = None
                else:
                    self.diario.error("comando nullo")
                self.mutex.release()

    def chiudi(self):
        """
        termina il ddd e chiude la seriale
        :return: Niente
        """
        if self.uart is not None:
            # ammazzo il ddd
            cmd = {
                "cmd": 0xE5C1,
            }
            self.coda_cmd.put_nowait(cmd)

            # aspetto
            self.join()

            # chiudo
            self.uart.close()
            self.uart = None

    def void_void(self, cmd, to=_T_MAX):
        """
        Comando senza parametri ne' risposta

        :param cmd: codice del comando (intero)
        :param to: timeout ricezione
        :return: bool
        """
        esito = queue.Queue()

        self.coda_cmd.put_nowait({"cmd": cmd, "prm": bytearray(), "rsp": esito})

        try:
            rsp = esito.get(True, to)
            if cmd | 0x8000 == rsp["cmd"]:
                return len(rsp["rsp"]) == 0

            if cmd | 0x4000 == rsp["cmd"]:
                self.diario.error("comando {:04X}: scono".format(cmd))
                return False

            self.diario.error("comando {:04X}: errore".format(cmd))
            return False

        except queue.Empty:
            self.diario.error("comando {:04X}: timeout".format(cmd))
            self.mutex.acquire()
            self.cmd_corr = None
            self.mutex.release()
            return False

    def prm_void(self, cmd, prm, to=_T_MAX):
        """
        Comando con parametri ma senza risposta

        :param cmd: codice del comando (intero)
        :param prm: bytearray contenente i parametri del comando
        :param to: timeout ricezione
        :return: bool
        """
        esito = queue.Queue()

        self.coda_cmd.put_nowait({"cmd": cmd, "prm": prm, "rsp": esito})

        try:
            rsp = esito.get(True, to)
            if cmd | 0x8000 == rsp["cmd"]:
                return len(rsp["rsp"]) == 0

            if cmd | 0x4000 == rsp["cmd"]:
                self.diario.error("comando {:04X}: scono".format(cmd))
                return False

            self.diario.error("comando {:04X}: errore".format(cmd))
            return False

        except queue.Empty:
            self.diario.error("comando {:04X}: timeout".format(cmd))
            self.mutex.acquire()
            self.cmd_corr = None
            self.mutex.release()
            return False

    def void_rsp(self, cmd, dim=None, to=_T_MAX):
        """
        Comando senza parametri ma con risposta

        :param cmd: codice del comando (intero)
        :param dim: dimensione attesa della risposta
        :param to: timeout ricezione
        :return: None in caso di errore, altrimenti il bytearray della risposta
        """
        esito = queue.Queue()

        self.coda_cmd.put_nowait({"cmd": cmd, "prm": bytearray(), "rsp": esito})

        try:
            rsp = esito.get(True, to)
            if cmd | 0x8000 == rsp["cmd"]:
                if dim is not None:
                    if len(rsp["rsp"]) != dim:
                        self.diario.error(
                            "comando {:04X}: dimensione sbagliata".format(cmd)
                        )
                        return None

                return rsp["rsp"]

            if cmd | 0x4000 == rsp["cmd"]:
                self.diario.error("comando {:04X}: scono".format(cmd))
                return None

            self.diario.error("comando {:04X}: errore".format(cmd))
            return None

        except queue.Empty:
            self.diario.error("comando {:04X}: timeout".format(cmd))
            self.mutex.acquire()
            self.cmd_corr = None
            self.mutex.release()
            return None

    def prm_rsp(self, cmd, prm, dim=None, to=_T_MAX):
        """
        Comando con parametri e risposta

        :param cmd: codice del comando (intero)
        :param prm: bytearray contenente i parametri del comando
        :param dim: dimensione attesa della risposta
        :param to: timeout ricezione
        :return: None in caso di errore, altrimenti il bytearray della risposta
        """
        esito = queue.Queue()

        self.coda_cmd.put_nowait({"cmd": cmd, "prm": prm, "rsp": esito})

        try:
            rsp = esito.get(True, to)
            if cmd | 0x8000 == rsp["cmd"]:
                if dim is not None:
                    if len(rsp["rsp"]) != dim:
                        self.diario.error(
                            "comando {:04X}: dimensione sbagliata".format(cmd)
                        )
                        return None
                return rsp["rsp"]

            if cmd | 0x4000 == rsp["cmd"]:
                self.diario.error("comando {:04X}: scono".format(cmd))
                return None

            self.diario.error("comando {:04X}: errore".format(cmd))
            return None

        except queue.Empty:
            self.diario.error("comando {:04X}: timeout".format(cmd))
            self.mutex.acquire()
            self.cmd_corr = None
            self.mutex.release()
            return None

    def riga_del_diario(self, riga):
        """
        metodo da overridere per ricevere le righe del diario

        :param riga: la riga del diario
        :return: niente
        """
        print(riga)

    def evento(self, evn, dati):
        """
        metodo da overridere per ricevere gli eventi

        :param evn: codice dell'evento
        :param dati: dell'evento
        :return: niente
        """
        sdati = ""
        if dati is None:
            pass
        elif len(dati) == 0:
            pass
        else:
            sdati = utili.stringa_da_ba(dati, " ")
        print("evento {:04X}: ".format(evn) + sdati)
