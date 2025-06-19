
# Note that this probably only works for the default pet tabs...
    # other tabs have a different length/size of the list due to a checkbox about favorites

    # may detect end of list early if there are too many similar pets in a row (ex fynni pet tab)

    # it is recommended to close your inventory windows to prevent false positive dye detections

    # it is recommended to delete the "pets" folder before running as this will remove any leftovers from previous runs

    # it is recommended to point the camera at the sky as best you can to avoid overly noisy backgrounds (if using semi-transparent menus)

    # it is also advisable to move the pet's inventory (and subsequently closing it) to above the center of the screen as many pets give some sort of bonus on summon and other bonuses often appear text in the center

import os
import time
import math
import pyautogui
import pygetwindow
# import PIL directly
from PIL import Image, ImageGrab
# import numpy so we can interact with screenshots by pixel
import numpy as np
# import keyboard so we can use keyboard shortcuts
import keyboard

# create and ensure folders for inventoried pets exist 
from pathlib import Path

# we'll do our own matching so we can compare confidence between templates
import cv2 as cv



# find the mabi window
# for some reason this just looks for the text in the title not an exact match
mabiwindow = pygetwindow.getWindowsWithTitle("Mabinogi")
# so refine it to the exact match (and narrow it down to a single object)
mabiwindow = next(window for window in mabiwindow if window.title == "Mabinogi")

# method to click on mabi window (mabi doesn't register the default click() method well)
def mabiClick(button="left", sleepDuring=0.2):
    pyautogui.mouseDown(button=button)
    time.sleep(sleepDuring) # click is too fast and doesn't always register the release w/o this
    pyautogui.mouseUp(button=button)

# this variable represents the last cached state of the mabi screen (it's a screenshot)
mabiscreen = None
# this method saves the state of the mabi screen (it takes the screenshot)
def mabiScreenGrabState():
    # take a screenshot of the mabi window
    global mabiscreen 
    mabiscreen = pyautogui.screenshot(region=(mabiwindow.left, mabiwindow.top, mabiwindow.width, mabiwindow.height))
    mabiscreen.save("test.png")


def mabiFindPetList():
    aboveList = pyautogui.locate('PetPartner.png', mabiscreen, grayscale=True, confidence=0.9)
    belowList = pyautogui.locate('SortInteraction.png', mabiscreen, grayscale=True, confidence=0.9)

    petHeight = belowList.top - aboveList.top - aboveList.height
    petHeight = int(petHeight/10)

    return {
        "region": (
            mabiwindow.left + int(aboveList.left),
            mabiwindow.top + int(aboveList.top + aboveList.height + petHeight*0.7),
            int(belowList.width),
            int(petHeight*9)
        ),
        "height": petHeight
    }

# takes an Image and returns a new Image that is upscaled and optionally inverted
def upscale(img, scaleFactor, inverted=False):
    cvImg = np.array(img.convert('RGB'))
    cvImg = cvImg[:, :, ::-1].copy()
    if (inverted):
        cvImg = cv.bitwise_not(cvImg)
    cvImg = cv.resize(cvImg, None, fx=scaleFactor, fy=scaleFactor, interpolation=cv.INTER_CUBIC)
    return Image.fromarray(cvImg[:, :, ::-1])

# compares the average color across two images and returns true if they are the same (returns false if either is None)
    # it allows a tolerance of 5 values between each (r,g,b) color component by default
def compareImageColors(imga, imgb, abs_tol=5):
    if (imga == None):
        return False
    if (imgb == None):
        return False
    elif (imga == imgb):
        return True
    else:
        meana = np.mean(np.array(imga.convert('RGB')), axis=(0,1))
        meanb = np.mean(np.array(imgb.convert('RGB')), axis=(0,1))
        for colora, colorb in zip(meana, meanb):
            if not math.isclose(colora, colorb, abs_tol=abs_tol):
                return False
        return True


petInventoryShortcut = "o"
########################################################################
# Beginning of script 
########################################################################

# allows for resuming traversal of the list at a specific pet
startingWith = int(pyautogui.prompt("Resume with pet number? (use 0 for new or last number mentioned if terminated early)"))
print("Beginning with pet in position " + str(startingWith))

# set the mabi window to the foreground
mabiwindow.activate()
time.sleep(0.1)


