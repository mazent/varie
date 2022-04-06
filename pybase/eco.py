#! /usr/bin/env python

"""
    Racchiude tutto quanto serve per la prova dell'eco
    L'applicazione deve avere:
        *) Un bottone per iniziare e terminare la prova
        *) Una edit col numero di prove
        *) Una edit col numero di byte per prova
        *) Una etichetta per i messaggi
        *) Una progressbar
        *) Una coda dove inviare i messaggi di aggiornamento grafica ...
        *) ... e le funzioni che gestiscono i messaggi:
              *) ecoFinePerErrore(quanti)
              *) ecoInfinito()
              *) ecoFinito(quanti)
           Queste funzioni devono invocare quelle omonime dell'oggetto passando
           il dispositivo
    Esempio: https://svnad.italia.texa.org/FW/TMDS/540-MK0/trunk/SC673_U8/host
"""

import random
import threading
import time

import utili


class ECO:

    def __init__(self, bottone,
                 numeco,
                 dimeco,
                 msg,
                 progBar,
                 coda):
        self.bottone = bottone
        self.numEco = numeco
        self.dimEco = dimeco
        self.msg = msg
        self.progBar = progBar
        self.coda = coda

        self.continuaEco = False

        self.ecoConta = 0
        self.ecoTot = 0
        self.crono = utili.CRONOMETRO()
        self.ecoMux = threading.Lock()
        self.ecoQuanti = 0

        self.timerEco = None
        self.durataTimer = None

        self.testo = self.bottone["text"]

        self.ecoLimite = 256
        self.dati = None

        self.ecoFnFinePerErrore = "ecoFinePerErrore"
        self.ecoFnInfinito = "ecoInfinito"
        self.ecoFnFinito = "ecoFinito"

        random.seed()

    def aggiornaEco(self):
        if self.continuaEco:
            self.ecoMux.acquire()
            durata = self.crono.durata()
            self.ecoMux.release()

            self.msg.set(utili.stampaDurata(int(round(durata * 1000.0, 0))))

            self.timerEco = self.bottone.after(
                self.durataTimer, self.aggiornaEco)
        else:
            self.bottone.after_cancel(self.timerEco)

    def cambia_funzioni(self, ecoFinePerErrore, ecoInfinito, ecoFinito):
        self.ecoFnFinePerErrore = ecoFinePerErrore
        self.ecoFnInfinito = ecoInfinito
        self.ecoFnFinito = ecoFinito

    def cambia_limite(self, nuovo):
        self.ecoLimite = nuovo

    def _crea_dati(self):
        dim = (self.ecoQuanti + 256 - 1) // 256
        self.dati = bytearray(range(256))
        dim -= 1

        while dim:
            self.dati += bytearray(range(256))
            dim -= 1

    # GUI

    def Bottone(self):
        if self.bottone["text"] == "Basta":
            self.continuaEco = False
            self.bottone.after_cancel(self.timerEco)
        else:
            esito, quanti = utili.validaCampo(self.numEco.get(), None, None)
            if esito:
                self.continuaEco = True
                self.bottone["text"] = "Basta"

                self.msg.set("Aspetta ...")

                esito, dimeco = utili.validaCampo(self.dimEco.get(), 0, None)
                if not esito:
                    self.ecoQuanti = 0
                elif self.ecoLimite <= 0:
                    # Nessun limite
                    self.ecoQuanti = dimeco
                else:
                    if dimeco > self.ecoLimite:
                        self.ecoQuanti = self.ecoLimite
                        self.dimEco.set(self.ecoLimite)
                    else:
                        self.ecoQuanti = dimeco

                if self.ecoQuanti:
                    self._crea_dati()

                    # Imposto un timer per le prove lunghe
                    self.durataTimer = 60 * 1000
                    self.timerEco = self.bottone.after(
                        self.durataTimer, self.aggiornaEco)

                if quanti < 0:
                    self.coda.put((self.ecoFnFinePerErrore, self, 0 - quanti))
                elif quanti == 0:
                    self.coda.put((self.ecoFnInfinito, self))
                else:
                    self.coda.put((self.ecoFnFinito, self, quanti))

            else:
                self.msg.set("Quanti echi ???")

    # Esegui

    def _esegui(self, dispo):
        if self.ecoQuanti == 0:
            return dispo.eco()

        random.shuffle(self.dati)
        return dispo.eco(self.dati[:self.ecoQuanti])

    def _stampa_bene(self, durata, sdurata):
        milli = round(1000.0 * durata / self.ecoTot, 3)
        tput = round((self.ecoQuanti * self.ecoTot) / durata, 1)
        kib = round((self.ecoQuanti * self.ecoTot) / (durata * 1024), 1)
        self.msg.set(
            "Eco: OK %d in %s (%.3f ms = %.1f B/s = %.1f KiB/s)" %
            (self.ecoTot, sdurata, milli, tput, kib))

    def ecoFinePerErrore(self, quanti, dispo):
        self.progBar.start(10)

        self.ecoConta = 0
        self.ecoTot = 0

        self.crono.conta()
        while self.ecoConta < quanti and self.continuaEco:
            self.ecoMux.acquire()
            self.ecoTot += 1

            if not self._esegui(dispo):
                self.ecoConta += 1
            self.ecoMux.release()

        self.continuaEco = False
        durata = self.crono.durata()
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if self.ecoConta == 0:
            self._stampa_bene(durata, sdurata)
        else:
            self.msg.set(
                "Eco: %d errori su %d [%s]" %
                (self.ecoConta, self.ecoTot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo

    def ecoInfinito(self, dispo):
        self.progBar.start(10)

        self.ecoConta = 0
        self.ecoTot = 0

        self.crono.conta()
        while self.continuaEco:
            self.ecoMux.acquire()
            self.ecoTot += 1

            if self._esegui(dispo):
                self.ecoConta += 1
            self.ecoMux.release()

        durata = self.crono.durata()
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if self.ecoConta == self.ecoTot:
            self._stampa_bene(durata, sdurata)
        elif self.ecoConta == 0:
            self.msg.set("Eco: ERR %d in %s" % (self.ecoTot, sdurata))
        else:
            self.msg.set(
                "Eco: OK %d / %d in %s" %
                (self.ecoConta, self.ecoTot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo

    def ecoFinito(self, quanti, dispo):
        self.progBar.start(10)

        self.ecoConta = 0
        self.ecoTot = 0

        self.crono.conta()
        while self.ecoTot < quanti and self.continuaEco:
            self.ecoMux.acquire()
            self.ecoTot += 1

            if self._esegui(dispo):
                self.ecoConta += 1
            self.ecoMux.release()

        self.continuaEco = False
        durata = self.crono.durata()
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if self.ecoConta == self.ecoTot:
            self._stampa_bene(durata, sdurata)
        elif self.ecoConta == 0:
            self.msg.set("Eco: ERR %d in %s" % (self.ecoTot, sdurata))
        else:
            self.msg.set(
                "Eco: OK %d / %d in %s" %
                (self.ecoConta, self.ecoTot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo
