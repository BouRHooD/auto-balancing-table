#include <Servo.h>

// <---------- SETTINGS PLATFORM ---------->

/* Максимальная и минимальная ширина импульса из даташита сервопривода */
#define MAX_SERVO_PULSE 2200
#define MIN_SERVO_PULSE 700

/* Положение сервоприводов, установленных в обратном направлении */
#define INVERSE_SERVO_1 0
#define INVERSE_SERVO_2 2
#define INVERSE_SERVO_3 4

/* Вычисление углов */
#define degToRad(degree) (degree * PI / 180.0)
#define radToDeg(radians)  ((radians * 180.0) / PI)

/* Множитель, используемый для преобразования радиан в импульсы в нас */
#define SERVO_MULT ( 400.0/(PI/4.0))

/* Максимальный и минимальный диапазон сервоприводов в радианах */
#define SERVO_MIN degToRad(-80)
#define SERVO_MAX degToRad(80)

/* Значения платформы в миллиметрах */
/* Длина руки сервопривода */
#define LENGTH_SERVO_ARM 15
/* Длина стержней */
#define LENGTH_SERVO_LEG 120
/* Высота платформы в стандарном положении (Это значение должно быть примерно равно длине стержней)
*/
#define PLATFORM_HEIGHT_DEFAULT 115
/* Радиус верхнего столика платформы */
#define PLATFORM_TOP_RADIUS 45.5
/* Радиус основания платформы */
#define PLATFORM_BASE_RADIUS 67.5
/* Угол между двумя точками оси сервоприводов */
#define THETA_P_ANGLE degToRad(67)
/* Угол между двумя точками крепления платформы */
#define THETA_R_ANGLE degToRad(12)
/* Не изменяется */
#define THETA_ANGLE ((PI/3.0 - THETA_P_ANGLE) / 2.0)
/* Здесь вы помещаете импульсы каждого из ваших сервоприводов в соответствии с их положением по горизонтали. */
#define SERVO_ZERO_POSITION 1550, 1450, 1350, 1600, 1500, 1600
/* Здесь вы помещаете вращение сервоприводов относительно оси X */
#define BETA_ANGLES PI / 2, -PI / 2, -PI / 6, 5 * PI / 6, -5 * PI / 6, PI / 6

// <--------------------------------------->

Servo servos[6];
float servosPosition[6];


double beta[6];
int servoHorPos[6];
float alpha[6]; 
float baseJoint[6][3], platformJoint[6][3], legLength[6][3];
  
//Init rotation and translation with zeros
float rotation[3];
float translation[3];

//Hold the values readed from Serial
float* values = new float[6];

