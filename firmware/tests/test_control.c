/* Unit tests for the two-site controller. Exit code 0 = all passed. */
#include <stdio.h>

#include "uzb_control.h"

static int failures;

#define CHECK(cond)                                                    \
    do {                                                               \
        if (!(cond)) {                                                 \
            fprintf(stderr, "%s:%d: CHECK failed: %s\n", __FILE__, __LINE__, #cond); \
            failures++;                                                \
        }                                                              \
    } while (0)

int main(void)
{
    uzb_two_site_t c;

    uzb_two_site_reset(&c);
    CHECK(uzb_two_site_step(&c, 1, 0, 0, 0, 0) == UZB_CMD_CLOSE && c.state == UZB_TS_CLOSING);
    CHECK(uzb_two_site_step(&c, 0, 1, 0, 0, 0) == UZB_CMD_OPEN && c.state == UZB_TS_OPENING);
    CHECK(uzb_two_site_step(&c, 0, 0, 0, 0, 0) == UZB_CMD_STOP && c.state == UZB_TS_STOPPED);
    CHECK(uzb_two_site_step(&c, 1, 1, 0, 0, 0) == UZB_CMD_STOP);
    CHECK(uzb_two_site_step(&c, 1, 0, 0, 0, 1) == UZB_CMD_STOP);
    CHECK(uzb_two_site_step(&c, 0, 1, 0, 1, 0) == UZB_CMD_STOP);

    CHECK(uzb_two_site_step(&c, 1, 0, 1, 0, 0) == UZB_CMD_SAFE_STOP && c.state == UZB_TS_SAFE);
    CHECK(uzb_two_site_step(&c, 1, 0, 0, 0, 0) == UZB_CMD_SAFE_STOP);
    CHECK(uzb_two_site_step(&c, 0, 1, 0, 0, 0) == UZB_CMD_SAFE_STOP);
    uzb_two_site_reset(&c);
    CHECK(uzb_two_site_step(&c, 0, 1, 0, 0, 0) == UZB_CMD_OPEN);

    if (failures)
        fprintf(stderr, "%d check(s) failed\n", failures);
    else
        printf("test_control: all checks passed\n");
    return failures ? 1 : 0;
}
