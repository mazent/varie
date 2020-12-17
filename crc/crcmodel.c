/*                                                                            */
/* Author : Ross Williams (ross@guest.adelaide.edu.au.).                      */
/* Date   : 3 June 1993.                                                      */
/* Status : Public domain.                                                    */
/*                                                                            */
/* Description : This is the implementation (.c) file for the reference       */
/* implementation of the Rocksoft^tm Model CRC Algorithm. For more            */
/* information on the Rocksoft^tm Model CRC Algorithm, see the document       */
/* titled "A Painless Guide to CRC Error Detection Algorithms" by Ross        */
/* Williams (ross@guest.adelaide.edu.au.). This document is likely to be in   */
/* "ftp.adelaide.edu.au/pub/rocksoft".                                        */
/*                                                                            */
/* Note: Rocksoft is a trademark of Rocksoft Pty Ltd, Adelaide, Australia.    */
/*                                                                            */
/******************************************************************************/
/*                                                                            */
/* Implementation Notes                                                       */
/* --------------------                                                       */
/* To avoid inconsistencies, the specification of each function is not echoed */
/* here. See the header file for a description of these functions.            */
/* This package is light on checking because I want to keep it short and      */
/* simple and portable (i.e. it would be too messy to distribute my entire    */
/* C culture (e.g. assertions package) with this package.                     */
/*                                                                            */
/******************************************************************************/

#include "crcmodel.h"

/******************************************************************************/

/* The following definitions make the code more readable. */

#define BITMASK(X) ( 1L << (X) )
#define MASK32 0xFFFFFFFFL

/******************************************************************************/

static ulong reflect P_( (ulong v, int b) ) ;
static ulong reflect(v, b)
/* Returns the value v with the bottom b [0,32] bits reflected. */
/* Example: reflect(0x3e23L,3) == 0x3e26                        */
ulong v ;
int b ;
{
    int i ;
    ulong t = v ;
    for (i = 0 ; i < b ; i++) {
        if (t & 1L) {
            v |= BITMASK( (b - 1) - i ) ;
        }
        else {
            v &= ~BITMASK( (b - 1) - i ) ;
        }
        t >>= 1 ;
    }
    return v ;
}

/******************************************************************************/

static ulong widmask P_( (p_cm_t) ) ;
static ulong widmask(p_cm)
/* Returns a longword whose value is (2^p_cm->cm_width)-1.     */
/* The trick is to do this portably (e.g. without doing <<32). */
p_cm_t p_cm ;
{
    return ( ( ( 1L << (p_cm->cm_width - 1) ) - 1L ) << 1 ) | 1L ;
}

/******************************************************************************/

void cm_ini(p_cm)
p_cm_t p_cm ;
{
    p_cm->cm_reg = p_cm->cm_init ;
}

/******************************************************************************/

void cm_nxt(p_cm, ch)
p_cm_t p_cm ;
int ch ;
{
    int i ;
    ulong uch = (ulong) ch ;
    ulong topbit = BITMASK(p_cm->cm_width - 1) ;

    if (p_cm->cm_refin) {
        uch = reflect(uch, 8) ;
    }
    p_cm->cm_reg ^= ( uch << (p_cm->cm_width - 8) ) ;
    //@ loop unroll 8;
    for (i = 0 ; i < 8 ; i++) {
        if (p_cm->cm_reg & topbit) {
            p_cm->cm_reg = (p_cm->cm_reg << 1) ^ p_cm->cm_poly ;
        }
        else {
            p_cm->cm_reg <<= 1 ;
        }
        p_cm->cm_reg &= widmask(p_cm) ;
    }
}

/******************************************************************************/

void cm_blk(p_cm, blk_adr, blk_len)
p_cm_t p_cm ;
p_ubyte_ blk_adr ;
ulong blk_len ;
{
    //@ loop unroll blk_len;
    while (blk_len--) {
        cm_nxt(p_cm, *blk_adr++) ;
    }
}

