#include <string.h>
#include "circo.h"

#define RIEMPITIVO_DI_DBG       0xCC

#define MIN(a, b)       ( (a) < (b) ? (a) : (b) )

static uint16_t incr(uint16_t x, uint16_t y, uint16_t l)
{
    x += y ;

    return x % l ;
}

static uint8_t * trova_buf(S_CIRCO * pC)
{
    union {
        void * v ;
        uint8_t * p ;
    } u ;

    u.v = pC ;
    u.p += sizeof(S_CIRCO) ;

    return u.p ;
}

static void * inc_void(void * v, uint16_t dim)
{
    union {
        void * v ;
        uint8_t * p ;
    } u ;

    u.v = v ;
    u.p += dim ;

    return u.v ;
}

bool CIRCO_ins(S_CIRCO * pC, const void * dati, uint16_t dim)
{
    bool esito = true ;

    do {
#ifdef DEBUG
        if (NULL == pC) {
            break ;
        }

        if (NULL == dati) {
            break ;
        }

        if (0 == dim) {
            break ;
        }
#endif
        if (0 == pC->tot) {
            pC->leggi = 0 ;
        }

        uint8_t * buf = trova_buf(pC) ;
        const uint16_t DIM_CIRCO = pC->DIM_CIRCO ;
        if (dim > DIM_CIRCO) {
            // Non ci staranno mai: copio gli ultimi
            esito = false ;

            pC->tot = DIM_CIRCO ;
            pC->leggi = 0 ;
            dati += dim - DIM_CIRCO ;
            memcpy(buf, dati, DIM_CIRCO) ;

            // Fatto
            break ;
        }

        const uint16_t LIBERI = DIM_CIRCO - pC->tot ;
        if (dim > LIBERI) {
            // I primi li perdo
            esito = false ;

            pC->leggi = incr(pC->leggi, dim - LIBERI, DIM_CIRCO) ;

            // Adesso ho spazio: procedo
        }

        // Primo posto dove inserire i nuovi
        uint16_t scrivi = incr(pC->leggi, pC->tot, DIM_CIRCO) ;

        if (pC->leggi >= scrivi) {
            //     s      l
            // ****.......****
            memcpy(buf + scrivi, dati, dim) ;
            pC->tot += dim ;
        }
        else {
            //     l      s
            // ....*******....
            const uint16_t CODA = MIN(dim, DIM_CIRCO - scrivi) ;
            memcpy(buf + scrivi, dati, CODA) ;
            pC->tot += CODA ;

            dim -= CODA ;
            if (dim) {
                memcpy(buf, dati + CODA, dim) ;
                pC->tot += dim ;
            }
        }
    } while (false) ;

    return esito ;
}

uint16_t CIRCO_est(S_CIRCO * pC, void * dati, uint16_t dim)
{
    uint16_t letti = 0 ;

    do {
#ifdef DEBUG
        if (NULL == pC) {
            break ;
        }

        if (NULL == dati) {
            break ;
        }

        if (0 == dim) {
            break ;
        }
#endif
        if (0 == pC->tot) {
            break ;
        }

        if (dim > pC->tot) {
            dim = pC->tot ;
        }

        uint8_t * buf = trova_buf(pC) ;

        //@ loop unroll dim;
        while (dim) {
            // In un colpo posso leggere o fino alla fine:
            //                l   U
            //     ****.......****
            // o fino al totale:
            //         l      U
            //     ....*******....
            const uint16_t ULTIMO = MIN(pC->DIM_CIRCO, pC->leggi + pC->tot) ;
            const uint16_t DIM = MIN(dim, ULTIMO - pC->leggi) ;

            memcpy(dati, buf + pC->leggi, DIM) ;
#ifndef NDEBUG
            memset(buf + pC->leggi, RIEMPITIVO_DI_DBG, DIM) ;
#endif
            dati = inc_void(dati, DIM) ;
            letti += DIM ;
            pC->tot -= DIM ;

            pC->leggi = incr(pC->leggi, DIM, pC->DIM_CIRCO) ;
            dim -= DIM ;
        }
    } while (false) ;

    return letti ;
}

uint16_t CIRCO_est2(S_CIRCO * pC, uint8_t finoa, void * dati, uint16_t dim)
{
    uint16_t letti = 0 ;

    do {
#ifdef DEBUG
        if (NULL == pC) {
            break ;
        }

        if (NULL == dati) {
            break ;
        }

        if (0 == dim) {
            break ;
        }
#endif
        if (0 == pC->tot) {
            break ;
        }

        if (dim > pC->tot) {
            dim = pC->tot ;
        }

        uint8_t * buf = trova_buf(pC) ;

        // L'elemento finale ? si puo' trovare:
        // 1) a destra
        //                l ?  U
        //     ****.......*****		leggo da l a ?
        // 2) a sinistra
        //      ?  S      l    U
        //     ****.......*****     leggo a destra + da 0 a ?
        // 3) in mezzo
        //         l  ?   U
        //     ....*******.....     leggo da l a ?
        // 4) da nessuna parte
        const uint16_t ULTIMO = MIN(pC->DIM_CIRCO, pC->leggi + pC->tot) ;
        const uint16_t DIM = MIN(dim, ULTIMO - pC->leggi) ;
        uint8_t * l = buf + pC->leggi ;
        uint8_t * fa = memchr(l, finoa, DIM) ;
        if (fa) {
            // caso (1) o (3)
            letti = fa - l + 1 ;

            memcpy(dati, l, letti) ;
#ifndef NDEBUG
            memset(l, RIEMPITIVO_DI_DBG, letti) ;
#endif
            pC->tot -= letti ;
            pC->leggi = incr(pC->leggi, letti, pC->DIM_CIRCO) ;
        }
        else if (ULTIMO < pC->DIM_CIRCO) {
            // caso (4)
        }
        else {
            const uint16_t SINISTRA = pC->leggi + pC->tot - pC->DIM_CIRCO ;
            fa = memchr(buf, finoa, SINISTRA) ;
            if (fa) {
                // caso (2)
                // tutta la destra
                memcpy(dati, l, DIM) ;
#ifndef NDEBUG
                memset(l, RIEMPITIVO_DI_DBG, DIM) ;
#endif
                dati += DIM ;
                letti += DIM ;

                // fino a ?
                ptrdiff_t diff = ( (uint8_t *) fa ) - buf ;

                letti += diff ;
                memcpy(dati, buf, diff) ;
#ifndef NDEBUG
                memset(buf, RIEMPITIVO_DI_DBG, diff + 1) ;
#endif
                pC->tot -= letti + 1 ;
                pC->leggi = incr(pC->leggi, letti + 1, pC->DIM_CIRCO) ;
            }
            else {
                // caso (4)
            }
        }
    } while (false) ;

    return letti ;
}
