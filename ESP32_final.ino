
#define USE_ARDUINO_INTERRUPTS false

#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include <Wire.h>
#include <PulseSensorPlayground.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_NeoPixel.h>
#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define BME_SCK 18
#define BME_MISO 19
#define BME_MOSI 23
#define BME_CS 5

#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BME680 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK);

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1:
#define LED_PIN    2

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 24

const int OUTPUT_TYPE = SERIAL_PLOTTER;

const int PULSE_INPUT = 15;
const int THRESHOLD = 350;   // Adjust this number to avoid noise when idle

byte samplesUntilReport;
const byte SAMPLES_PER_SERIAL_SAMPLE = 10;

PulseSensorPlayground pulseSensor;

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(24, 2, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)

BluetoothSerial SerialBT;

Adafruit_MPU6050 mpu;
Adafruit_Sensor *mpu_temp, *mpu_accel, *mpu_gyro;

float bpm = 0;
float accelero = 0;
float vochtigheid = 0;
uint32_t red = strip.Color(255, 0, 0);
uint32_t green = strip.Color(0, 255, 0);
bool statusNeo = true;
void setup() {
  strip.begin();
  strip.show();
  Serial.begin(115200);
  SerialBT.begin("ESP32test"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
  uint32_t blue = strip.Color(0, 0, 255);
  strip.fill(blue);
  strip.setBrightness(125);
  strip.show();
  pulseSensor.analogInput(PULSE_INPUT);

  pulseSensor.setSerial(Serial);
  pulseSensor.setOutputType(OUTPUT_TYPE);
  pulseSensor.setThreshold(THRESHOLD);
  samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE;
  if (!bme.begin()) {
    Serial.println(F("Could not find a valid BME680 sensor, check wiring!"));
    while (1);
  }
  if (!pulseSensor.begin()) {
    for (;;) {
      // Flash the led to show things didn't work.
      Serial.println("no");
    }
  }
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("Adafruit MPU6050 test!");

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  Serial.println("MPU6050 Found!");
  mpu_temp = mpu.getTemperatureSensor();
  mpu_temp->printSensorDetails();

  mpu_accel = mpu.getAccelerometerSensor();
  mpu_accel->printSensorDetails();

  mpu_gyro = mpu.getGyroSensor();
  mpu_gyro->printSensorDetails();

  // Set up oversampling and filter initialization
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320*C for 150 ms
}

void loop() {
  while (!SerialBT.available()) {
    pulse();
    accel();
    gas();
    if (statusNeo) {
      if (accelero <= 12.0) {
        strip.fill(red,0,8);
        strip.show();
      } else {
        strip.fill(green,0,8);
        strip.show();
      }
      if (bpm <= 110.0) {
        strip.fill(green,8,8);
        strip.show();
      } else {
        strip.fill(red,8,8);
        strip.show();
      }
      if (vochtigheid <= 60.0) {
        strip.fill(green,16,8);
        strip.show();
      } else {
       strip.fill(red,16,8);
        strip.show();
      }
    }else{
      strip.clear();
      strip.show();
    }
  }
  if (SerialBT.available()) {
    String command = SerialBT.readString();
    Serial.println(command);
    if (command == "accelero") {
      bluetoothPrintLine(String(accelero));
    }
    else if (command == "pulse") {
      bluetoothPrintLine(String(bpm));
    }
    else if (command == "gas") {
      bluetoothPrintLine(String(vochtigheid));
    }
    else if (command == "neo"){
      statusNeo = !statusNeo;
      bluetoothPrintLine("switch done");
    }
    else {
      bluetoothPrintLine("0");
    }
  }

  delay(20);
}

void bluetoothPrintLine(String line)
{
  unsigned l = line.length();
  for (int i = 0; i < l; i++)
  {
    if (line[i] != '\0')
      SerialBT.write(byte(line[i]));
  }
  SerialBT.write(10); // \n
}

void accel() {
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  mpu_temp->getEvent(&temp);
  mpu_accel->getEvent(&accel);
  mpu_gyro->getEvent(&gyro);

  float x_int = accel.acceleration.x;
  float y_int = accel.acceleration.y;
  float z_int = accel.acceleration.z;
  accelero = (abs(x_int - 1.0)) + (abs(y_int + 0.28)) + (abs(z_int - 9.80));
}
void pulse() {
  if (pulseSensor.sawNewSample()) {
    if (--samplesUntilReport == (byte) 0) {
      samplesUntilReport = SAMPLES_PER_SERIAL_SAMPLE;
      pulseSensor.outputSample();
      if (pulseSensor.sawStartOfBeat()) {
        pulseSensor.outputBeat();

      }
    }
    bpm = pulseSensor.getBeatsPerMinute();
  }
}

void gas() {
  // Tell BME680 to begin measurement.
  unsigned long endTime = bme.beginReading();
  if (endTime == 0) {
    Serial.println(F("Failed to begin reading :("));
    return;
  }
  Serial.print(F("Reading started at "));
  Serial.print(millis());
  Serial.print(F(" and will finish at "));
  Serial.println(endTime);
  Serial.println(F("You can do other work during BME680 measurement."));
  if (!bme.endReading()) {
    Serial.println(F("Failed to complete reading :("));
    return;
  }
  Serial.print(F("Reading completed at "));
  Serial.println(millis());
  vochtigheid = bme.humidity;
  Serial.println();
}
