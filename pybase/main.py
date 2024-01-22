#!/usr/bin/env python

"""
    Script principale
"""

import threading
import queue as coda
import tkinter as tk

import gui
import gui_support

import esegui
import utili
import eco
import dispositivo

TAB_CHIUSA = {1: False, 2: False}
TAB_APERTA = {1: True, 2: True}

VID_DISPO = 0x0403
PID_DISPO = 0x6001


class MAIN(gui.GUI):

    # da un certo punto in poi page butta tutto in gui_support, a me non piace,
    # preferisco ereditare ma, quando si aggiunge un bottone, bisogna lasciare il comando
    # vuoto e metterlo qua
    def _callback(self):
        # # tasto che cambia operazione (prende un argomento)
        self.Button1.bind("<ButtonRelease-1>", self._apri_seriale)
        # # tasto normale
        self.Button2.configure(command=self._trova_seriali)
        # # tasto che inizia/termina operazione (cfr self.evnFine)
        # self.Button44.configure(command=self.bteco)
        self.Button3.configure(command=self._eco)
        self.Button4.configure(command=self._eco_prova)
        self.Button5.configure(command=self._canc_dia)

    def __init__(self, master=None):
        self.master = master
        gui.GUI.__init__(self, master)

        #     logging.basicConfig(
        #         filename='desolfa.txt',
        #         level=logging.DEBUG,
        #         format='%(asctime)s - %(levelname)s - %(message)s')
        #     logging.getLogger().addHandler(logging.StreamHandler())
        self.logger = utili.LOGGA()

        self._callback()

        self._imposta_tab(TAB_CHIUSA)

        self.dispo = None

        # tasti che iniziano e terminano operazioni
        self.evnFine = threading.Event()

        # seriali
        self._trova_seriali()

        # Code per la comunicazione fra grafica e ciccia
        self.codaEXE = coda.Queue()
        self.codaGUI = coda.Queue()

        self.task = esegui.Esecutore(self.codaEXE, self.codaGUI)

        self.eco = eco.ECO(self.Button4,
                           gui_support.numEco,
                           gui_support.dimEco,
                           gui_support.Messaggio,
                           self.TProgressbar1,
                           self._un_eco)
        self.eco.cambia_limite(dispositivo.DISPO.DIM_DATI_CMD)

        # Comandi dall'esecutore
        self.cmd = {
            # 'fbteco': self._fine_bteco,
            "d_scrivi": self._diario_dispo
        }
        self._esegui_GUI()

    def _diario_dispo(self, riga):
        self.Scrolledlistbox2.insert(tk.END, riga)
        self.Scrolledlistbox2.see(tk.END)

    # def _fine_bteco(self):
    #     # Il thd ha finito
    #     gui_support.Messaggio.set("qualcosa")
    #
    #     # Il mio bottone e' riutilizzabile ...
    #     self.Button44['text'] = 'Eco'
    #     self.Button44['state'] = gui.tk.NORMAL
    #
    #     # ... e anche quelli incompatibili
    #     self.Button15['state'] = gui.tk.NORMAL
    #
    #     # ... pronto!
    #     self.evnFine.clear()

    def __del__(self):
        pass

    def _un_eco(self, dati=None):
        return self.dispo.eco(dati)

    def chiudi(self):
        self.codaEXE.put(("esci",))
        self.task.join()

        if self.dispo is not None:
            self.dispo.chiudi()
            self.dispo = None

    def _imposta_tab(self, lista):
        for tab in lista:
            stato = "disabled"
            if lista[tab]:
                stato = "normal"

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

    # --------- SERIALE ------------------------------------

    def _trova_seriali(self):
        self.Scrolledlistbox1.delete(0, tk.END)

        ls = utili.lista_seriali()
        for k, v in ls.items():
            if len(v) != 4:
                continue

            if v[2] != VID_DISPO:
                continue

            if v[3] != PID_DISPO:
                continue
            self.Scrolledlistbox1.insert(tk.END, k + " - " + v[0] + " - " + v[1])

    def _chiudi_seriale(self):
        self.dispo.chiudi()
        self.dispo = None
        self.codaEXE.put(("Dispositivo", self.dispo))

        self.Button1["text"] = "Usa questa"
        self._imposta_tab(TAB_CHIUSA)

    def _apri_seriale(self,_):
        if self.dispo is None:
            cs = self.Scrolledlistbox1.curselection()
            if len(cs) == 0:
                gui_support.Messaggio.set("? quale ?")
            else:
                sdati = self.Scrolledlistbox1.get(cs[0])
                dati = sdati.split("-")
                dev = dati[0].strip()
                self.dispo = dispositivo.DISPO(dev=dev)
                if not self.dispo.a_posto():
                    del self.dispo
                    self.dispo = None
                else:
                    self.codaEXE.put(("Dispositivo", self.dispo))

                    self.Button1["text"] = "Mollala"
                    self._imposta_tab(TAB_APERTA)
        else:
            self._chiudi_seriale()

    # --------- VARIE ---------------------------------------------

    def _eco(self):
        gui_support.Messaggio.set("Aspetta ...")
        self.codaEXE.put(("eco",))

    def _eco_prova(self):
        self.eco.Bottone()

    # --------- DIARIO --------------------------------------------

    def _canc_dia(self):
        self.Scrolledlistbox2.delete(0, tk.END)


if __name__ == "__main__":
    ROOT = gui.tk.Tk()

    # inizializzo ...
    gui_support.set_Tk_var()
    # ... e imposto le variabili di supporto
    gui_support.Messaggio.set("Eccomi")

    # creo
    FINESTRA = MAIN(ROOT)

    # dopo che la finestra e' creata imposto ...
    ROOT.title("Desolfatore")
    ROOT.resizable(False, False)
    gui_support.init(ROOT, FINESTRA)

    # eseguo
    ROOT.mainloop()

    # quando arrivo qua hanno terminato il programma
    FINESTRA.chiudi()
