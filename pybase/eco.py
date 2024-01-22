#! /usr/bin/env python

"""
    Racchiude tutto quanto serve per la prova dell'eco
    L'applicazione deve avere:
        *) Un bottone per iniziare e terminare la prova (deve invocare Bottone())
           p.e.
                self.Button5.configure(command=self._ecoProva)
                ...
                def _ecoProva(self):
                    self.eco.Bottone()
        *) Una edit col numero di prove
        *) Una edit col numero di byte per prova
        *) Una etichetta per i messaggi
        *) Una progressbar
        *) La funzione che implementa l'eco vero e proprio: riceve i
           dati da trasmettere (o niente) e restituisce l'esito (bool)
        *) Una coda dove inviare il messaggio di fine prova (opzionale):
                msgFineEco
           Il messaggio puo' essere cambiato con: cambia_messaggi()

    Ricordarsi di chiudere:
        eco.esci()

    Quindi:
        self.eco = eco.ECO(self.Button5,
                           gui_support.numEco,
                           gui_support.dimEco,
                           gui_support.Messaggio,
                           self.TProgressbar1,
                           self._un_eco)
        self.eco.cambia_limite(dispo.DISPO.DIM_DATI_CMD)

"""

import random
import threading
import queue as coda

import utili

MSG_FINE_X_ERRORE = "fine x errore"
MSG_INFINITO = "prova infinita"
MSG_FINITO = "provane un tot"


class ECO(threading.Thread):
    def __del__(self):
        self.esci()

    def __init__(self, bottone,
                 numeco,
                 dimeco,
                 msg,
                 progBar,
                 fn,
                 coda_fine=None):
        # salvo i parametri
        self.bottone = bottone
        self.numEco = numeco
        self.dimEco = dimeco
        self.msg = msg
        self.progBar = progBar
        self.funz_eco = fn
        self.codaf = coda_fine

        # thd
        self.codat = coda.Queue()
        self.thd = False

        # per le prove
        self.continua = False

        self.crono = utili.CRONOMETRO()
        self.ecoQuanti = 0

        self.timerEco = None

        self.testo = self.bottone["text"]

        self.ecoLimite = 256
        self.dati = None

        # personalizzabile
        self.msgFineEco = "ecoFineProva"

        random.seed()

        threading.Thread.__init__(self)
        self.start()

    def _esci(self, _):
        raise utili.Problema("fine")

    def run(self):
        FUNZ = {
            MSG_FINE_X_ERRORE: self._fine_x_errore,
            MSG_INFINITO: self._Infinito,
            MSG_FINITO: self._Finito,
            "esci": self._esci,
        }
        self.thd = True
        while True:
            try:
                msg = self.codat.get()
                FUNZ[msg[0]](msg[1])
            except utili.Problema:
                break
        self.thd = False

    def esci(self):
        if self.thd:
            self.codat.put(("esci", 0))
            self.join()

    def _msg_durata(self):
        if self.continua:
            durata = self.crono.durata()
            self.msg.set(utili.stampaDurata(int(round(durata * 1000.0, 0))))

    def cambia_messaggi(self, ecoFineProva):
        self.msgFineEco = ecoFineProva

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
            self.continua = False
            self.timerEco.termina()
        else:
            esito, quanti = utili.validaCampo(self.numEco.get(), None, None)
            if esito:
                self.continua = True
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
                self.timerEco = utili.Periodico(self._msg_durata)
                self.timerEco.avvia(60)

                if quanti < 0:
                    self.codat.put((MSG_FINE_X_ERRORE, 0 - quanti))
                elif quanti == 0:
                    self.codat.put((MSG_INFINITO, 0))
                else:
                    self.codat.put((MSG_FINITO, quanti))
            else:
                self.msg.set("Quanti echi ???")

    # Esecuzione

    def _esegui(self):
        if self.ecoQuanti == 0:
            return self.funz_eco()

        random.shuffle(self.dati)
        return self.funz_eco(self.dati[: self.ecoQuanti])

    def _stampa_bene(self, totale, durata, sdurata):
        milli = round(1000.0 * durata / totale, 3)
        tput = round((self.ecoQuanti * totale) / durata, 1)
        kib = round((self.ecoQuanti * totale) / (durata * 1024), 1)
        self.msg.set(
            "Eco: OK %d in %s (%.3f ms = %.1f B/s = %.1f KiB/s)"
            % (totale, sdurata, milli, tput, kib)
        )

    def _fine_x_errore(self, quanti):
        self.progBar.start(10)

        conta = 0
        tot = 0

        self.crono.conta()
        while conta < quanti and self.continua:
            tot += 1

            if not self._esegui():
                conta += 1

        durata = self.crono.durata()
        self.continua = False
        self.timerEco.termina()
        del self.timerEco
        self.timerEco = None
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if conta == 0:
            self._stampa_bene(tot, durata, sdurata)
        else:
            self.msg.set("Eco: %d errori su %d [%s]" % (conta, tot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo
        if self.codaf is not None:
            self.codaf.put((self.msgFineEco,))

    def _Infinito(self, _):
        self.progBar.start(10)

        conta = 0
        tot = 0

        self.crono.conta()
        while self.continua:
            tot += 1

            if self._esegui():
                conta += 1

        durata = self.crono.durata()
        self.timerEco.termina()
        del self.timerEco
        self.timerEco = None
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if conta == tot:
            self._stampa_bene(tot, durata, sdurata)
        elif conta == 0:
            self.msg.set("Eco: ERR %d in %s" % (tot, sdurata))
        else:
            self.msg.set("Eco: OK %d / %d in %s" % (conta, tot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo
        if self.codaf is not None:
            self.codaf.put((self.msgFineEco,))

    def _Finito(self, quanti):
        self.progBar.start(10)

        conta = 0
        tot = 0

        self.crono.conta()
        while tot < quanti and self.continua:
            tot += 1

            if self._esegui():
                conta += 1

        durata = self.crono.durata()
        self.continua = False
        self.timerEco.termina()
        del self.timerEco
        self.timerEco = None
        sdurata = utili.stampaDurata(int(round(durata * 1000.0, 0)))

        if conta == tot:
            self._stampa_bene(tot, durata, sdurata)
        elif conta == 0:
            self.msg.set("Eco: ERR %d in %s" % (tot, sdurata))
        else:
            self.msg.set("Eco: OK %d / %d in %s" % (conta, tot, sdurata))

        self.progBar.stop()
        self.bottone["text"] = self.testo
        if self.codaf is not None:
            self.codaf.put((self.msgFineEco,))
