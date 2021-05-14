#ifndef MIDDLEWARES_RCCS_PRM_PRM_H_
#define MIDDLEWARES_RCCS_PRM_PRM_H_

#include <stdbool.h>

void PRM_iniz(void);

bool PRM_cld_erase(void);

bool PRM_nsp_scrivi(const char * v);
const char * PRM_nsp_leggi(void);


#else
#	warning prm.h incluso
#endif