void setup() {
  Serial.begin(38400);
  Serial.println("Init...");
  servos[0].attach(3, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
  servos[1].attach(5, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
  servos[2].attach(6, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
  servos[3].attach(9, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
  servos[4].attach(10, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
  servos[5].attach(11, MIN_SERVO_PULSE, MAX_SERVO_PULSE);
}

void loop() 
{
  //Формат сообщения: 30,0,20,0,0,0 
  // 30,0,20,0,0,0 - X, Y, Z, GX, GY, GZ
  if(Serial.available() >= 11)
  {
    String rsp = Serial.readStringUntil('\n');
    Serial.println(rsp);
    values = getValuesFromString(rsp);
    translation[0] = values[0];
    translation[1] = values[1];
    translation[2] = values[2];
    rotation[0] = values[3];
    rotation[1] = values[4];
    rotation[2] = values[5];
  }

  // Получить позицию сервоприводов
  getServoPosition(translation, rotation, servosPosition); 

  // Установите сервоприводы в желаемое положение
  for(int i = 0; i < 6; i++){      
    servos[i].writeMicroseconds(servosPosition[i]);
  }  
}


// Здесь мы извлекаем значения из полученной строки.
float* getValuesFromString(String rsp){
  int lastIndex = 0, j = 0, i;
  float values[6];
  for(i = 0; i < rsp.length(); i++){
    if(rsp.substring(i, i+1) == ","){
      values[j++] = (rsp.substring(lastIndex, i)).toFloat(); 
      lastIndex = i + 1;
      
      if( j == 6) break;
    }
  }
  values[j] = (rsp.substring(lastIndex, i)).toFloat(); 
  return values;
}

void getServoPosition(float transl[3], float rotat[3], float servoPos[6]) 
{
  setTranslation(transl);
  setRotation(rotat);
  calcLegLength();
  calcAlpha();
  calcServoPos(servoPos);
}


void setTranslation(float pos[3]) 
{
  translation[0] = pos[0];
  translation[1] = pos[1];
  translation[2] = pos[2] + PLATFORM_HEIGHT_DEFAULT;
}


void setRotation(float rot[3]) 
{
  rotation[0] = rot[0];
  rotation[1] = rot[1];
  rotation[2] = rot[2];
}


void getRotationMatrix(float rotationMatrix[3][3])
{
  float roll = rotation[0];
  float pitch = rotation[1];
  float yaw = rotation[2];

  rotationMatrix[0][0] =  cos(yaw) * cos(pitch);
  rotationMatrix[1][0] = -sin(yaw) * cos(roll) + cos(yaw) * sin(pitch) * sin(roll);
  rotationMatrix[2][0] =  sin(yaw) * sin(roll) + cos(yaw) * cos(roll)  * sin(pitch);
  
  rotationMatrix[0][1] = sin(yaw)  * cos(pitch);
  rotationMatrix[1][1] = cos(yaw)  * cos(roll) + sin(yaw) * sin(pitch) * sin(roll);
  rotationMatrix[2][1] = cos(pitch)* sin(roll);
  
  rotationMatrix[0][2] = -sin(pitch);
  rotationMatrix[1][2] = -cos(yaw)   * sin(roll) + sin(yaw) * sin(pitch) * cos(roll);
  rotationMatrix[2][2] =  cos(pitch) * cos(roll);
}


void calcLegLength() 
{
  float rotMatrix[3][3] = {};

  getRotationMatrix(rotMatrix);

  for (int i = 0; i < 6; i++) {
    legLength[i][0] = (rotMatrix[0][0] * platformJoint[i][0]) + (rotMatrix[0][1] * platformJoint[i][1]) + (rotMatrix[0][2] * platformJoint[i][2]);
    legLength[i][1] = (rotMatrix[1][0] * platformJoint[i][0]) + (rotMatrix[1][1] * platformJoint[i][1]) + (rotMatrix[1][2] * platformJoint[i][2]);
    legLength[i][2] = (rotMatrix[2][0] * platformJoint[i][0]) + (rotMatrix[2][1] * platformJoint[i][1]) + (rotMatrix[2][2] * platformJoint[i][2]);
    
    legLength[i][0] += translation[0]; 
    legLength[i][1] += translation[1]; 
    legLength[i][2] += translation[2]; 
  }
}  


void calcAlpha() 
{
  float basePoint[3], Li[3];
  double min, max, dist;

  for (int i = 0; i < 6; i++)
  {    
    min = SERVO_MIN; 
    max = SERVO_MAX;
    for (int j = 0; j < 20; j++)
    {
      basePoint[0] = LENGTH_SERVO_ARM * cos(alpha[i]) * cos(beta[i]) + baseJoint[i][0];
      basePoint[1] = LENGTH_SERVO_ARM * cos(alpha[i]) * sin(beta[i]) + baseJoint[i][1];
      basePoint[2] = LENGTH_SERVO_ARM * sin(alpha[i]);

      Li[0] = legLength[i][0] - basePoint[0];
      Li[1] = legLength[i][1] - basePoint[1];
      Li[2] = legLength[i][2] - basePoint[2];

      dist = sqrt(Li[0] * Li[0] + Li[1] * Li[1] + Li[2] * Li[2]);

      if (abs(LENGTH_SERVO_LEG - dist) < 0.01) 
      {
        break;
      }
      
      if (dist < LENGTH_SERVO_LEG) 
      {
        max = alpha[i];
      }
      else 
      {
        min = alpha[i];
      }
      if (max == SERVO_MIN || min == SERVO_MAX) 
      {
        break;
      }
      
      alpha[i] = min + (max - min) / 2;
    }
  }
}


void calcServoPos(float servoPos[6]) 
{
  for (int i = 0; i < 6; i++) 
  {
    if (i == INVERSE_SERVO_1 || i == INVERSE_SERVO_2 || i == INVERSE_SERVO_3) 
    {
      servoPos[i] = constrain(servoHorPos[i] - (alpha[i]) *  SERVO_MULT , MIN_SERVO_PULSE, MAX_SERVO_PULSE);
    }
    else
    {
      servoPos[i] = constrain(servoHorPos[i] + (alpha[i]) *  SERVO_MULT , MIN_SERVO_PULSE, MAX_SERVO_PULSE);
    }
  }
}
