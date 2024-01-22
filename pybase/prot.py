"""
    Protocollo di comunicazione con la SC637

    Il protocollo e' cosi' composto:
        0xII    Inizio trama
        0xDD    Destinatario
        0xMM    Mittente
        0xCCMD  Codice comando (little endian)
        ???     Eventuali dati
        0xCRCC  crc ccitt
        0xFF    Fine trama
"""

import struct

import serial
import crcmod

import utili


class PROT():
    _BAUD = 921600
    _CRC_INI = 0xC777
    _INIZIO_TRAMA = 0xC5
    _FINE_TRAMA = 0xC2
    _CARATTERE_DI_FUGA = 0xCF

    def __init__(self, io=0, altro=2, timeout=1, **cosa):
        self.io = io
        self.altro = altro
        if "porta" in cosa:
            # Apro come seriale
            try:
                self.uart = serial.Serial(
                    cosa["porta"],
                    PROT._BAUD,
                    serial.EIGHTBITS,
                    serial.PARITY_NONE,
                    serial.STOPBITS_ONE,
                    timeout,
                    rtscts=True,
                )
                self.prm = self.uart.getSettingsDict()
            except serial.SerialException as err:
                print(err)
                self.uart = None
            except ValueError as err:
                print(err)
                self.uart = None
        else:
            # Apro come usb
            try:
                self.uart = serial.serial_for_url(
                    "hwgrep://%s:%s" % (cosa["vid"], cosa["pid"]),
                    baudrate=PROT._BAUD,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=timeout,
                    rtscts=True,
                )
                self.prm = self.uart.getSettingsDict()
            except serial.SerialException as err:
                print(err)
                self.uart = None

    def __del__(self):
        self.chiudi()

    def a_posto(self):
        return self.uart is not None

    def chiudi(self):
        if self.uart is not None:
            self.uart.close()
            self.uart = None

    def cambia(self, baud=None, tempo=None):
        imp = self.uart.getSettingsDict()
        if baud is not None:
            imp["baudrate"] = baud
        if tempo is not None:
            imp["timeout"] = tempo
        self.uart.applySettingsDict(imp)

    def ripristina(self):
        self.uart.applySettingsDict(self.prm)

    @staticmethod
    def _aggiungi(dove, cosa):
        if cosa in (PROT._INIZIO_TRAMA, PROT._FINE_TRAMA, PROT._CARATTERE_DI_FUGA):
            dove.append(PROT._CARATTERE_DI_FUGA)
            dove.append((~cosa) & 0xFF)
        else:
            dove.append(cosa)

    # ============================================
    # Ispeziona quanto ricevuto
    # ============================================

    @staticmethod
    def _esamina(dati):
        msg = {}

        # almeno: dst + mit + cmd
        if len(dati) < 1 + 1 + 2:
            pass
        else:
            intest = struct.unpack("<BBH", dati[:4])
            msg["dst"] = intest[0]
            msg["mit"] = intest[1]
            msg["cmd"] = intest[2]
            msg["prm"] = dati[4:]

        return msg

    # nei comandi con tanti dati da trasmettere, calcola la
    # dimensione massima
    def max_dim(self, cmd, dati, maxdim):
        md = bytearray()

        tx = bytearray(struct.pack("<BBH", self.altro, self.io, cmd))
        for x in tx:
            self._aggiungi(md, x)

        dim = 0
        while len(md) < maxdim and dim < len(dati):
            self._aggiungi(md, dati[dim])
            dim += 1

        return dim

    # ============================================
    # Spedisce il messaggio aggiungendo la parte mancante
    # ============================================

    def _trasmetti(self, msg):
        crc = crcmod.Crc(0x11021, PROT._CRC_INI, False, 0x0000)
        crc.update(msg)
        msgcrc = bytes(crc.digest())

        # Compongo il pacchetto
        pkt = bytearray([PROT._INIZIO_TRAMA])

        for x in msg:
            self._aggiungi(pkt, x)

        self._aggiungi(pkt, msgcrc[0])
        self._aggiungi(pkt, msgcrc[1])

        pkt.append(PROT._FINE_TRAMA)

        # print("TX[{}] ".format(len(pkt)) + utili.stringa_da_ba(pkt, ' '))

        # Trasmetto
        self.uart.flushInput()
        self.uart.write(pkt)

        return True

    # ============================================
    # Restituisce il messaggio ricevuto o un bytearray vuoto
    # ============================================

    def _ricevi(self):
        pkt = bytearray()
        nega = False
        trovato = False
        # Mi aspetto almeno: inizio + dst + mit + comando + crc + fine
        daLeggere = 1 + 1 + 1 + 2 + 2 + 1
        tot = 0
        while not trovato:
            letti = bytearray(self.uart.read(daLeggere))
            tot += len(letti)
            if len(letti) == 0:
                break
            for rx in letti:
                if nega:
                    rx = ~rx & 0xFF
                    pkt.append(rx)
                    nega = False
                elif PROT._INIZIO_TRAMA == rx:
                    pkt = bytearray()
                elif PROT._FINE_TRAMA == rx:
                    # almeno: dst + mit + comando + crc
                    if len(pkt) >= 1 + 1 + 2 + 2:
                        crc = crcmod.Crc(0x11021, PROT._CRC_INI, False, 0x0000)
                        crc.update(pkt)
                        msgcrc = bytes(crc.digest())
                        if msgcrc[0] == msgcrc[1] == 0:
                            # tolgo crc
                            del pkt[-1]
                            del pkt[-1]

                            trovato = True
                elif PROT._CARATTERE_DI_FUGA == rx:
                    nega = True
                else:
                    pkt.append(rx)
            daLeggere = self.uart.inWaiting()
            if daLeggere == 0:
                daLeggere = 1

        if not trovato:
            pkt = bytearray()

        # print('rx {} -> {}'.format(tot, len(pkt)))

        return pkt

    # ============================================
    # Comando senza parametri e senza risposta
    # ============================================

    def cmdVoidVoid(self, cmd):
        rsp = False

        tx = bytearray(struct.pack("<BBH", self.altro, self.io, cmd))

        if not self._trasmetti(tx):
            pass
        else:
            msg = self._esamina(self._ricevi())
            try:
                risp = cmd | 0x8000
                if risp != msg["cmd"]:
                    raise utili.PROBLEMA("comando non eseguito")

                if self.io != msg["dst"]:
                    raise utili.PROBLEMA("risposta a dst scono")

                if self.altro != msg["mit"]:
                    raise utili.PROBLEMA("risposta da mit scono")

                # ok
                rsp = True
            except KeyError:
                pass
            except utili.PROBLEMA as err:
                print(err)

        return rsp

    # ============================================
    # Comando con parametri e senza risposta
    # ============================================

    def cmdPrmVoid(self, cmd, prm):
        rsp = False

        tx = bytearray(struct.pack("<BBH", self.altro, self.io, cmd))
        tx += prm

        if not self._trasmetti(tx):
            pass
        else:
            msg = self._esamina(self._ricevi())
            try:
                risp = cmd | 0x8000
                if risp != msg["cmd"]:
                    raise utili.PROBLEMA("comando non eseguito")

                if self.io != msg["dst"]:
                    raise utili.PROBLEMA("risposta a dst scono")

                if self.altro != msg["mit"]:
                    raise utili.PROBLEMA("risposta da mit scono")

                # ok
                rsp = True
            except KeyError:
                pass
            except utili.PROBLEMA as err:
                print(err)

        return rsp

    # ============================================
    # Comando senza parametri ma con risposta
    # ============================================

    def cmdVoidRsp(self, cmd, dim=None):
        rsp = {}

        tx = bytearray(struct.pack("<BBH", self.altro, self.io, cmd))

        if not self._trasmetti(tx):
            pass
        else:
            msg = self._esamina(self._ricevi())
            try:
                risp = cmd | 0x8000
                if risp != msg["cmd"]:
                    raise utili.PROBLEMA("comando non eseguito")

                if self.io != msg["dst"]:
                    raise utili.PROBLEMA("risposta a dst scono")

                if self.altro != msg["mit"]:
                    raise utili.PROBLEMA("risposta da mit scono")

                if dim is not None:
                    if len(msg["prm"]) != dim:
                        raise utili.PROBLEMA("dimensione sbagliata")

                # ok
                rsp = msg
            except KeyError:
                rsp = {}
            except utili.PROBLEMA as err:
                print(err)
                rsp = {}

        return rsp

    # ============================================
    # Comando con parametri e risposta
    # ============================================

    def cmdPrmRsp(self, cmd, prm, dim=None):
        rsp = {}

        tx = bytearray(struct.pack("<BBH", self.altro, self.io, cmd))
        tx += prm

        if not self._trasmetti(tx):
            pass
        else:
            msg = self._esamina(self._ricevi())
            try:
                risp = cmd | 0x8000
                if risp != msg["cmd"]:
                    raise utili.PROBLEMA("comando non eseguito")

                if self.io != msg["dst"]:
                    raise utili.PROBLEMA("risposta a dst scono")

                if self.altro != msg["mit"]:
                    raise utili.PROBLEMA("risposta da mit scono")

                if dim is not None:
                    if len(msg["prm"]) != dim:
                        raise utili.PROBLEMA("dimensione sbagliata")

                # ok
                rsp = msg
            except KeyError:
                rsp = {}
            except utili.PROBLEMA as err:
                print(err)
                rsp = {}

        return rsp
