#include "time2.h"

/*
 	Sul psoc del ghost:

	sizeof(time_t) = 4

	localtime: 0 = 1970/01/01 (001 - gio) 00:00:00
	gmtime: 0 = 1970/01/01 (001 - gio) 00:00:00

	da tm a epoca
	=============
	OK: 0 = 1998/01/01 (001 - gio) 00:00:00
	OK: 2145916799 = 2065/12/31 (365 - gio) 23:59:59
	OK: 1269862765 = 2038/03/29 (088 - lun) 11:39:25
	OK: 300038758 = 2007/07/05 (186 - gio) 16:05:58
	OK: 1070621835 = 2031/12/05 (339 - ven) 10:57:15
	OK: 1961263796 = 2060/02/24 (055 - mar) 19:29:56
	OK: 1969489645 = 2060/05/30 (151 - dom) 00:27:25
	OK: 700262367 = 2020/03/10 (070 - mar) 21:19:27
	OK: 904881777 = 2026/09/04 (247 - ven) 04:02:57
	OK: 1853494165 = 2056/09/25 (269 - lun) 11:29:25
	OK: 258212872 = 2006/03/08 (067 - mer) 13:47:52
	OK: 1377244280 = 2041/08/23 (235 - ven) 07:51:20
	da epoca a tm
	=============
	OK: 0 = 1998/01/01 (001 - gio) 00:00:00
	OK: 2145916799 = 2065/12/31 (365 - gio) 23:59:59
	OK: 1269859165 = 2038/03/29 (088 - lun) 10:39:25
	OK: 300035158 = 2007/07/05 (186 - gio) 15:05:58
	OK: 1070618235 = 2031/12/05 (339 - ven) 09:57:15
	OK: 1961260196 = 2060/02/24 (055 - mar) 18:29:56
	OK: 1969486045 = 2060/05/29 (150 - sab) 23:27:25
	OK: 700258767 = 2020/03/10 (070 - mar) 20:19:27
	OK: 904878177 = 2026/09/04 (247 - ven) 03:02:57
	OK: 1853490565 = 2056/09/25 (269 - lun) 10:29:25
	OK: 258209272 = 2006/03/08 (067 - mer) 12:47:52
	OK: 1377240680 = 2041/08/23 (235 - ven) 06:51:20
*/

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

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

    printf("%s: %u = %d/%02d/%02d (%03d - %s) %02d:%02d:%02d\r\n",
           t, e,
           YEAR_TM(bt->tm_year), MON_TM(bt->tm_mon), bt->tm_mday,
           YDAY_TM(bt->tm_yday), giorno,
           bt->tm_hour, bt->tm_min, bt->tm_sec) ;
}

#ifdef __FRAMAC__
#   include "__fc_builtin.h"

#define NUM_EPOCHE      10

static time_t dammi_epoca(void)
{
    return Frama_C_interval(0, 2145916799) ;
}

#else
size_t quale = 0 ;
time_t vE[] = {
    0,
	2145916799,
    1269859165,
    300035158,
    1070618235,
    1961260196,
    1969486045,
    700258767,
    904878177,
    1853490565,
    258209272,
    1377240680,
} ;
#define NUM_EPOCHE      ( sizeof(vE) / sizeof(vE[0]) )

static time_t dammi_epoca(void)
{
    time_t e = 0 ;

    if (quale < NUM_EPOCHE) {
        e = vE[quale] ;
    }
    ++quale ;

    return e ;
}

#endif

struct tm vTM[] = {
    { .tm_year = TM_YEAR(1998), .tm_mon = TM_MON(1), .tm_mday = 1, .tm_hour = 0,
      .tm_min = 0, .tm_sec = 0 },
    { .tm_year = TM_YEAR(2065), .tm_mon = TM_MON(12), .tm_mday = 31, .tm_hour =
          23, .tm_min = 59, .tm_sec = 59 },

