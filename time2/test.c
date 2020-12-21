#include "time2.h"

#include <stdio.h>
#include <stdint.h>

#include "__fc_builtin.h"

static void stampa_bt(const char * t, time_t e, struct tm * bt)
{
    const char * giorno = NULL ;

    switch (bt->tm_wday) {
    case 0:
        giorno = "dom" ;
        break ;
    case 1:
        giorno = "lun" ;
        break ;
    case 2:
        giorno = "mar" ;
        break ;
    case 3:
        giorno = "mer" ;
        break ;
    case 4:
        giorno = "gio" ;
        break ;
    case 5:
        giorno = "ven" ;
        break ;
    case 6:
        giorno = "sab" ;
        break ;
    default:
        giorno = "???" ;
        break ;
    }

    printf("%s: %d = %d/%02d/%02d (%03d - %s) %02d:%02d:%02d\r\n",
           t, e,
           bt->tm_year + 1900, bt->tm_mon + 1, bt->tm_mday,
           bt->tm_yday + 1, giorno,
           bt->tm_hour, bt->tm_min, bt->tm_sec) ;
}

int main(void)
{
    //@ loop unroll 10;
    for (size_t i = 0 ; i < 10 ; ++i) {
        time_t epoca = Frama_C_interval(0, 2145916799) ;

        // Deve essere coerente
        struct tm * tmp = gmtime2(&epoca) ;

        if (NULL == tmp) {
            printf("ERR %d \r\n", epoca) ;
            continue ;
        }

        time_t e = mktime2(tmp) ;
        if (e != epoca) {
            printf("ERR %d e != epoca %d\r\n", e, epoca) ;
            break ;
        }
        else {
            stampa_bt("OK", epoca, tmp) ;
        }
    }
}

