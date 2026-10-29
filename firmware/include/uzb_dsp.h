/* Per-channel sEMG processing, sample by sample. Mirrors emg/pipeline (Python reference).
 * Hardware-independent: no MCU headers here, so it builds and is tested on a PC. */
#ifndef UZB_DSP_H
#define UZB_DSP_H

#include "uzb_coeffs.h"

typedef struct {
    float c[5]; /* b0, b1, b2, a1, a2 */
    float z1, z2;
} uzb_biquad_t;

void uzb_biquad_init(uzb_biquad_t *f, const float c[5]);
float uzb_biquad_step(uzb_biquad_t *f, float x);

/* Causal moving RMS over UZB_WINDOW_SAMPLES; shorter window until the buffer fills. */
typedef struct {
    float sq[UZB_WINDOW_SAMPLES];
    double sum; /* double keeps the running sum from drifting; revisit on an MCU without an FPU for double */
    int idx;
    int count;
} uzb_rms_t;

void uzb_rms_init(uzb_rms_t *r);
float uzb_rms_step(uzb_rms_t *r, float x);

/* Hysteresis detector: on after env > on for UZB_MIN_ON_SAMPLES, off after env < off for UZB_MIN_OFF_SAMPLES. */
typedef struct {
    float on, off;
    int active;
    int count;
} uzb_detector_t;

void uzb_detector_init(uzb_detector_t *d, float on, float off);
int uzb_detector_step(uzb_detector_t *d, float env);

typedef struct {
    uzb_biquad_t bp[UZB_BP_SECTIONS];
    uzb_biquad_t notch;
    uzb_rms_t rms;
    uzb_detector_t det;
} uzb_channel_t;

void uzb_channel_init(uzb_channel_t *ch, float on, float off);
/* Returns 1 while the muscle is active; writes the envelope to *env if env != NULL. */
int uzb_channel_step(uzb_channel_t *ch, float x, float *env);

#endif
