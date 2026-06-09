/*
 * OutputTask.c
 *
 *  Created on: Jun 9, 2026
 *      Author: Seven T
 */
#include "OutputTask.h"

#define OUTPUT_TASK_TICK_MS 50U

void OutputTask(void *argument)
{
	for(;;) {
		osDelay(OUTPUT_TASK_TICK_MS);
	}
}
