/* PC harness: reads "close_x,open_x" lines on stdin, runs both channels and the two-site
 * controller, prints "close_env,open_env,close_act,open_act,cmd" per sample.
 * Usage: host_run <close_on> <close_off> <open_on> <open_off> */
#include <stdio.h>
#include <stdlib.h>

#include "uzb_control.h"
#include "uzb_dsp.h"

int main(int argc, char **argv)
{
    if (argc != 5) {
        fprintf(stderr, "usage: %s close_on close_off open_on open_off\n", argv[0]);
        return 2;
    }
    uzb_channel_t close_ch, open_ch;
    uzb_channel_init(&close_ch, strtof(argv[1], NULL), strtof(argv[2], NULL));
    uzb_channel_init(&open_ch, strtof(argv[3], NULL), strtof(argv[4], NULL));
    uzb_two_site_t ctl;
    uzb_two_site_reset(&ctl);

    float xc, xo;
    while (scanf("%f,%f", &xc, &xo) == 2) {
        float ec, eo;
        int ac = uzb_channel_step(&close_ch, xc, &ec);
        int ao = uzb_channel_step(&open_ch, xo, &eo);
        uzb_cmd_t cmd = uzb_two_site_step(&ctl, ac, ao, 0, 0, 0);
        printf("%.9g,%.9g,%d,%d,%d\n", ec, eo, ac, ao, (int)cmd);
    }
    return 0;
}
