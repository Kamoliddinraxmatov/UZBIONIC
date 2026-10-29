#include "uzb_modes.h"

#include <math.h>

#define BIT(n) (1u << (n))

const unsigned char UZB_MODE_ACTUATORS[UZB_MODE_COUNT] = {
    [UZB_MODE_POWER] = BIT(UZB_ACT_THUMB) | BIT(UZB_ACT_INDEX) | BIT(UZB_ACT_MIDDLE) | BIT(UZB_ACT_RING) |
                       BIT(UZB_ACT_LITTLE),
    [UZB_MODE_PINCH] = BIT(UZB_ACT_THUMB) | BIT(UZB_ACT_INDEX),
    [UZB_MODE_POINT] = BIT(UZB_ACT_THUMB) | BIT(UZB_ACT_MIDDLE) | BIT(UZB_ACT_RING) | BIT(UZB_ACT_LITTLE),
    [UZB_MODE_WRIST] = BIT(UZB_ACT_WRIST),
};

/* Round half to even, matching Python's round(). */
static int ms_to_samples(float ms, float fs_hz)
{
    return (int)nearbyintf(ms * fs_hz / 1000.0f);
}

void uzb_modes_init(uzb_modes_t *m, float fs_hz, float pulse_min_ms, float pulse_max_ms, float lockout_ms)
{
    m->pulse_min = ms_to_samples(pulse_min_ms, fs_hz);
    m->pulse_max = ms_to_samples(pulse_max_ms, fs_hz);
    m->lockout_len = ms_to_samples(lockout_ms, fs_hz);
    m->mode = UZB_MODE_POWER;
    uzb_modes_reset(m);
}

void uzb_modes_reset(uzb_modes_t *m)
{
    m->safe = 0;
    m->both = 0;
    m->lockout = 0;
}

uzb_cmd_t uzb_modes_step(uzb_modes_t *m, int close_active, int open_active, int fault, int open_limit,
                         int closed_limit)
{
    if (fault || m->safe) {
        m->safe = 1;
        return UZB_CMD_SAFE_STOP;
    }
    if (close_active && open_active) {
        m->both++;
        return UZB_CMD_STOP;
    }
    if (m->both) {
        if (m->both >= m->pulse_min && m->both <= m->pulse_max) {
            m->mode = (uzb_mode_t)((m->mode + 1) % UZB_MODE_COUNT);
            m->lockout = m->lockout_len;
        }
        m->both = 0;
    }
    if (m->lockout) {
        m->lockout--;
        return UZB_CMD_STOP;
    }
    if (close_active && !closed_limit)
        return UZB_CMD_CLOSE;
    if (open_active && !open_limit)
        return UZB_CMD_OPEN;
    return UZB_CMD_STOP;
}
