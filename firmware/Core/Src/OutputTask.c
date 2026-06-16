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
#define CSV_HEADER "event,timestamp_ms,accel_x_ms2,accel_y_ms2,accel_z_ms2,gyro_x_dps,gyro_y_dps,gyro_z_dps\r\n"

static void uart_print(const char *str)
{
	HAL_UART_Transmit(&huart2, (uint8_t *)str, strlen(str), HAL_MAX_DELAY);
}

void OutputTask(void *argument)
{
	IMUData_t rxData;
	char buf[128];
	uart_print(CSV_HEADER);

	for(;;) {
		if(osMessageQueueGet(DataQueueHandle, &rxData, NULL, OUTPUT_TASK_TICK_MS) == osOK)
		{
			snprintf(buf, sizeof(buf), "imu_data,%lu,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\r\n",
					rxData.timestamp_ms, rxData.accel_x, rxData.accel_y, rxData.accel_z, rxData.gyro_x, rxData.gyro_y, rxData.gyro_z);
			uart_print(buf);
		}
	}
}
