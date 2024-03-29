#! /usr/bin/env python

"""
    Per non bloccare la grafica viene creato un task
    che aspetta i comandi e li esegue
"""

import threading

import gui_support
import utili


class Esecutore(threading.Thread):
    def __init__(self, codaEXE, codaGUI):
        threading.Thread.__init__(self)
        # o anche threading.Thread.__init__(self, daemon=True)

        self.sincro = {
            "exe": codaEXE,
            "gui": codaGUI,
        }

        self.dispo = None
        self.logger = utili.LOGGA()

        self.comando = {"eco": self._eco_e}

        self.start()

    def run(self):
        while True:
            lavoro = self.sincro["exe"].get()
            if lavoro[0] == "esci":
                break

            if lavoro[0] == "Logger":
                self.logger = utili.LOGGA("ESEGUI")
            elif lavoro[0] == "Dispositivo":
                self.dispo = lavoro[1]
                self.dispo.cambia_coda(self.sincro["gui"])
            elif not lavoro[0] in self.comando:
                pass
            else:
                self.comando[lavoro[0]](lavoro)

    def _manda_alla_grafica(self, x, y=None):
        if y is None:
            self.sincro["gui"].put((x,))
        else:
            self.sincro["gui"].put((x, y))

    # --------- VARIE ----------------------------------------------------------

    def _eco_e(self, _):
        if self.dispo.eco():
            gui_support.Messaggio.set("Eco: BENE")
        else:
            gui_support.Messaggio.set("Eco: MALE")
