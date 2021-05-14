#ifndef CLD_H_
#define CLD_H_

/*
 * Un solo blocco di flash: si usa quando i parametri sono scritti
 * una volta e poi vengono letti
 *
 * Il blocco viene diviso in settori fisici, che vengono scritti con
 * i settori logici (con i dati da salvare)
 *
 * I settori logici iniziano da 1
 *
 * I settori logici vengono scritti in sequenza, per cui una scrittura
 * successiva si trova in un settore fisico con un ordinale piu' alto
 *
 * Quando non ci sono piu' settori fisici la scrittura fallisce
 * E' compito altrui:
 *     1) salvare i dati in ram (CLD_read)
 *     2) cancellare il blocco
 *     3) ripartire (CLD_fin + CLD_ini)
 *     4) riscrivere i dati (CLD_write)
 */

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "cfg/cld_cfg.h"


// Get the address of the given offset in the block
typedef const void *(*CLD_READ)(uint32_t offset) ;

// Write a vector of half words (16 bit) at the given offset
typedef bool (*CLD_WRITE)(const uint16_t * hw, size_t numhw, uint32_t offset) ;

// Compute the check value
typedef uint16_t (*CLD_CHECK)(const uint16_t *, size_t numhw) ;

typedef struct {
    CLD_READ pfRead ;
    CLD_WRITE pfWrite ;

    CLD_CHECK pfCheck ;
} CLD_OP ;

// The first operation
bool CLD_ini(const CLD_OP *) ;

// The last operation
void CLD_fin(void) ;

// NULL if error or sector does not exist
const void * CLD_read(uint16_t) ;

// If NULL the sector will not exist anymore
bool CLD_write(uint16_t, const void *) ;

bool CLD_full(void);

#ifdef __cplusplus
}
#endif

#endif