/******************************************************************************/

ulong cm_crc(p_cm)
p_cm_t p_cm ;
{
    if (p_cm->cm_refot) {
        return p_cm->cm_xorot ^ reflect(p_cm->cm_reg, p_cm->cm_width) ;
    }
    else {
        return p_cm->cm_xorot ^ p_cm->cm_reg ;
    }
}

/******************************************************************************/

ulong cm_tab(p_cm, index)
p_cm_t p_cm ;
int index ;
{
    int i ;
    ulong r ;
    ulong topbit = BITMASK(p_cm->cm_width - 1) ;
    ulong inbyte = (ulong) index ;

    if (p_cm->cm_refin) {
        inbyte = reflect(inbyte, 8) ;
    }
    r = inbyte << (p_cm->cm_width - 8) ;
    //@ loop unroll 8;
    for (i = 0 ; i < 8 ; i++) {
        if (r & topbit) {
            r = (r << 1) ^ p_cm->cm_poly ;
        }
        else {
            r <<= 1 ;
        }
    }
    if (p_cm->cm_refin) {
        r = reflect(r, p_cm->cm_width) ;
    }
    return r & widmask(p_cm) ;
}

/******************************************************************************/

// Esempio: CRC ITT (tmd)

#define WIDTH       16
#define POLY        0x1021
#define INIT        0
#define XOROT       0

ulong crctable[256] ;

ulong crc_normal(unsigned char * blk_adr, ulong blk_len)
{
    ulong crc = INIT ;
    //@ loop unroll blk_len;
    while (blk_len--) {
        crc =
            crctable[( ( crc >>
                         (WIDTH - 8) ) ^ *blk_adr++ ) & 0xFFL] ^ (crc << 8) ;
    }
    return crc ^ XOROT ;
}

#include <stdio.h>
#include <stdint.h>

int main(void)
{
    uint8_t msg[] = {
        0, 1, 2, 3, 4
    } ;

    // Step 1 + 2
    cm_t prm = {
        .cm_width = WIDTH,
        .cm_poly = POLY,
        .cm_init = INIT,
        .cm_refin = FALSE,
        .cm_refot = FALSE,
        .cm_xorot = XOROT
    } ;

    // Calcolo la tabella
    //@ loop unroll 256;
    for (int index = 0 ; index < 256 ; ++index) {
        crctable[index] = cm_tab(&prm, index) ;
    }
    prm.cm_init = INIT ;

    // Step 3
    cm_ini(&prm) ;

    // Step 4
    cm_nxt(&prm, msg[0]) ;
    cm_blk(&prm, &msg[1], sizeof(msg) - 1) ;

    // Step 5
    ulong crc = cm_crc(&prm) ;

    // Uguale?
    ulong crct = crc_normal( msg, sizeof(msg) ) ;
#if WIDTH == 16
    crct &= 0xFFFF ;
#endif
    if (crc == crct) {
#if WIDTH == 16
        printf("uint16_t crctab[] = {\r\n") ;
#endif
        //@ loop unroll 16;
        for (int i = 0 ; i < 16 ; ++i) {
            int riga = i * 16 ;
#if WIDTH == 16
            printf(
                "\t0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, 0x%04X, \r\n",
#else
            printf(
                "\t0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, 0x%08X, \r\n",
#endif
                crctable[riga +  0], crctable[riga +  1],
                crctable[riga +  2], crctable[riga +  3],
                crctable[riga +  4], crctable[riga +  5],
                crctable[riga +  6], crctable[riga +  7],
                crctable[riga +  8], crctable[riga +  9],
                crctable[riga + 10], crctable[riga + 11],
                crctable[riga + 12], crctable[riga + 13],
                crctable[riga + 14], crctable[riga + 15]) ;
        }
        printf("} ;\r\n") ;
    }
    else {
        printf("crc 0x%08X != 0x%08x crct\r\n", crc, crct) ;
    }

    return 0 ;
}
