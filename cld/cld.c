#include <stdlib.h>
#include <string.h>
#include "cld.h"
#define DBGP_FILE
#include "cfg/includimi.h"

// In flash un settore ha anche un prologo e un epilogo

#define LOG_LIBERO    0xFFFF
#define LOG_USATO     0x0000

static const uint16_t USATO = LOG_USATO ;

struct fisico {
    // LOG_LIBERO -> 1/CLD_NUM_LOG -> LOG_USATO
    // Deve rappresentare (CLD_NUM_LOG + 2) valori
    uint16_t logico ;

    uint16_t dati[CLD_DIM_LOG / sizeof(uint16_t)] ;

    uint16_t cs ;
} ;

#define DIM_CHECK        ( 1 + ( CLD_DIM_LOG / sizeof(uint16_t) ) )

#define DIM_HW      ( sizeof(struct fisico) / sizeof(uint16_t) )

#define NUM_FIS         ( CLD_DIM_BLK / sizeof(struct fisico) )

// Associa logico a fisico

struct logico {
    uint32_t ofs ;
    const void * dati ;
} ;

static struct logico vLog[CLD_NUM_LOG] ;

// Operazioni
static const CLD_OP * pOp = NULL ;

static struct {
    // Prossimo settore fisico
    uint32_t psf ;

    // Quanti ne restano
    size_t liberi ;
} blocco ;

static bool elimina(uint16_t vlog)
{
    bool esito = false ;

    if (NULL == vLog[vlog].dati) {
        // Ottimo
        esito = true ;
    }
    else {
        vLog[vlog].dati = NULL ;

        esito = pOp->pfWrite(&USATO, 1, vLog[vlog].ofs) ;
    }

    return esito ;
}

static const uint16_t * indir(uint32_t offset)
{
    return pOp->pfRead(offset) ;
}

static void esamina(void)
{
    bool continua = true ;
    const struct fisico * pF = pOp->pfRead(blocco.psf) ;

    for ( uint16_t i = 0 ; i < NUM_FIS && continua ; i++, pF++) {
        switch (pF->logico) {
        case LOG_LIBERO: {
                // Verifico che sia davvero tutto a FF
                const size_t DIM_H = sizeof(struct fisico) / sizeof(uint16_t) ;
                const uint16_t * pH = (const uint16_t *) pF ;
                size_t j = 0 ;
                for ( ; j < DIM_H ; j++) {
                    if (pH[j] != 0xFFFF) {
                        break ;
                    }
                }

                if (DIM_H == j) {
                    // Libero
                    continua = false ;
                }
                else {
                    blocco.psf += sizeof(struct fisico) ;
                    blocco.liberi -= 1 ;
                }
            }
            break ;
        case LOG_USATO:
            blocco.psf += sizeof(struct fisico) ;
            blocco.liberi -= 1 ;
            break ;
        default:
            if (pF->logico <= CLD_NUM_LOG) {
                uint16_t cs = pOp->pfCheck(indir(blocco.psf), DIM_CHECK) ;
                if (cs == pF->cs) {
                    // Eccolo!
                    vLog[pF->logico - 1].ofs = blocco.psf ;
                    vLog[pF->logico - 1].dati = pF->dati ;
                }
            }
            else {
                // ???
            	DBG_ERR;
            }
            blocco.psf += sizeof(struct fisico) ;
            blocco.liberi -= 1 ;
            break ;
        }

        // Prossimo
    }
}

static bool scrivi_settore(
    uint16_t vlog,
    uint32_t ofs,
    const void * dati)
{
    bool esito = false ;

    // Prima metto a posto la copia temporanea
    struct fisico tmp = {
        .logico = vlog + 1
    } ;

    memcpy(tmp.dati, dati, CLD_DIM_LOG) ;
    tmp.cs = pOp->pfCheck( (const uint16_t *) &tmp, DIM_CHECK ) ;

    do {
        // Poi la copio in flash
        CHECK(esito = pOp->pfWrite( (const uint16_t *) &tmp, DIM_HW, ofs )) ;

        // Elimino il precedente
        CHECK(elimina(vlog)) ;

        // Sostituisco
        vLog[vlog].ofs = ofs ;
        const struct fisico * pF = pOp->pfRead(ofs) ;
        vLog[vlog].dati = pF->dati ;
    } while (false) ;

    return esito ;
}

static bool stessi_dati(
    uint16_t vlog,
    const void * dati)
{
    bool esito = false ;

    if (NULL == vLog[vlog].dati) {
        // Assente
    }
    else {
        // Accedo direttamente in flash
        esito = 0 == memcmp(dati, vLog[vlog].dati, CLD_DIM_LOG) ;
    }

    return esito ;
}

bool CLD_ini(const CLD_OP * p)
{
    bool esito = false ;

    do {
        ASSERT(NULL == pOp) ;
        if (NULL != pOp) {
            // Gia' inizializzata
            esito = true ;
            break ;
        }

        if (NULL == p) {
            break ;
        }

        blocco.psf = 0 ;
        blocco.liberi = NUM_FIS ;

        // Nessun settore logico
        memset( vLog, 0, sizeof(vLog) ) ;

        pOp = p ;

        esamina() ;

        esito = true ;
    } while (false) ;

    return esito ;
}

void CLD_fin(void)
{
    pOp = NULL ;
}

const void * CLD_read(uint16_t logi)
{
    const void * dati = NULL ;

    do {
        ASSERT(NULL != pOp) ;
        if (NULL == pOp) {
            break ;
        }

        logi -= 1 ;

        ASSERT(logi < CLD_NUM_LOG) ;
        if (logi >= CLD_NUM_LOG) {
            break ;
        }

        dati = vLog[logi].dati ;
    } while (false) ;

    return dati ;
}

bool CLD_write(
    uint16_t logi,
    const void * dati)
{
    bool esito = false ;

    do {
        ASSERT(NULL != pOp) ;
        if (NULL == pOp) {
            break ;
        }

        logi -= 1 ;
        ASSERT(logi < CLD_NUM_LOG) ;
        if (logi >= CLD_NUM_LOG) {
            break ;
        }

        if (NULL == dati) {
            CHECK(esito = elimina(logi)) ;
            break ;
        }

        if ( stessi_dati(logi, dati) ) {
            esito = true ;
            break ;
        }

        if (0 == blocco.liberi) {
            break ;
        }

        uint32_t dove = blocco.psf ;
        blocco.liberi -= 1 ;
        blocco.psf += sizeof(struct fisico) ;

        CHECK(esito = scrivi_settore(logi, dove, dati)) ;
    } while (false) ;

    return esito ;
}

bool CLD_full(void)
{
    ASSERT(NULL != pOp) ;
    return 0 == blocco.liberi ;
}
