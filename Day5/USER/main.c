#include "stm32f4xx.h"
#include "usart.h"
#include "delay.h"
#include "dht11.h"
#include "mq.h"
#include "lcd_ili9341.h"
#include <stdio.h>

#define TEMP_LIMIT 35
#define MQ_LIMIT   2000

void BEEP_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_8;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_25MHz;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;

    GPIO_Init(GPIOA, &GPIO_InitStructure);

    GPIO_SetBits(GPIOA, GPIO_Pin_8);    // PA8高电平，蜂鸣器不响
}

void BEEP_ON(void)
{
    GPIO_ResetBits(GPIOA, GPIO_Pin_8);  // PA8低电平，蜂鸣器响
}

void BEEP_OFF(void)
{
    GPIO_SetBits(GPIOA, GPIO_Pin_8);    // PA8高电平，蜂鸣器停止
}

void LED_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;

    RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);

    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_0 | GPIO_Pin_1;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
    GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_25MHz;
    GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;

    GPIO_Init(GPIOB, &GPIO_InitStructure);

    GPIO_SetBits(GPIOB, GPIO_Pin_5 | GPIO_Pin_0 | GPIO_Pin_1);  // 高电平，LED灭
}

void LED_ON(void)
{
    GPIO_ResetBits(GPIOB, GPIO_Pin_5 | GPIO_Pin_0 | GPIO_Pin_1); // 低电平，LED亮
}

void LED_OFF(void)
{
    GPIO_SetBits(GPIOB, GPIO_Pin_5 | GPIO_Pin_0 | GPIO_Pin_1);   // 高电平，LED灭
}



int main(void)
{
    DHT11_Data dht11_data;
    uint16_t mq_value;
    char str[50];

    UART2_Init(115200);
    DHT11_Init();
    MQ_Init();
    LCD_Init();
    BEEP_Init();
		LED_Init();
	
    LCD_SetColors(WHITE, BLACK);
    LCD_Clear(0, 0, LCD_GetLenX(), LCD_GetLenY());

    LCD_DispStringEN(10, 10, 0, "Smart Kitchen System");
    LCD_DispStringEN(10, 35, 0, "DHT11 + MQ + BEEP");

    printf("Smart Kitchen System Start\r\n");

    while (1)
    {
        mq_value = MQ_ReadValue();

        if (DHT11_ReadData(&dht11_data) == 0)
        {
            LCD_Clear(0, 60, LCD_GetLenX(), 180);

            sprintf(str, "Temp: %d.%d C", dht11_data.temp_int, dht11_data.temp_deci);
            LCD_DispStringEN(10, 65, 0, str);

            sprintf(str, "Humi: %d.%d %%", dht11_data.humi_int, dht11_data.humi_deci);
            LCD_DispStringEN(10, 90, 0, str);

            sprintf(str, "MQ: %d", mq_value);
            LCD_DispStringEN(10, 115, 0, str);

            printf("Temp:%d.%dC  Humi:%d.%d%%  MQ:%d\r\n",
                   dht11_data.temp_int,
                   dht11_data.temp_deci,
                   dht11_data.humi_int,
                   dht11_data.humi_deci,
                   mq_value);

            if (dht11_data.temp_int >= TEMP_LIMIT || mq_value >= MQ_LIMIT)
            {
                BEEP_ON();
								LED_ON();
							
                LCD_SetColors(RED, BLACK);
                LCD_DispStringEN(10, 145, 0, "Status: ALARM!");
                LCD_DispStringEN(10, 170, 0, "Danger detected!");

                LCD_SetColors(WHITE, BLACK);

                printf("Warning! Kitchen danger detected!\r\n");
            }
            else
            {
                BEEP_OFF();
								LED_OFF();
							
                LCD_SetColors(GREEN, BLACK);
                LCD_DispStringEN(10, 145, 0, "Status: SAFE ");
                LCD_DispStringEN(10, 170, 0, "Environment normal");

                LCD_SetColors(WHITE, BLACK);
            }
        }
        else
        {
            LCD_Clear(0, 60, LCD_GetLenX(), 120);
            LCD_SetColors(RED, BLACK);
            LCD_DispStringEN(10, 65, 0, "DHT11 Read Error!");
            LCD_SetColors(WHITE, BLACK);

            printf("DHT11 Read Error!\r\n");
        }

        delay_ms(1000);
    }
}