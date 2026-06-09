/*
 * DataAcqTask.h
 *
 *  Created on: Jun 8, 2026
 *      Author: Seven T
 */

#ifndef INC_DATAACQTASK_H_
#define INC_DATAACQTASK_H_

#include "cmsis_os.h"
#include "i2c.h"

extern osMessageQueueId_t DataQueueHandle;
extern I2C_HandleTypeDef hi2c1;

// Accel in m/s^2
// Gyro in dps
typedef struct {
	double accel_x;
	double accel_y;
	double accel_z;
	double gyro_x;
	double gyro_y;
	double gyro_z;
} IMUData_t;

void DataAcqTask(void *argument);

#endif /* INC_DATAACQTASK_H_ */
