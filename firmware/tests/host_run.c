/* PC harness: reads "close_x,open_x" lines on stdin, runs both channels and the mode
 * controller, prints "close_env,open_env,close_act,open_act,cmd,mode" per sample.
 * Usage: host_run <close_on> <close_off> <open_on> <open_off> */
#include <stdio.h>
#include <stdlib.h>

#include "uzb_modes.h"
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
    uzb_modes_t ctl;
    uzb_modes_init(&ctl, UZB_FS_HZ, 50.0f, 800.0f, 300.0f);

    float xc, xo;
    while (scanf("%f,%f", &xc, &xo) == 2) {
        float ec, eo;
        int ac = uzb_channel_step(&close_ch, xc, &ec);
        int ao = uzb_channel_step(&open_ch, xo, &eo);
        uzb_cmd_t cmd = uzb_modes_step(&ctl, ac, ao, 0, 0, 0);
        printf("%.9g,%.9g,%d,%d,%d,%d\n", ec, eo, ac, ao, (int)cmd, (int)ctl.mode);
    }
    return 0;
}
