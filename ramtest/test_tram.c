#define STAMPA_DBG
#include "utili.h"
#include "tram.h"
#include "unity.h"

/*
 * Verifica funzionale dei test della ram
 *
 * Approfitto dei 64 KiB della CCM
 */

#define CCM_ADDR	(uint32_t) 0x10000000
#define CCM_DIM		65536


static void bus_8(void)
{
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk1(CCM_ADDR, RDB_8_BIT), "Fallito DW1-8") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk0(CCM_ADDR, RDB_8_BIT), "Fallito DW0-8") ;

    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk1(CCM_ADDR, CCM_DIM, RDB_8_BIT), "Fallito AW1-8") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk0(CCM_ADDR, CCM_DIM, RDB_8_BIT), "Fallito AW0-8") ;

    TEST_ASSERT_TRUE_MESSAGE(TRAM_accedi(CCM_ADDR, CCM_DIM, RDB_8_BIT), "Fallito accesso (8)") ;
}

static void bus_16(void)
{
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk1(CCM_ADDR, RDB_16_BIT), "Fallito DW1-16") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk0(CCM_ADDR, RDB_16_BIT), "Fallito DW0-16") ;

    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk1(CCM_ADDR, CCM_DIM, RDB_16_BIT), "Fallito AW1-16") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk0(CCM_ADDR, CCM_DIM, RDB_16_BIT), "Fallito AW0-16") ;

    TEST_ASSERT_TRUE_MESSAGE(TRAM_accedi(CCM_ADDR, CCM_DIM, RDB_16_BIT), "Fallito accesso (16)") ;
}

static void bus_32(void)
{
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk1(CCM_ADDR, RDB_32_BIT), "Fallito DW1-32") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_DataWalk0(CCM_ADDR, RDB_32_BIT), "Fallito DW0-32") ;

    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk1(CCM_ADDR, CCM_DIM, RDB_32_BIT), "Fallito AW1-32") ;
    TEST_ASSERT_EQUAL_UINT32_MESSAGE(0, TRAM_AddrWalk0(CCM_ADDR, CCM_DIM, RDB_32_BIT), "Fallito AW0-32") ;

    TEST_ASSERT_TRUE_MESSAGE(TRAM_accedi(CCM_ADDR, CCM_DIM, RDB_32_BIT), "Fallito accesso (32)") ;
}

void test_tram(void)
{
    UnityBegin("tram") ;

    // Un test per ogni dimensione di bus dati
    RUN_TEST(bus_8) ;
    RUN_TEST(bus_16) ;
    RUN_TEST(bus_32) ;

    (void) UnityEnd() ;
}
