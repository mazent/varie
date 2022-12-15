import struct
import datetime

import pdc
import utili


class DISPO(pdc.PdC):
    DIM_DATI_CMD = 100

    def __init__(self, logga=False, **argo):
        self.logger = utili.LOGGA('DISPO' if logga else None)

        self.coda = None

        pdc.PdC.__init__(self, 460800, 0xCCCC,logga=logga, **argo)

    def cambia_coda(self, usala):
        self.coda = usala

    # callback

    def riga_del_diario(self, riga):
        self.logger.info(riga)

        if self.coda is not None:
            adesso = datetime.datetime.now()
            sadesso = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:03.0f}: '.format(adesso.year, adesso.month,
                                                                                    adesso.day, adesso.hour,
                                                                                    adesso.minute, adesso.second,
                                                                                    adesso.microsecond / 1000.0)

            self.coda.put(('d_scrivi', sadesso + riga))

    def evento(self, evn, dati):
        if self.coda is not None:
            evento = {
                'cod': evn,
                'ora': datetime.datetime.now(),
                'dati': dati.decode('ascii')
            }

            self.coda.put(('evento', evento))

    # comandi

    def eco(self, dati=None):
        if dati is None:
            dati = utili.byte_casuali(utili.numero_casuale(self.DIM_DATI_CMD))

        self.logger.debug('eco {}'.format(len(dati)))
        eco = self.prm_rsp(0x0001, dati, dim=len(dati))
        if eco is None:
            return False
        return dati == eco
