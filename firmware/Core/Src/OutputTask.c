/*
 * OutputTask.c
 *
 *  Created on: Jun 9, 2026
 *      Author: Seven T
 */
#include "OutputTask.h"
#include "DataAcqTask.h"
#include <stdio.h>
#include <string.h>

#define OUTPUT_TASK_TICK_MS 50U
#define CSV_HEADER "accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z\r\n"

static void uart_print(const char *str)
{
	HAL_UART_Transmit(&huart2, (uint8_t *)str, strlen(str), HAL_MAX_DELAY);
}

void OutputTask(void *argument)
{
	imuData rxData;
	char buf[128];
	uart_print(CSV_HEADER);

	for(;;) {
		if(osMessgeQueueGet(DataQueueHandle, &rxData, NULL, OUTPUT_TASK_TICK_MS) == osOk)
		{
			snprintf(buf, sizeof(buf), "%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\r\n", rxData.accel_x, rxData.accel_y, rxData.accel_z, rxData.gyro_x, rxData.gyro_y, rxData.gyro_z);
			uart_print(buf);
		}
	}
}
