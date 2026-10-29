#include "uzb_control.h"

void uzb_two_site_reset(uzb_two_site_t *c)
{
    c->state = UZB_TS_STOPPED;
}

uzb_cmd_t uzb_two_site_step(uzb_two_site_t *c, int close_active, int open_active, int fault, int open_limit,
                            int closed_limit)
{
    if (fault || c->state == UZB_TS_SAFE) {
        c->state = UZB_TS_SAFE;
        return UZB_CMD_SAFE_STOP;
    }
    if (close_active && !open_active && !closed_limit) {
        c->state = UZB_TS_CLOSING;
        return UZB_CMD_CLOSE;
    }
    if (open_active && !close_active && !open_limit) {
        c->state = UZB_TS_OPENING;
        return UZB_CMD_OPEN;
    }
    c->state = UZB_TS_STOPPED;
    return UZB_CMD_STOP;
}
