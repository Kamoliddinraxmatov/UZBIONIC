/* Mode switching by short co-contraction pulses. Mirrors emg/pipeline/modes.py. */
#ifndef UZB_MODES_H
#define UZB_MODES_H

#include "uzb_control.h"

typedef enum { UZB_MODE_POWER = 0, UZB_MODE_PINCH, UZB_MODE_POINT, UZB_MODE_WRIST, UZB_MODE_COUNT } uzb_mode_t;

enum { UZB_ACT_THUMB = 0, UZB_ACT_INDEX, UZB_ACT_MIDDLE, UZB_ACT_RING, UZB_ACT_LITTLE, UZB_ACT_WRIST };

/* Bit mask of actuators driven in each mode (bit n = actuator n). */
extern const unsigned char UZB_MODE_ACTUATORS[UZB_MODE_COUNT];

typedef struct {
    int pulse_min, pulse_max, lockout_len; /* in samples */
    uzb_mode_t mode;
    int safe;
    int both;
    int lockout;
} uzb_modes_t;

/* Timing in milliseconds; tunable design values, see modes.py. */
void uzb_modes_init(uzb_modes_t *m, float fs_hz, float pulse_min_ms, float pulse_max_ms, float lockout_ms);
void uzb_modes_reset(uzb_modes_t *m);
uzb_cmd_t uzb_modes_step(uzb_modes_t *m, int close_active, int open_active, int fault, int open_limit,
                         int closed_limit);

#endif
