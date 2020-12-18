#include <stdio.h>
#include <string.h>
#include "circo.h"
#include "__fc_builtin.h"

#define MAX_BUFF        20

#define DBG_ERR     printf("ERR %d\r\n", __LINE__)

static union {
    S_CIRCO c ;
    uint8_t b[sizeof(S_CIRCO) - 1 + MAX_BUFF] ;
} u ;

int main(void)
{
    CIRCO_iniz(&u.c, MAX_BUFF) ;

    // Creo i dati
    uint8_t db[MAX_BUFF] ;
    //@ loop unroll MAX_BUFF;
    for (int i = 0 ; i < MAX_BUFF ; ++i) {
        db[i] = Frama_C_interval(0, 255) ;
    }

    // Inserimento
    if ( !CIRCO_ins(&u.c, db, MAX_BUFF) ) {
        DBG_ERR ;
    }
    if ( MAX_BUFF != CIRCO_dim(&u.c) ) {
        DBG_ERR ;
    }
    if ( 0 != CIRCO_liberi(&u.c) ) {
        DBG_ERR ;
    }

    // Estrazione
    //@ loop unroll MAX_BUFF;
    for (int i = 0 ; i < MAX_BUFF ; ++i) {
        uint8_t val = 0 ;
        if ( 1 != CIRCO_est(&u.c, &val, 1) ) {
            DBG_ERR ;
            break ;
        }
        if (val != db[i]) {
            DBG_ERR ;
            break ;
        }
    }

    CIRCO_svuota(&u.c) ;

    do {
        // Inserimento
        if ( !CIRCO_ins(&u.c, "ciao", 5) ) {
            DBG_ERR ;
            break ;
        }

        if ( !CIRCO_ins(&u.c, "ciccio*", 7) ) {
            DBG_ERR ;
            break ;
        }

        // Estrazione
        char tmp[MAX_BUFF] ;

        uint16_t dim = CIRCO_est2(&u.c, 0, tmp, MAX_BUFF) ;
        if (dim != 5) {
            DBG_ERR ;
            printf("\t%d != 5\r\n", dim) ;
            tmp[5] = 0 ;
            printf("\t<%s>\r\n", tmp) ;
            break ;
        }
        if ( 0 != strcmp("ciao", tmp) ) {
            DBG_ERR ;
            break ;
        }

        dim = CIRCO_est2(&u.c, '*', tmp, MAX_BUFF) ;
        if (dim != 7) {
            DBG_ERR ;
            printf("\t%d != 5\r\n", dim) ;
            tmp[7] = 0 ;
            printf("\t<%s>\r\n", tmp) ;
            break ;
        }
        tmp[dim - 1] = 0 ;
        if ( 0 != strcmp("ciccio", tmp) ) {
            DBG_ERR ;
            printf("\t<%s>\r\n", tmp) ;
            break ;
        }
    } while (false) ;

    return 0 ;
}
