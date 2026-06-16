/*
 * DataAcqTask.c
 *
 *  Created on: Jun 8, 2026
 *      Author: Seven T
 */
#include "DataAcqTask.h"
#include "bno055_stm32.h"

#define DAQ_TASK_TICK_MS 50U

static IMUData_t imuData;

/* USER CODE BEGIN Header_DataAcqTask */
/**
  * @brief  Function implementing the Data thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_DataAcqTask */
void DataAcqTask(void *argument)
{
  /* USER CODE BEGIN 5 */
	bno055_assignI2C(&hi2c1);
	bno055_setup();
	bno055_setOperationModeNDOF();

	bno055_vector_t accel;
	bno055_vector_t gyro;

	uint32_t tick = osKernelGetTickCount();

  /* Infinite loop */
	for(;;)
	{
		tick += DAQ_TASK_TICK_MS;
		accel = bno055_getVectorAccelerometer();
		gyro = bno055_getVectorGyroscope();
		imuData.timestamp_ms = osKernelGetTickCount();
		imuData.accel_x = accel.x;
		imuData.accel_y = accel.y;
		imuData.accel_z = accel.z;
		imuData.gyro_x = gyro.x;
		imuData.gyro_y = gyro.y;
		imuData.gyro_z = gyro.z;
//		printf("[Data] Accel: x = %.2f, y = %.2f, z = %.2f\nGyro: x = %.2f, y = %.2f, z = %.2f\n", imuData.accel_x, imuData.accel_y, imuData.accel_z, imuData.gyro_x, imuData.gyro_y, imuData.gyro_z);
		if(osMessageQueuePut(DataQueueHandle, &imuData, 0, 5) != osOK) {
			// dropped samples
		}
		osDelayUntil(tick);
	}
  /* USER CODE END 5 */
}
