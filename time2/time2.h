#ifndef TIME2_H_
#define TIME2_H_

#include <time.h>

/*
	Le due funzioni che seguono estendono la validita' dell'epoca
	oltre il 2038 traslando di 28 anni l'intervallo:
		1998/1/1 00:00:00 <= tm <= 2065/12/31 23:59:59

	========== tl;dr; ==========

	Usualmente epoca = 0 <==> 1970/1/1 00:00:00
	A 32 bit:
                        0 <= epoca <= 2147483647
        1970/1/1 00:00:00 <=   tm  <= 2038/1/19 03:14:07

    In anni "interi":
                        0 <= epoca <= 2145916799
        1970/1/1 00:00:00 <=   tm  <= 2037/12/31 23:59:59

    Se si escludono gli anni secolari non bisestili, il ciclo
    con cui si ripetono gli anni e' di 4 * 7 = 28, cioe' ogni
    28 anni l'anno si ripresenta uguale, p.e.
    	Monday, 21 December 2020 == Monday, 21 December 2048

    Dal 2026 si potranno aggiungere 2 cicli:
                        0 <= epoca <= 2145916799
        2026/1/1 00:00:00 <=   tm  <= 2093/12/31 23:59:59
    Poi questo metodo non vale piu' perche' il 2100 non e' bisestile

	cfr https://www.epochconverter.com/
*/

// Torna -1 se errore
time_t mktime2(struct tm *) ;

// Torna NULL se errore
struct tm * gmtime2(const time_t *) ;

#else
#   warning time2.h incluso
#endif