# open the pets window
keyboard.press_and_release("t")
time.sleep(0.5)
# grab the screen state
mabiScreenGrabState()


# locate the list of pets
petList = mabiFindPetList()
# and position cursor just above it (this allows rel movement later which is safer in case something goes wrong)
pyautogui.moveTo(
    int(petList["region"][0] + petList["region"][2]*0.8), 
    int(petList["region"][1] - petList["height"]*0.5)
)

# move cursor to each of the pet spots
prevPetListScreen = pyautogui.screenshot(region=petList["region"])
petNumber = 0
# do while we have not reached the end of the pet list
while(True):
    time.sleep(0.3)
    print("Detecting pet number " + str(petNumber + 1))
    # move the mouse down a pet
    if (petNumber < 9):
        pyautogui.moveRel(0, petList["height"])
    else:
        pyautogui.scroll(-1)
    time.sleep(0.2)
    # and click
    mabiClick(sleepDuring=0.2)
    time.sleep(0.2)

    petListScreen = pyautogui.screenshot(region=petList["region"])

    # attempt to find prevscreen in the current list and if successful then we have reached the end of scrolling
    try:
        pyautogui.locate(petListScreen, prevPetListScreen, grayscale=True, confidence=0.9)
    except:
        print("Pet Exists")
    else:
        print("End of Pet List Detected")
        # if the prev image and the current image are too similar then we've most likely reached the end of the list
        break

    # record the mouse position before processing the current pet
    listCursorPos = pyautogui.position()
    if (petNumber + 1 >= startingWith):
        ###########################################################################################
        # This is where we process the pet
        print("Summon Pet")
        mabiScreenGrabState()
        summon = pyautogui.locate("Summon.png", mabiscreen, grayscale=True, confidence=0.9)
        pyautogui.moveTo(mabiwindow.left + summon.left + summon.width/2, mabiwindow.top + summon.top + summon.height/2)
        mabiClick()
        time.sleep(0.5)

        # create folders to house the pet/details

        folderPath = Path("../pets/pet" + str(petNumber + 1))
        folderPath.mkdir(parents=True, exist_ok=True)

        # create profile image
        profilePic = Image.new('RGB', (petList["region"][2], petList["height"]*8))
        profilePic.paste(
            # use prevPetListScreen here so it is not cluttered by being selected
            prevPetListScreen.crop((
                0, # left 
                petList["height"]*min(8, petNumber), # top
                petList["region"][2], # right
                petList["height"]*(min(8, petNumber) + 1) # bottom
            )),
            (0,0)
        )
        profilePic.paste(
            pyautogui.screenshot(region=(
                petList["region"][0] + petList["region"][2], # left
                petList["region"][1], # top
                petList["region"][2], # width
                petList["height"]*7 # height
            )),
            (0, petList["height"])
        )
        profilePic.save(folderPath / "profile.png")

        print("Open Inventory")
        keyboard.press_and_release(petInventoryShortcut)
        time.sleep(0.5)
        mabiScreenGrabState()

        # prepare snapshot for opencv
        cvSnapshot = np.array(mabiscreen.convert('RGB'))
        cvSnapshot = cvSnapshot[:, :, ::-1].copy()
        grayscaleSnap = cv.cvtColor(cvSnapshot, cv.COLOR_BGR2GRAY)

        # search image for each dye type
        resultSet = []
        for dyeType in ["ClassicSpiritDye", "Dye", "HairDye", "InstrumentDye", "MagicInstrumentDye", "MetalDye", "WandDye"]:
            # prepare search file for opencv
            dyeTemplate = np.array(Image.open(dyeType + ".png").convert('RGB'))
            dyeTemplate = dyeTemplate[:, :, ::-1].copy()
            grayscaleTemp = cv.cvtColor(dyeTemplate, cv.COLOR_BGR2GRAY)

            # we'll need these in a minute to figure out how wide the image is
            width, height = grayscaleTemp.shape[::-1]

            resGraph = cv.matchTemplate(grayscaleSnap, grayscaleTemp, cv.TM_CCOEFF_NORMED)
            hits = np.where( resGraph >= 0.82 )
            for pt in zip(*hits[::-1]):
                resultSet.append({
                    "type": dyeType,
                    "point": pt,
                    "confidence": resGraph[pt[1]][pt[0]]
                })

        # sort all the found dyes by our confidence
        resultSet.sort(key=lambda item: item['confidence'], reverse=True)
        # and deduplicate it
        foundDyes = []
        for potDye in resultSet:
            pt = potDye["point"]
            # so long as no higher found dye is less than 5 pixels away we will consider it not a duplicate
            if all(map(lambda x: pow(potDye["point"][0] - x["point"][0], 2) + pow(potDye["point"][1] - x["point"][1], 2) > pow(5, 2), foundDyes)):
                foundDyes.append(potDye)

        # grab the current screen state because it's free of tooltips (which might otherwise cover dyes when we go to take a pic of them)
        invSnapshot = [mabiscreen]
        # grab it a few more times in case it was a flashy dye
        for i in range(5):
            mabiScreenGrabState()
            invSnapshot.append(mabiscreen)
        for dye in foundDyes:
            print("Found " + dye["type"] + " at " + str(dye["point"]) + " with confidence " + str(dye["confidence"]))
            cv.rectangle(
                cvSnapshot, 
                dye["point"], 
                (
                    dye["point"][0] + width, 
                    dye["point"][1] + height
                ),
                (0,0,255),
                2
            )

            # mouse over the dye for the tooltip
            pyautogui.moveTo(mabiwindow.left + dye["point"][0] + width/2, mabiwindow.top + dye["point"][1] + height/2)
            time.sleep(0.1)

            # try and grab an image of the tooltip
            mabiScreenGrabState()
            try: 
                desc = pyautogui.locate("ItemDescription.png", mabiscreen, grayscale=True, confidence=0.83)
                nosale = pyautogui.locate("CannotBeSold.png", mabiscreen, grayscale=True, confidence=0.83)

                tooltip = mabiscreen.crop((
                    desc.left, # left
                    desc.top - desc.height*1.4, # top
                    desc.left + nosale.width*1.03, # right
                    nosale.top + nosale.height # bottom
                ))
                upscaleFactor = 2.6
                tooltip = upscale(tooltip, upscaleFactor, True)
                dyepic = Image.new('RGB', (tooltip.width, tooltip.height))
                dyepic.paste(tooltip, (0,0))

                # get the dye from each snapshot picture and hang onto it if it's different from previous
                dyeSnaps = []
                for snap in invSnapshot:
                    prevSnap = dyeSnaps[-1] if (len(dyeSnaps) > 0) else None
                    dyeSnap = upscale(
                        snap.crop((
                            dye["point"][0], # left
                            dye["point"][1], # top
                            dye["point"][0] + width, # right
                            dye["point"][1] + height # bottom
                        )),
                        upscaleFactor
                    )
                    # append the dye snap to the list if it's a different color
                    if not compareImageColors(prevSnap, dyeSnap):
                        dyeSnaps.append(dyeSnap)

                # paste all the dye snapshots onto the tooltip
                for idx, dyeSnap in enumerate(dyeSnaps):
                    dyepic.paste(
                        dyeSnap,
                        (
                            int(tooltip.width - width*upscaleFactor*(len(dyeSnaps) - idx)), # x
                            int(tooltip.height - height*2*upscaleFactor) # y
                        )
                    )

                # create folders to house the dyepics
                typePath = folderPath / dye["type"]
                typePath.mkdir(parents=True, exist_ok=True)
                # dyepic.save(typePath / (str(time.time()*1000) + ".png"))
                dyepic.save(typePath / "x{}y{}.png".format(dye["point"][0], dye["point"][1]))
            except Exception as e:
                print(e)
                print("Unable to find tooltip")

        # save a snapshot of the dyes that were found
        Image.fromarray(cvSnapshot[:, :, ::-1]).save(folderPath / "snapshot.png")


        print("Cancel Summon")
        # we assume that the summon button has become the cancel summon button and not moved to save a little time
        pyautogui.moveTo(mabiwindow.left + summon.left + summon.width/2, mabiwindow.top + summon.top + summon.height/2)
        mabiClick()
        time.sleep(0.5)
        # and now we go back to doom scrolling pets
        ###########################################################################################
    # and move the mouse back to resume scrolling the list of pets
    pyautogui.moveTo(listCursorPos)

    petNumber += 1
    prevPetListScreen = petListScreen
    # safety testing break
    if (petNumber >= 125):
        break
