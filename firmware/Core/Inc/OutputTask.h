/*
 * OutputTask.h
 *
 *  Created on: Jun 9, 2026
 *      Author: Seven T
 */

#ifndef INC_OUTPUTTASK_H_
#define INC_OUTPUTTASK_H_

#include "cmsis_os.h"
#include "usart.h"

extern osMessageQueueId_t DataQueueHandle;
extern UART_HandleTypeDef huart2;

void OutputTask(void *argument);


#endif /* INC_OUTPUTTASK_H_ */
