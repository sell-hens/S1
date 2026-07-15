#ifndef __IR_RECV_H
#define __IR_RECV_H

#include "stm32f4xx.h"

/* 引脚定义（按需改） */
#define IR_RECV_PORT        GPIOA
#define IR_RECV_PIN         GPIO_Pin_3
#define IR_RECV_EXTI_LINE  EXTI_Line3
#define IR_RECV_IRQn       EXTI3_IRQn

/* NEC 解码结果 */
typedef struct
{
    uint8_t addr;     // 用户码
    uint8_t addr_inv; // 用户反码
    uint8_t cmd;      // 按键码
    uint8_t cmd_inv;  // 按键反码
    uint8_t valid;    // 1=本次解码有效
} IR_RecvData_t;

/* 函数声明 */
void IR_Recv_Init(void);
void IR_Recv(void);
IR_RecvData_t IR_Recv_GetData(void);

#endif /* __IR_RECV_H */