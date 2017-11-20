import time
import RPi.GPIO as GPIO

redPin = 20
greenPin = 21
bluePin = 16
largePin = 13
extraPin = 19
allPins = [20,21,16,19,13]

GPIO.setmode(GPIO.BCM) 
GPIO.setup(redPin, GPIO.OUT)
GPIO.setup(bluePin, GPIO.OUT)
GPIO.setup(greenPin, GPIO.OUT)
GPIO.setup(largePin, GPIO.OUT)
GPIO.setup(extraPin, GPIO.OUT)


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

def turnOn(pins):
    turnOff(allPins)
    for pin in pins:
        GPIO.output(pin,1)

def colorChangeLarge(newState):
    pins = getPins(newState)
    pins.append(largePin)
    turnOff(allPins)
    for pin in pins:
        GPIO.output(pin,1)
        

def colorChangeSmall(newState):
    pins = getPins(newState)
    turnOff(allPins)
    for pin in pins:
        GPIO.output(pin,1)

def turnOff(pins):
    for pin in pins:
        GPIO.output(pin,0)