    { .tm_year = TM_YEAR(2038), .tm_mon = TM_MON(3), .tm_mday = 29, .tm_hour =
          11, .tm_min = 39, .tm_sec = 25 },
    { .tm_year = TM_YEAR(2007), .tm_mon = TM_MON(7), .tm_mday = 5, .tm_hour =
          16, .tm_min = 5, .tm_sec = 58 },
    { .tm_year = TM_YEAR(2031), .tm_mon = TM_MON(12), .tm_mday = 5, .tm_hour =
          10, .tm_min = 57, .tm_sec = 15 },
    { .tm_year = TM_YEAR(2060), .tm_mon = TM_MON(2), .tm_mday = 24, .tm_hour =
          19, .tm_min = 29, .tm_sec = 56 },
    { .tm_year = TM_YEAR(2060), .tm_mon = TM_MON(5), .tm_mday = 30, .tm_hour =
          0, .tm_min = 27, .tm_sec = 25 },
    { .tm_year = TM_YEAR(2020), .tm_mon = TM_MON(3), .tm_mday = 10, .tm_hour =
          21, .tm_min = 19, .tm_sec = 27 },
    { .tm_year = TM_YEAR(2026), .tm_mon = TM_MON(9), .tm_mday = 04, .tm_hour =
          4, .tm_min = 2, .tm_sec = 57 },
    { .tm_year = TM_YEAR(2056), .tm_mon = TM_MON(9), .tm_mday = 25, .tm_hour =
          11, .tm_min = 29, .tm_sec = 25 },
    { .tm_year = TM_YEAR(2006), .tm_mon = TM_MON(3), .tm_mday = 8, .tm_hour =
          13, .tm_min = 47, .tm_sec = 52 },
    { .tm_year = TM_YEAR(2041), .tm_mon = TM_MON(8), .tm_mday = 23, .tm_hour =
          7, .tm_min = 51, .tm_sec = 20 },
    //{.tm_year=TM_YEAR(), .tm_mon=TM_MON(), .tm_mday=, .tm_hour=, .tm_min=,
    // .tm_sec=}
} ;

#define NUM_TM      ( sizeof(vTM) / sizeof(vTM[0]) )

static bool stessa_data(const struct tm * sx, const struct tm * dx)
{
    bool uguali = false ;

    do {
        if (sx->tm_year != dx->tm_year) {
            break ;
        }
        if (sx->tm_mon != dx->tm_mon) {
            break ;
        }
        if (sx->tm_mday != dx->tm_mday) {
            break ;
        }
        if (sx->tm_hour != dx->tm_hour) {
            break ;
        }
        if (sx->tm_min != dx->tm_min) {
            break ;
        }
        if (sx->tm_sec != dx->tm_sec) {
            break ;
        }

        uguali = true ;
    } while (false) ;

    return uguali ;
}

#define MKTIME		mktime2
#define LOCALTIME	localtime2
//#define LOCALTIME	gmtime

int main(void)
{
	printf("sizeof(time_t) = %d\r\n", sizeof(time_t));
	time_t rif=0;
	struct tm * bdtlr = localtime(&rif) ;
	stampa_bt("localtime", rif, bdtlr) ;
	struct tm * bdtgr = gmtime(&rif) ;
	stampa_bt("gmtime", rif, bdtgr) ;


    printf("da tm a epoca\r\n");
    printf("=============\r\n");
    //@ loop unroll NUM_TM;
    for (size_t i = 0 ; i < NUM_TM ; ++i) {
        struct tm * tmp = vTM + i ;

        time_t e = MKTIME(tmp) ;
        if (-1==e) {
            printf("ERR %d (%d) \r\n", __LINE__, i) ;
            continue ;
        }

        struct tm * bdt = LOCALTIME(&e) ;
        if (NULL == bdt) {
            printf("ERR %d (%d) \r\n", __LINE__, i) ;
            continue ;
        }

        if ( stessa_data(tmp, bdt) ) {
            stampa_bt("OK", e, tmp) ;
        }
        else {
        	stampa_bt("ERR", e, tmp) ;
        	stampa_bt("\tERR", e, bdt) ;
            continue ;
        }
    }

    printf("da epoca a tm\r\n");
    printf("=============\r\n");
    //@ loop unroll NUM_EPOCHE;
    for (size_t i = 0 ; i < NUM_EPOCHE ; ++i) {
        time_t epoca = dammi_epoca() ;

        struct tm * tmp = LOCALTIME(&epoca) ;
        if (NULL == tmp) {
            printf("ERR %d (%d) \r\n", __LINE__, i) ;
            continue ;
        }

        time_t e = MKTIME(tmp) ;
        if (e != epoca) {
            printf("ERR %u e != epoca %u\r\n", e, epoca) ;
            continue ;
        }
        else {
            stampa_bt("OK", epoca, tmp) ;
        }
    }

    return 0 ;
}
