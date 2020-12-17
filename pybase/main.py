#!/usr/bin/env python

"""
    Script principale
"""

import sys
try:
    import Queue as coda
except ImportError:
    import queue as coda

import gui
import gui_support

import esegui
import utili


NOME_UART = None
if sys.platform.startswith("win32"):
    NOME_UART = "COM"
else:
    NOME_UART = "/dev/tty"

TAB_CHIUSA = { 1: False }
TAB_APERTA = { 1: True }


class MAIN(gui.GUI):

    # da un certo punto in poi page butta tutto in gui_support, a me non piace,
    # preferisco ereditare ma, quando si aggiunge un bottone, bisogna lasciare il comando
    # vuoto e metterlo qua
    def _callback(self):
        # tasto che cambia operazione
        self.Button1.bind('<ButtonRelease-1>',self.apriSeriale)
        # tasto normale
        self.Button2.configure(command=self.Eco)
        # tasto che inizia/termina operazione (cfr self.evnFine)
        self.Button44.configure(command=self.bteco)
        

    def __init__(self, master=None):
        self.master = master
        gui.GUI.__init__(self, master)

        self.logger = None

        gui_support.portaSeriale.set(NOME_UART)

        self._callback()

        self._imposta_tab(TAB_CHIUSA)

        self.dispo = None
        
        # tasti che iniziano e terminano operazioni
        self.evnFine = threading.Event()

        # Code per la comunicazione fra grafica e ciccia
        self.codaEXE = coda.Queue()
        self.codaGUI = coda.Queue()

        self.task = esegui.Esecutore(self.codaEXE, self.codaGUI)

        self.eco = eco.ECO(self.Button3,
                           gui_support.numEco,
                           gui_support.Messaggio,
                           self.TProgressbar1,
                           self.codaEXE)

        # Comandi dall'esecutore
        self.cmd = {
            'fbteco': self._fine_bteco,
        }
        self._esegui_GUI()
        
    def _fine_bteco(self):
        # Il thd ha finito
        gui_support.Messaggio.set("qualcosa")
        
        # Il mio bottone e' riutilizzabile ...
        self.Button44['text'] = 'Eco'
        self.Button44['state'] = gui.tk.NORMAL

        # ... e anche quelli incompatibili
        self.Button15['state'] = gui.tk.NORMAL


    def __del__(self):
        pass

    def chiudi(self):
        self.codaEXE.put(("esci",))
        self.task.join()

        if self.dispo is not None:
            self.dispo.Chiudi()
            self.dispo = None

    def _imposta_tab(self, lista):
        for tab in lista:
            stato = 'disabled'
            if lista[tab]:
                stato = 'normal'

            self.TNotebook1.tab(tab, state=stato)

    def _esegui_GUI(self):
        try:
            msg = self.codaGUI.get(0)

            if msg[0] in self.cmd:
                if len(msg) == 2:
                    self.cmd[msg[0]](msg[1])
                else:
                    self.cmd[msg[0]]()
        except coda.Empty:
            pass

        self.master.after(300, self._esegui_GUI)

    # ---------- SERIALE ------------------------------------------------------

    def _apri_o_chiudi(self, svid, spid, bottone, testo, entry, bott1, bott2):
        if self.dispo is None:
            try:
                if svid is None and spid is None:
                    # apro una seriale 'normale'
                    porta = gui_support.portaSeriale.get()
                    if porta is None:
                        raise utili.problema('? che porta ?')
                    elif any(porta):
                        self.dispo = sc681.SC681(logga=self.logger is not None, uart=porta)
                    else:
                        raise utili.problema('? che porta ?')
                else:
                    # apro una seriale usb
                    self.dispo = sc681.SC681(logga=self.logger is not None, vid=svid, pid=spid)

                # se arrivo qua ho in mano il coso
                if not self.dispo.a_posto():
                    del self.dispo
                    self.dispo = None
                else:
                    self.eco.cambia_limite(self.dispo.DIM_DATI_CMD)
                    self.codaEXE.put(("Dispositivo", self.dispo))

                    bottone['text'] = 'Mollala'
                    entry['state'] = 'readonly'
                    bott1['state'] = 'disabled'
                    bott2['state'] = 'disabled'

                    self._imposta_tab(TAB_APERTA)

            except utili.Problema as err:
                print(err)
                gui_support.portaSeriale.set(NOME_UART)
        else:
            self.dispo.chiudi()
            self.dispo = None
            self.codaEXE.put(("Dispositivo", self.dispo))

            bottone['text'] = testo
            entry['state'] = 'normal'
            bott1['state'] = 'normal'
            bott2['state'] = 'normal'

            self._imposta_tab(TAB_CHIUSA)

    def apriUSB(self):
        self._apri_o_chiudi('04B4', 'F139', self.Button4, 'Usa USB', self.Entry1, self.Button47, self.Button1)

    def apriFTDI(self):
        self._apri_o_chiudi('0403', '6001', self.Button47, 'Usa FTDI',
                            self.Entry1, self.Button4, self.Button1)

    def apriSeriale(self):
        self._apri_o_chiudi(None, None, self.Button1, 'Usa questa', self.Entry1, self.Button47, self.Button4)

    # --------- VARIE ----------------------------------------------------------

    def bteco(self):
        if not self.evnFine.is_set():
            # Inizio
            self.evnFine.set()
            self.Button44['text'] = 'Basta'

            # eventuali operazioni incompatibili
            self.Button15['state'] = gui.tk.DISABLED

            # attivo il thd
            gui_support.Messaggio.set("Aspetta ...")
            self.codaEXE.put(("bteco", self.evnFine))
        else:
            # Fine
            self.Button44['state'] = gui.tk.DISABLED
            
            # segnalo al thd (che deve controllare sempre che l'evento sia set)
            self.evnFine.clear()
            
            # quando il thd finisce mi manda un messaggio


if __name__ == '__main__':
    ROOT = gui.tk.Tk()

    # inizializzo ...
    gui_support.set_Tk_var()
    # ... e imposto le variabili di supporto
    gui_support.Messaggio.set("Eccomi")

    # creo
    FINESTRA = MAIN(ROOT)

    # dopo che la finestra e' creata imposto ...
    ROOT.title('titolo')
    ROOT.resizable(False, False)
    gui_support.init(ROOT, FINESTRA)

    # eseguo
    ROOT.mainloop()

    # quando arrivo qua hanno terminato il programma
    FINESTRA.chiudi()
