#include "stm32f4xx.h"

GPIO_InitTypeDef GPIO_InitStructure; //定义一个GPIO初始化用的结构体
TIM_TimeBaseInitTypeDef TIM_TimeBaseInitStructure; //定义一个定时器初始化结构体
NVIC_InitTypeDef NVIC_InitStructure; //定义一个NVIC初始化结构体

u16 PWM_Value = 0;//PWM值的临时变量

/*定义所需的初始化结构体变量*/
GPIO_InitTypeDef GPIO_InitStructure;
TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure;
TIM_OCInitTypeDef TIM_OCInitStructure;

/* 函数声明（延时用的） */
void delay_us(uint16_t nus);
void delay_ms(u16 nms);

int main(void)
{
/*初始化LED1的GPIO，用于闪烁(PB5)*/
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);//使能LED1的IO时钟
GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5; //选择LED PB5的IO
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT; //输出模式
GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; //推挽输出模式
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz; //LED可以慢一些省电
GPIO_SetBits(GPIOB,GPIO_Pin_5); //预先设置LED1（PB5）为熄灭
GPIO_Init(GPIOB, &GPIO_InitStructure); //初始化

RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3,ENABLE); ///使能定时器TIM3时钟

TIM_TimeBaseInitStructure.TIM_Period = 4999; //预装载值
TIM_TimeBaseInitStructure.TIM_Prescaler = 8400; //定时器预分频
TIM_TimeBaseInitStructure.TIM_CounterMode= TIM_CounterMode_Up;//向上计数模式
TIM_TimeBaseInit(TIM3,&TIM_TimeBaseInitStructure);//初始化定时器TIM3

TIM_ClearFlag(TIM3, TIM_FLAG_Update); //清除一次定时器更新标志

TIM_ITConfig(TIM3,TIM_IT_Update,ENABLE); //开启定时器3外设中断

NVIC_InitStructure.NVIC_IRQChannel = TIM3_IRQn; //定时器3中断向量
NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x01; //抢占优先级1
NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x03; //子优先级3
NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
NVIC_Init(&NVIC_InitStructure);

TIM_Cmd(TIM3,ENABLE); //使能定时器3,计时开始




/** 配置2个按键KEY1-KEY2所在的GPIO **/
/*开启 GPIOA GPIOC的时钟*/
RCC_AHB1PeriphClockCmd (RCC_AHB1Periph_GPIOA | RCC_AHB1Periph_GPIOC,ENABLE);

/*配置 KEY1 所在的GPIO（PA0）*/
GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0; //要初始化的引脚号
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN; //GPIO设置为输入模式
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz; //速度设置为2MHz
GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; //上拉电阻
/*使用上面配置的GPIO_InitStructure数据，初始化GPIOA*/
GPIO_Init( GPIOA, &GPIO_InitStructure );

/*配置 KEY2 所在的GPIO（PC13）*/
GPIO_InitStructure.GPIO_Pin = GPIO_Pin_13;//引脚号
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN; //GPIO设置为输入模式
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_2MHz; //速度设置为2MHz
GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; //上拉电阻
/*使用上面配置的GPIO_InitStructure数据，初始化GPIOC*/
GPIO_Init( GPIOC, &GPIO_InitStructure );



RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM3,ENABLE); //使能TIM3时钟
RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE); //使能PORTB时钟

GPIO_PinAFConfig(GPIOB,GPIO_PinSource5,GPIO_AF_TIM3); //连接PB5为定时器3复用

GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5; //PB5
GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF; //IO复用功能
GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz;//速度100MHz
GPIO_InitStructure.GPIO_OType = GPIO_OType_PP; //推挽复用输出
GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP; //上拉
GPIO_Init(GPIOB,&GPIO_InitStructure); //初始化PB5

TIM_TimeBaseStructure.TIM_Prescaler = 84; //定时器分频
TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up; //向上计数模式
TIM_TimeBaseStructure.TIM_Period = 500-1; //预装载值
TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1;

TIM_TimeBaseInit(TIM3,&TIM_TimeBaseStructure);//初始化TIM3

TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1; //脉宽调制模式
TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable; //使能比较输出
TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_Low; //输出极性
TIM_OC2Init(TIM3, &TIM_OCInitStructure);

TIM_OC2PreloadConfig(TIM3, TIM_OCPreload_Enable);//使能TIM3在CCR1预装载寄存器
TIM_ARRPreloadConfig(TIM3,ENABLE); //使能ARPE
TIM_Cmd(TIM3, ENABLE); //使能TIM3




/*间隔0.5秒，依次输入四个PWM值，LED1亮度会产生四种变化最后熄灭*/
TIM_SetCompare2(TIM3,499); //写入PWM值(0--499)
delay_ms(500);
TIM_SetCompare2(TIM3,300); //写入PWM值(0--499)
delay_ms(500);
TIM_SetCompare2(TIM3,100); //写入PWM值(0--499)
delay_ms(500);
TIM_SetCompare2(TIM3,0); //写入PWM值(0--499)















/* 主函数中检测两个按键，增加或减少PWM的值，改变亮度*/
while(1)
{
if(0 == GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_0))//按键1被按下
{
if(PWM_Value < 500)//小于500就加一，重新SetCompare2
{
PWM_Value++;
TIM_SetCompare2(TIM3,PWM_Value);
}
}
else if(0 == GPIO_ReadInputDataBit(GPIOC, GPIO_Pin_13))//按键2被按下
{
if(PWM_Value > 0)//大于0就减一，重新SetCompare2
{
PWM_Value--;
TIM_SetCompare2(TIM3,PWM_Value);
}
}
delay_ms(20);//检测间隔20毫秒，每秒50次（0-499大约10秒结束）
}

}



/*定时器3中断服务函数*/
void TIM3_IRQHandler(void)
{
static u8 i; //定义静态变量i，每次用完不会被清零
if(TIM_GetITStatus(TIM3,TIM_IT_Update)==SET) //判断是定时器3溢出中断
{
if(i) //用户代码：根据i的值点亮或熄灭LED1(PB5)
{
i = 0;
GPIO_ResetBits(GPIOB,GPIO_Pin_5);//点亮LED1(PB5)
}
else
{
i = 1;
GPIO_SetBits(GPIOB,GPIO_Pin_5);//熄灭LED1(PB5)
}
}
TIM_ClearITPendingBit(TIM3,TIM_IT_Update); //清除中断标志位
}








/***** 简单延时函数,ms,us *****/
void delay_us(uint16_t nus)
{
uint16_t i;
while(nus--)
{
i = 31;
while(i--);
}
}

void delay_ms(u16 nms)
{
uint16_t i;
while(nms--)
{
i = 33800;
while(i--);
}
}





















