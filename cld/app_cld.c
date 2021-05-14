#include <stdlib.h>
#include <string.h>
#include "stm32f0xx_hal.h"
#include "cld.h"
#include "unity.h"
#define DBGP_FILE
#include "cfg/includimi.h"

#pragma segment="PRM_CLD"
//static const size_t DIMENSIONE_PRM_CLD = __section_size("PRM_CLD") ;
static const void * INDIRIZZO_PRM_CLD = __section_begin("PRM_CLD") ;

static uint32_t dove ;

static const void * leggi_flash(uint32_t addr)
{
    uint32_t mem = UINTEGER(INDIRIZZO_PRM_CLD) ;
    mem += addr ;

    return CPOINTER(mem) ;
}

static uint16_t checksum(
    const uint16_t * v,
    size_t dim)
{
    uint16_t cs = v[0] ;

    for (size_t i = 1 ; i < dim ; i++) {
        cs += v[i] ;
    }

    return NOT(cs) ;
}

static bool scrivi_flash(
    const uint16_t * dati,
    size_t numh,
    uint32_t offset)
{
    bool continua = true ;

    offset += UINTEGER(INDIRIZZO_PRM_CLD) ;

    dove = offset ;

    (void) HAL_FLASH_Unlock() ;

    for (size_t i = 0 ; i < numh && continua ; ++i, offset += 2) {
        continua = HAL_OK == HAL_FLASH_Program(FLASH_TYPEPROGRAM_HALFWORD,
                                               offset,
                                               dati[i]) ;
    }

    (void) HAL_FLASH_Lock() ;

    return continua ;
}

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

static const CLD_OP fop = {
    .pfRead = leggi_flash,
    .pfWrite = scrivi_flash,
    .pfCheck = checksum,
} ;

static uint8_t dati1[CLD_DIM_LOG] ;
static uint8_t dati2[CLD_DIM_LOG] ;

static void crea_dati(uint8_t * dati)
{
    static unsigned int seme = 436676279 ;

    srand(seme) ;

    for (int i = 0 ; i < CLD_DIM_LOG ; i++) {
        dati[i] = rand() & 0xFF ;
    }

    seme++ ;
}

static void aggiorna_dati(uint8_t * dati)
{
    for (int i = 0 ; i < CLD_DIM_LOG ; i++) {
        dati[i]++ ;
    }
}

static bool diversi(
    const uint8_t * sx,
    const uint8_t * dx)
{
    bool esito = false ;

    for (size_t i = 0 ; i < CLD_DIM_LOG && !esito ; i++) {
        esito = sx[i] != dx[i] ;
    }

    return esito ;
}

void setUp(void)
{}

void tearDown(void)
{
    CLD_fin() ;
}

void test1(void)
{
    CLD_fin() ;

    // Prima di tutto inizializzare
    TEST_ASSERT_NULL( CLD_read(CLD_NUM_LOG) ) ;
    TEST_ASSERT( !CLD_write(CLD_NUM_LOG, dati1) ) ;
    TEST_ASSERT_NULL( CLD_read(CLD_NUM_LOG) ) ;
}

void test2(void)
{
    // Se la flash e' vuota
    TEST_ASSERT( cancella(CLD_BLOCK) ) ;

    TEST_ASSERT( CLD_ini(&fop) ) ;

    // C'e' spazio
    TEST_ASSERT_FALSE(CLD_full());

    // Non trovo elementi
    for (uint16_t virt = 1 ; virt <= CLD_NUM_LOG ; virt++) {
        TEST_ASSERT_NULL( CLD_read(virt) ) ;
    }
}

