#include <ctype.h>
#include "prm.h"
#include "cld.h"
#include "varie/crc.h"
#define DBGP_FILE
#include "cfg/includimi.h"

#pragma segment="PRM_CLD"
//static const size_t DIMENSIONE_PRM_CLD = __section_size("PRM_CLD") ;
static const void * INDIRIZZO_PRM_CLD = __section_begin("PRM_CLD") ;

// Allocazione dei settori logici
#define SL_COLL_NSP     1

static const void * leggi_flash(uint32_t addr)
{
    uint32_t mem = UINTEGER(INDIRIZZO_PRM_CLD) ;
    mem += addr ;

    return CPOINTER(mem) ;
}

static bool scrivi_flash(
    const uint16_t * dati,
    size_t numh,
    uint32_t offset)
{
    bool continua = true ;

    offset += UINTEGER(INDIRIZZO_PRM_CLD) ;

    (void) HAL_FLASH_Unlock() ;

    for (size_t i = 0 ; i < numh && continua ; ++i, offset += 2) {
        continua = HAL_OK == HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD,
                                               offset,
                                               dati[i]) ;
    }

    (void) HAL_FLASH_Lock() ;

    return continua ;
}

static const CLD_OP fop = {
    .pfRead = leggi_flash,
    .pfWrite = scrivi_flash,
    .pfCheck = CRC_prm_cld,
} ;

static bool cancella(uint32_t block)
{
    FLASH_EraseInitTypeDef EraseInitStruct = {
        .TypeErase = FLASH_TYPEERASE_PAGES,
        .PageAddress = UINTEGER(INDIRIZZO_PRM_CLD),
        .NbPages = 1
    } ;

    INUTILE(block) ;

    (void) HAL_FLASH_Unlock() ;

    uint32_t PageError ;
    bool esito = HAL_OK == HAL_FLASHEx_Erase(&EraseInitStruct, &PageError) ;

    (void) HAL_FLASH_Lock() ;

    return esito ;
}

void PRM_iniz(void)
{
    CHECK( CLD_ini(&fop) ) ;
}

bool PRM_cld_erase(void)
{
    CLD_fin() ;
    bool esito = cancella(CLD_BLOCK)  ;
    return esito && CLD_ini(&fop)  ; ;
}

static size_t nsp_valido(
    char * dst,
    const char * srg)
{
    size_t i = 0 ;

    while (true) {
        char x = srg[i] ;
        if (0 == x) {
            break ;
        }
        if ( 0 == isalnum( (int) x ) ) {
            i = 0 ;
            break ;
        }
        if (i < CLD_DIM_LOG) {
            dst[i] = x ;
            i += 1 ;
        }
        else {
            i = 0 ;
            break ;
        }
    }
    return i ;
}

bool PRM_nsp_scrivi(const char * v)
{
    char nsp[CLD_DIM_LOG] = {
        0
    } ;

    const size_t DIM = nsp_valido(nsp, v) ;
    if (0 == DIM) {
        return false ;
    }

    return CLD_write(SL_COLL_NSP, nsp) ;
}

const char * PRM_nsp_leggi(void)
{
    return CLD_read(SL_COLL_NSP) ;
}
