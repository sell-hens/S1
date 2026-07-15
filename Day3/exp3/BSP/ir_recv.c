#include "ir_recv.h"
#include "delay.h"      // 用你已有的 systick_delay_us
#include "usart.h"      // 为了 printf 调试

/* NEC 时序 (μs) */
#define NEC_LEAD_LOW    9000
#define NEC_LEAD_HIGH   4500
#define NEC_BIT_LOW      560
#define NEC_BIT1_HIGH   1690
#define NEC_BIT0_HIGH    560

/* 全局解码结果 */
static IR_RecvData_t ir_data = {0};

/* 简单判区间 */
static uint8_t in_range(uint32_t val, uint32_t target, uint32_t tol)
{
    return (val > target - tol) && (val < target + tol);
}

/* 等待指定电平并返回持续时间(μs)，超时返回 0 */
static uint32_t wait_level(uint8_t level, uint32_t timeout_us)
{
    uint32_t cnt = 0;
    while (GPIO_ReadInputDataBit(IR_RECV_PORT, IR_RECV_PIN) == level)
    {
        cnt++;
        if (cnt >= timeout_us) return 0;
        systick_delay_us(1);
    }
    return cnt;
}

/*================ IR_Recv_Init =================*/
void IR_Recv_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct;
    EXTI_InitTypeDef EXTI_InitStruct;
    NVIC_InitTypeDef NVIC_InitStruct;

    /* 1. 开时钟 */
    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SYSCFG, ENABLE);  // F4 必须用 SYSCFG 映射 EXTI

    /* 2. GPIO：上拉输入 */
    GPIO_InitStruct.GPIO_Mode = GPIO_Mode_IN;
    GPIO_InitStruct.GPIO_PuPd = GPIO_PuPd_UP;
    GPIO_InitStruct.GPIO_Pin   = IR_RECV_PIN;
    GPIO_InitStruct.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(IR_RECV_PORT, &GPIO_InitStruct);

    /* 3. SYSCFG 映射 EXTI */
    SYSCFG_EXTILineConfig(EXTI_PortSourceGPIOA, EXTI_PinSource3);

    /* 4. EXTI：下降沿触发（NEC 引导码从 9ms 低开始） */
    EXTI_InitStruct.EXTI_Line    = IR_RECV_EXTI_LINE;
    EXTI_InitStruct.EXTI_Mode    = EXTI_Mode_Interrupt;
    EXTI_InitStruct.EXTI_Trigger = EXTI_Trigger_Falling;
    EXTI_InitStruct.EXTI_LineCmd = ENABLE;
    EXTI_Init(&EXTI_InitStruct);

    /* 5. NVIC */
    NVIC_InitStruct.NVIC_IRQChannel = IR_RECV_IRQn;
    NVIC_InitStruct.NVIC_IRQChannelPreemptionPriority = 1;
    NVIC_InitStruct.NVIC_IRQChannelSubPriority = 1;
    NVIC_InitStruct.NVIC_IRQChannelCmd = ENABLE;
    NVIC_Init(&NVIC_InitStruct);
}

/*================ IR_Recv =================*/
/* 查询式解码（在 main 循环里调用，不阻塞太久） */
void IR_Recv(void)
{
    uint32_t t;

    /* 空闲是高，检测到低说明可能有引导码 */
    if (GPIO_ReadInputDataBit(IR_RECV_PORT, IR_RECV_PIN) == Bit_SET)
        return;

    /* 等引导码低电平 9ms */
    t = wait_level(Bit_RESET, 15000);
    if (!in_range(t, 9000, 1500)) return;

    /* 引导码高 4.5ms */
    t = wait_level(Bit_SET, 6000);
    if (!in_range(t, 4500, 1500)) return;

    /* 32 位数据 */
    uint8_t bytes[4] = {0};
    for (uint8_t i = 0; i < 32; i++)
    {
        wait_level(Bit_RESET, 1000);          // 562μs 低
        t = wait_level(Bit_SET, 2500);        // 高：0≈562μs, 1≈1690μs
        if (t == 0) return;
        if (t > 1100)                         // 判 1
            bytes[i / 8] |= (1 << (i % 8));
    }

    ir_data.addr     = bytes[0];
    ir_data.addr_inv = bytes[1];
    ir_data.cmd      = bytes[2];
    ir_data.cmd_inv  = bytes[3];
    ir_data.valid    = 1;

    printf("IR: Addr=0x%02X Cmd=0x%02X\r\n", bytes[0], bytes[2]);
}

/* 取数据（读后不清 flag，简单版） */
IR_RecvData_t IR_Recv_GetData(void)
{
    return ir_data;
}

/*================ EXTI3 中断 =================*/
/* 这里只清标志，真正解码放 IR_Recv() 里做，避免 ISR 太长 */
void EXTI3_IRQHandler(void)
{
    if (EXTI_GetITStatus(EXTI_Line3) != RESET)
    {
        EXTI_ClearITPendingBit(EXTI_Line3);
    }
}