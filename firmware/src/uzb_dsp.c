#include "uzb_dsp.h"

#include <math.h>
#include <string.h>

void uzb_biquad_init(uzb_biquad_t *f, const float c[5])
{
    memcpy(f->c, c, sizeof f->c);
    f->z1 = f->z2 = 0.0f;
}

/* Transposed direct form II, same structure as scipy.signal.sosfilt. */
float uzb_biquad_step(uzb_biquad_t *f, float x)
{
    const float *c = f->c;
    float y = c[0] * x + f->z1;
    f->z1 = c[1] * x - c[3] * y + f->z2;
    f->z2 = c[2] * x - c[4] * y;
    return y;
}

void uzb_rms_init(uzb_rms_t *r)
{
    memset(r, 0, sizeof *r);
}

float uzb_rms_step(uzb_rms_t *r, float x)
{
    float s = x * x;
    r->sum += (double)s - (double)r->sq[r->idx];
    r->sq[r->idx] = s;
    r->idx = (r->idx + 1) % UZB_WINDOW_SAMPLES;
    if (r->count < UZB_WINDOW_SAMPLES)
        r->count++;
    double mean = r->sum / r->count;
    return mean > 0.0 ? (float)sqrt(mean) : 0.0f;
}

void uzb_detector_init(uzb_detector_t *d, float on, float off)
{
    d->on = on;
    d->off = off;
    d->active = 0;
    d->count = 0;
}

int uzb_detector_step(uzb_detector_t *d, float env)
{
    if (!d->active) {
        d->count = env > d->on ? d->count + 1 : 0;
        if (d->count >= UZB_MIN_ON_SAMPLES) {
            d->active = 1;
            d->count = 0;
        }
    } else {
        d->count = env < d->off ? d->count + 1 : 0;
        if (d->count >= UZB_MIN_OFF_SAMPLES) {
            d->active = 0;
            d->count = 0;
        }
    }
    return d->active;
}

void uzb_channel_init(uzb_channel_t *ch, float on, float off)
{
    for (int i = 0; i < UZB_BP_SECTIONS; i++)
        uzb_biquad_init(&ch->bp[i], UZB_BP_COEFFS[i]);
    uzb_biquad_init(&ch->notch, UZB_NOTCH_COEFFS);
    uzb_rms_init(&ch->rms);
    uzb_detector_init(&ch->det, on, off);
}

int uzb_channel_step(uzb_channel_t *ch, float x, float *env)
{
    float y = x;
    for (int i = 0; i < UZB_BP_SECTIONS; i++)
        y = uzb_biquad_step(&ch->bp[i], y);
    y = uzb_biquad_step(&ch->notch, y);
    float e = uzb_rms_step(&ch->rms, y);
    if (env)
        *env = e;
    return uzb_detector_step(&ch->det, e);
}
