int buttonPin = D0;
int led1 = D7;
bool doIt = true;

/* IP Address of flask app server */
byte server[] = {192, 168, 1, 25};

TCPClient client;

void setup() {
    Serial.begin(115200);
    pinMode(buttonPin, INPUT);
    pinMode(led1, OUTPUT);
    delay(100);
}

void loop() {
    /* When reed switch not connected, door is open */
    bool doorOpen = digitalRead(buttonPin) == LOW;
    if (doorOpen) {
        if (doIt) {
            if (client.connect(server, 8000)) {
                Serial.println("connected");
                client.println("POST / HTTP/1.1");
                client.println();
                client.flush();
            } else {
                Serial.println("connection failed");
            }
            /* Writes to the LED pin for some
               Blinken-lights-type troubleshooting */
            digitalWrite(led1, HIGH);
            Serial.println("Lighting LED");
            delay(1000);
            doIt = false;
        }
    } else {
        /* Door is closed, reset the application */
        doIt = true;
    }
    digitalWrite(led1, LOW);
}