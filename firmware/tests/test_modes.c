/* Unit tests for co-contraction mode switching (1 kHz so 1 sample = 1 ms). */
#include <stdio.h>

#include "uzb_modes.h"

static int failures;

#define CHECK(cond)                                                                    \
    do {                                                                               \
        if (!(cond)) {                                                                 \
            fprintf(stderr, "%s:%d: CHECK failed: %s\n", __FILE__, __LINE__, #cond); \
            failures++;                                                                \
        }                                                                              \
    } while (0)

static uzb_cmd_t run(uzb_modes_t *m, int c, int o, int n)
{
    uzb_cmd_t cmd = UZB_CMD_STOP;
    for (int i = 0; i < n; i++)
        cmd = uzb_modes_step(m, c, o, 0, 0, 0);
    return cmd;
}

static uzb_modes_t fresh(void)
{
    uzb_modes_t m;
    uzb_modes_init(&m, 1000.0f, 50.0f, 800.0f, 300.0f);
    return m;
}

int main(void)
{
    uzb_modes_t m = fresh();
    run(&m, 1, 1, 200);
    CHECK(m.mode == UZB_MODE_POWER);
    CHECK(run(&m, 1, 0, 300) == UZB_CMD_STOP); /* lockout */
    CHECK(m.mode == UZB_MODE_PINCH);
    CHECK(run(&m, 1, 0, 1) == UZB_CMD_CLOSE);

    m = fresh();
    run(&m, 1, 1, 20);
    run(&m, 0, 0, 5);
    CHECK(m.mode == UZB_MODE_POWER);
    run(&m, 1, 1, 1000);
    run(&m, 0, 0, 5);
    CHECK(m.mode == UZB_MODE_POWER);

    m = fresh();
    for (int i = 0; i < 4; i++) {
        run(&m, 1, 1, 200);
        run(&m, 0, 0, 400);
    }
    CHECK(m.mode == UZB_MODE_POWER);

    CHECK(UZB_MODE_ACTUATORS[UZB_MODE_PINCH] == ((1u << UZB_ACT_THUMB) | (1u << UZB_ACT_INDEX)));
    CHECK(UZB_MODE_ACTUATORS[UZB_MODE_WRIST] == (1u << UZB_ACT_WRIST));

    m = fresh();
    m.mode = UZB_MODE_PINCH;
    CHECK(uzb_modes_step(&m, 1, 0, 1, 0, 0) == UZB_CMD_SAFE_STOP);
    run(&m, 1, 1, 200);
    run(&m, 0, 0, 400);
    CHECK(m.mode == UZB_MODE_PINCH);
    CHECK(run(&m, 1, 0, 1) == UZB_CMD_SAFE_STOP);
    uzb_modes_reset(&m);
    CHECK(run(&m, 1, 0, 1) == UZB_CMD_CLOSE);

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("test_modes: all checks passed\n");
    return failures ? 1 : 0;
}
