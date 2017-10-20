import sys, time, wiringpi

# Initialize pin numbers
redPin = 20
greenPin = 21
bluePin = 16

# Setup wiringpi
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(redPin,1)
wiringpi.softPwmCreate(redPin,0,100)
wiringpi.pinMode(bluePin,1)
wiringpi.softPwmCreate(bluePin,0,100)
wiringpi.pinMode(greenPin,1)
wiringpi.softPwmCreate(greenPin,0,100)

# Turn off all pins
wiringpi.softPwmWrite(redPin,100)
wiringpi.softPwmWrite(greenPin,100)
wiringpi.softPwmWrite(bluePin,100)


def getPins(state):
    '''
    Determins which pins are necessary to show a certain color with an RGB LED
    that describes the state or mood.

    Parameters
    ----------
    state : str
        The state or mood that you wish to describe.

    Returns
    -------
    pins : list[int]
        pins is a list of integers that correspond to the required GPIO pins.

    '''
    
    pins = []
    # Append pin numbers to the list when
    # they correspond to a state
    if state == "happy":
        pins.append(redPin)
        pins.append(greenPin)
    elif state == "sad":
        pins.append(bluePin)
    elif state == "envy":
        pins.append(greenPin)
    elif state == "angry":
        pins.append(redPin)
    elif state == "surprise":
        pins.append(bluePin)
        pins.append(greenPin)
        pins.append(redPin)
    elif state == "scared":
        pins.append(greenPin)
        pins.append(bluePin)
    elif state == "love":
        pins.append(bluePin)
        pins.append(redPin)
    return pins

# Turns off specified pins in a specified amount of time
def turnOff(pins,offTime):
    for brightness in range(0,100):
        for pin in pins:
            wiringpi.softPwmWrite(pin,brightness)
        wiringpi.delay(offTime)

# Turns on specified pins in a specified amount of time
def turnOn(pins,onTime):
    for brightness in reversed(range(0,100)):
            for pin in pins:
                wiringpi.softPwmWrite(pin,brightness)
            wiringpi.delay(onTime)

# Change color of RGB LED to newState from oldState (quickly)
def colorChangeSmall(newState,oldState):
    oldPins = getPins(oldState)
    newPins = getPins(newState)

    turnOff(oldPins,30)
    turnOn(newPins,30)
    

# Change color of RGB LED to newState from oldState (slowly, with blinking)
def colorChangeLarge(newState,oldState):
    oldPins = getPins(oldState)
    newPins = getPins(newState)

    turnOff(oldPins,10)
    for t in range(0,4):
        turnOn(newPins,10)
        turnOff(newPins,10)
    turnOn(newPins,50)
    
if __name__ == "__main__":
    wiringpi.softPwmWrite(redPin,100)
    wiringpi.softPwmWrite(greenPin,100)
    wiringpi.softPwmWrite(bluePin,100)
    print("OFF")
    time.sleep(10)
    colorChangeLarge("sad","angry")
    print("sad")
    time.sleep(5)
    colorChangeLarge("love","sad")
    print("love")
    time.sleep(5)
    colorChangeSmall("happy","love")
    print("happy")
    time.sleep(5)
    colorChangeSmall("envy","happy")
    print("envy")
    time.sleep(5)
    colorChangeLarge("surprise","envy")
    print("surprise")
    time.sleep(5)
    colorChangeSmall("scared","surprise")
    print("scared")
    time.sleep(5)
    colorChangeLarge("angry","scared")
    print("angry")
    
