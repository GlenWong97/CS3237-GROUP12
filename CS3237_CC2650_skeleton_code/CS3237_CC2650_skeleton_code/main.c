/*
 * Copyright (c) 2016, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 *    ======== i2ctmp007.c ========
 */

/* XDCtools Header files */
#include <xdc/std.h>
#include <xdc/runtime/System.h>

/* BIOS Header files */
#include <ti/sysbios/BIOS.h>
#include <ti/sysbios/knl/Clock.h>
#include <ti/sysbios/knl/Task.h>

/* TI-RTOS Header files */
#include <ti/drivers/PIN.h>
#include <ti/drivers/I2C.h>


/* TI-RTOS Header files */
#include <ti/drivers/GPIO.h>
#include <ti/drivers/PWM.h>


/* Example/Board Header files */
#include "Board.h"
#include "SensorOpt3001.h"
#include "SensorHdc1000.h"
#include "SensorUtil.h"
#include "SensorI2C.h"
#include "SensorMpu9250.h"
#define TASKSTACKSIZE       2048
#define TMP007_OBJ_TEMP     0x0003  /* Object Temp Result Register */


/*
 * Application LED pin configuration table:
 *   - All LEDs board LEDs are off.
 */
PIN_Config ledPinTable[] = {
Board_LED1 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW | PIN_PUSHPULL | PIN_DRVSTR_MAX,
                             Board_LED2 | PIN_GPIO_OUTPUT_EN | PIN_GPIO_LOW
                                     | PIN_PUSHPULL | PIN_DRVSTR_MAX,
                             PIN_TERMINATE };




/*
 *  ======== echoFxn ========
 *  Task for this function is created statically. See the project's .cfg file.
 */
#define HDC1000_REG_TEMP           0x00 // Temperature
#define HDC1000_REG_HUM            0x01 // Humidity
#define HDC1000_REG_CONFIG         0x02 // Configuration
#define HDC1000_REG_SERID_H        0xFB // Serial ID high
#define HDC1000_REG_SERID_M        0xFC // Serial ID middle
#define HDC1000_REG_SERID_L        0xFD // Serial ID low
#define HDC1000_REG_MANF_ID        0xFE // Manufacturer ID
#define HDC1000_REG_DEV_ID         0xFF // Device ID

// Fixed values
#define HDC1000_VAL_MANF_ID        0x5449
#define HDC1000_VAL_DEV_ID         0x1000
#define HDC1000_VAL_CONFIG         0x1000 // 14 bit, acquired in sequence
#define SENSOR_DESELECT()   SensorI2C_deselect()


Task_Struct tsk0Struct;
Task_Handle task;
Char task0Stack[TASKSTACKSIZE];

void readOPT3001()
{
    // config sensor
    SensorOpt3001_init();
    SensorOpt3001_enable(true);
    uint16_t rawdata = 0;
    if (!SensorOpt3001_test())
    {
        System_printf("SensorOpt3001 did not pass test!\n");
    }

    // read data
    
    // CS3237 TODO: add code to read optical sensor data. The API is provided in OPT3001 library code
    if (----- add your code here to read into variable rawdata -----){
    {
        System_printf("SensorOpt3001 Sample  %u: %d \n", i, rawdata);
        //CS3237 TODO: please add code to convert data. API provided in OPT3001 library code.
        // ...
    }
    else
    {
        System_printf("SensorOpt3001 I2C fault!\n");
    }
    System_flush();
    

}

void readMpu9250()
{

    // config MPU
    uint16_t rawdata = 0;
    SensorMpu9250_powerOn();
    if (!SensorMpu9250_init())
    {
        System_printf("SensorMPU9250_ cannot init!\n");
        return;
    }
    SensorMpu9250_accSetRange(ACC_RANGE_2G);
    SensorMpu9250_enable(9);
    SensorMpu9250_enableWom(1);
    if (!SensorMpu9250_test())
    {
        System_printf("SensorMPU9250_ did not pass test!\n");
    }
    unsigned int i;

    // read MPU data
    
    //CS3237 TODO: add code to read MPU accelermoter data. The API is provided in MPU library code.
    if (-----------add your code here to read into rawdata ------------) 
       {
           System_printf("SensorMPU9250_ no.Sample %u: %d (C)\n", i, rawdata);

           // See if conversion is necessary
           //....
        }
    else
        {
            System_printf("SensorMPU9250_ I2C fault!\n");
        }
        
    System_flush();
}

void PWMLED()
{
   // CS3237 TODO: Lookup PWM code from PWM Examples in TI-RTOS for CC2650 SensorTag.
}

// You need to write the task functions here.

/*
 *  ======== main ========
 */
int main(void)
{
    

    /* Call board init functions */
    Board_initGeneral();
    Board_initI2C();
    Board_initGPIO();
    Board_initPWM();

    GPIO_write(Board_LED0, Board_LED_ON);

    // CS3237 TODO: Create task structures for reading sensor data and performing PWM. Do not forgot to open I2C, which is available in the library file SensorI2C.c.

    // CS3237 new tip: It might happen that you get I2C fault or some weird data in the first read. You can get right data if you read sensor again.

    System_printf("Starting the I2C example\nSystem provider is set to SysMin."
                  " Halt the target to view any SysMin contents in ROV.\n");
    /* SysMin will only print to the console when you call flush or exit */
    System_flush();

    /* Start BIOS */
    BIOS_start();

    return (0);
}