void test3(void)
{
    crea_dati(dati1) ;
    TEST_ASSERT( cancella(CLD_BLOCK) ) ;

    TEST_ASSERT( CLD_ini(&fop) ) ;

    // Se scrivo qualcosa
    TEST_ASSERT( CLD_write(CLD_NUM_LOG, dati1) ) ;

    // E chiudo
    CLD_fin() ;

    // Quando riapro
    TEST_ASSERT( CLD_ini(&fop) ) ;

    // La ritrovo
    const void * x = CLD_read(CLD_NUM_LOG) ;
    TEST_ASSERT_NOT_NULL(x) ;
    TEST_ASSERT( !diversi(dati1, x) ) ;

    // Ma se la elimino
    TEST_ASSERT( CLD_write(CLD_NUM_LOG, NULL) ) ;

    // E chiudo
    CLD_fin() ;

    // Quando riapro
    TEST_ASSERT( CLD_ini(&fop) ) ;

    // Non c'e' piu'
    TEST_ASSERT_NULL( CLD_read(CLD_NUM_LOG) ) ;
}

void test4(void)
{
    bool continua = true ;

    crea_dati(dati1) ;
    crea_dati(dati2) ;
    TEST_ASSERT( cancella(CLD_BLOCK) ) ;

    TEST_ASSERT( CLD_ini(&fop) ) ;

    for (uint16_t virt1 = 1 ; virt1 <= CLD_NUM_LOG && continua ; virt1++) {
        // Se scrivo una cosa da una parte
        TEST_ASSERT( CLD_write(virt1, dati1) ) ;

        // E una cosa diversa negli altri settori
        for (uint16_t virt2 = 1 ; virt2 <= CLD_NUM_LOG && continua ; virt2++) {
            if (virt2 == virt1) {
                continue ;
            }
            continua = CLD_write(virt2, dati2)  ;
        }

        // La ritrovo
        const void * x = CLD_read(virt1) ;
        TEST_ASSERT_NOT_NULL(x) ;
        TEST_ASSERT( !diversi(dati1, x) ) ;

        aggiorna_dati(dati1) ;
        aggiorna_dati(dati2) ;
    }
}

void test5(void)
{
    TEST_ASSERT( cancella(CLD_BLOCK) ) ;

    crea_dati(dati1) ;
    TEST_ASSERT( CLD_ini(&fop) ) ;

    // Riempio con un solo settore
    while (true) {
        if ( !CLD_write(CLD_NUM_LOG, dati1) ) {
            break ;
        }
        memcpy(dati2, dati1, CLD_DIM_LOG) ;
        aggiorna_dati(dati1) ;
    }

    TEST_ASSERT(CLD_full());

    // Vale l'ultimo
    const void * x = CLD_read(CLD_NUM_LOG) ;
    TEST_ASSERT_NOT_NULL(x) ;
    TEST_ASSERT( !diversi(dati2, x) ) ;

    CLD_fin() ;

    // Anche se ricomincio
    TEST_ASSERT( CLD_ini(&fop) ) ;

    x = CLD_read(CLD_NUM_LOG) ;
    TEST_ASSERT_NOT_NULL(x) ;
    TEST_ASSERT( !diversi(dati2, x) ) ;
}

void test6(void)
{
    crea_dati(dati1) ;
    TEST_ASSERT( cancella(CLD_BLOCK) ) ;

    TEST_ASSERT( CLD_ini(&fop) ) ;

    // Se scrivo una cosa ...
    TEST_ASSERT( CLD_write(CLD_NUM_LOG, dati1) ) ;

    const void * x = CLD_read(CLD_NUM_LOG) ;
    TEST_ASSERT_NOT_NULL(x) ;
    TEST_ASSERT( !diversi(dati1, x) ) ;

    // ... quando la riscrivo
    dove = NOT(0) ;
    TEST_ASSERT( CLD_write(CLD_NUM_LOG, dati1) ) ;

    x = CLD_read(CLD_NUM_LOG) ;
    TEST_ASSERT_NOT_NULL(x) ;
    TEST_ASSERT( !diversi(dati1, x) ) ;

    // ... me ne accorgo
    TEST_ASSERT(NOT(0) == dove) ;
}

void app(void)
{
    UNITY_BEGIN() ;

    RUN_TEST(test1) ;
    RUN_TEST(test2) ;
    RUN_TEST(test3) ;
    RUN_TEST(test4) ;
    RUN_TEST(test5) ;
    RUN_TEST(test6) ;

    UNITY_END() ;

    while (true) {
        BPOINT ;
    }
}
