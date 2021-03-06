#include <stdint.h>
#include <stdbool.h>

#include "time2.h"

/*
 * Ogni 28 anni i giorni si ripetono nella stessa sequenza
 * (esclusi i secolari non bisestili)
 */

#define PERIODO_ANNI        28
#define PERIODI         (PERIODO_ANNI)

#define MIN_TM2_YEAR     TM_YEAR(1998)
#define MAX_TM2_YEAR     TM_YEAR(2065)

#define MIN_TM_YEAR     (MIN_TM2_YEAR - PERIODI)
#define MAX_TM_YEAR     (MAX_TM2_YEAR - PERIODI)

#define MIN_EPOCA2      ( (time_t)          0 )
#define MAX_EPOCA2      ( (time_t) 2145916799 )

time_t mktime2(struct tm * pBT)
{
    time_t epoca = -1 ;

    do {
        if (NULL == pBT) {
            break ;
        }

        if (pBT->tm_year < MIN_TM2_YEAR) {
            break ;
        }

        if (pBT->tm_year > MAX_TM2_YEAR) {
            break ;
        }

        // Tolgo i cicli
        pBT->tm_year -= PERIODI ;

        // Converto
        time_t risul = mktime(pBT) ;
        if (-1 == risul) {
            break ;
        }

        // Renormalizes local calendar time expressed as a struct tm object and
        // also converts it to time since epoch as a time_t object.
        // Ripeto i controlli
        if ( (MIN_TM_YEAR <= pBT->tm_year) && (pBT->tm_year <= MAX_TM_YEAR) ) {
            // A posto
            epoca = risul ;

            // Ripristino
            pBT->tm_year += PERIODI ;
        }
        else {
        }
    } while (false) ;

    return epoca ;
}

struct tm * localtime2(const time_t * pE2)
{
    struct tm * bd = NULL ;

    do {
        if (NULL == pE2) {
            break ;
        }

        time_t epoca2 = *pE2 ;

        if (epoca2 < MIN_EPOCA2) {
            break ;
        }

        if (epoca2 > MAX_EPOCA2) {
            break ;
        }

        // Converto
        bd = localtime(&epoca2) ;
        if (NULL == bd) {
            break ;
        }

        if ( (MIN_TM_YEAR <= bd->tm_year) &&
             (bd->tm_year <= MAX_TM_YEAR) ) {
            // Aggiorno
            bd->tm_year += PERIODI ;
        }
    } while (false) ;

    return bd ;
}
