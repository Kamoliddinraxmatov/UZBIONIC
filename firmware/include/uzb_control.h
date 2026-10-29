/* Grip control state machines. Mirrors emg/pipeline/state_machine.py and two_site.py. */
#ifndef UZB_CONTROL_H
#define UZB_CONTROL_H

typedef enum { UZB_CMD_STOP = 0, UZB_CMD_OPEN = 1, UZB_CMD_CLOSE = 2, UZB_CMD_SAFE_STOP = 3 } uzb_cmd_t;

/* Two-site control (transhumeral: biceps closes, triceps opens). Rest or co-contraction stops.
 * Any fault latches SAFE until uzb_two_site_reset(). */
typedef enum { UZB_TS_STOPPED = 0, UZB_TS_CLOSING, UZB_TS_OPENING, UZB_TS_SAFE } uzb_ts_state_t;

typedef struct {
    uzb_ts_state_t state;
} uzb_two_site_t;

void uzb_two_site_reset(uzb_two_site_t *c);
uzb_cmd_t uzb_two_site_step(uzb_two_site_t *c, int close_active, int open_active, int fault, int open_limit,
                            int closed_limit);

#endif
