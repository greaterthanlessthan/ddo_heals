# dependencies: pillow
import threading
import time

from pyautogui import locateOnScreen
from ahk import AHK
ahk = AHK()

import keyboard, mouse
from mouse import X, X2, DOWN, UP

class GameAction(threading.Thread):
    """
    Define a class containing each game action. This class will have all properties
    needed to handle in-game actions
    """

    def __init__(self, keybind, cooldown, icon_path=None, update_icon_loc=True, use_grayscale=True, wait_time=1.05):
        # for making threading work
        # set as daemon as nothing important is happening here
        threading.Thread.__init__(self, daemon=True)

        # the image path to the game action's off-cooldown icon. Used for image search
        # to verify action is available
        # leave this None to not use image search
        self.icon_path = icon_path  # example: /folder/myimage.png

        # restrict the region for the image search. These will be dynamically updated for efficiency once
        # the first image search is successful. Disable with update_icon_loc = False
        self._update_icon_loc = update_icon_loc
        self._icon_region = [0, 0, 3440, 1440]
        # image search can further be optimized with grayscale. Default is use grayscale, disable here
        # if issues arrive
        self._use_grayscale = use_grayscale

        # the cooldown in seconds (float) of the game action. Can be used a a complete alternative to
        # image search, or in conjunction to reduce image search calls
        self._cooldown = cooldown  # example: 7.000

        # the in-game keybind to the action, using pyautogui syntax
        # pass a set of the keybinds to this property, e.g. keybind = ('ctrl', 'num0')
        # sand call with pyautogui.hoykey(*keybind)
        self._keybind = keybind

        # when an action is used, game will take some time to get feedback to hotbar icon. If not on cooldown
        # when wait_time is elapsed, assume action failed and wait for _newActionUsed
        self.wait_time = wait_time

        # for cooldown management
        self._last_used = 0.0
        self._newActionUsed = threading.Event()
        self.offCooldown = True

        # start thread when instance is made
        self.start()

    def run(self):
        while True:
            # wait for the action to be used
            self._newActionUsed.wait()
            # verify action was used
            time.sleep(self.wait_time)
            if not self._offCooldown():
                # when action is on cooldown, sleep for remaining time and then clear action used flag
                self.offCooldown = False
                time.sleep(self._remainingTime())
                self._newActionUsed.clear()
                self.offCooldown = True
            else:
                # if not on cooldown, assume action failed
                self._newActionUsed.clear()
                self.offCooldown = True

    def sendAction(self):
        #print("here")
        keyboard.press('ctrl')
        keyboard.press(self._keybind)
        keyboard.release(self._keybind)
        keyboard.release('ctrl')
        self._last_used = time.time()
        self._newActionUsed.set()
        self.offCooldown = False

    def _remainingTime(self):
        if (self._cooldown - (time.time() - self._last_used)) > 0:
            return self._cooldown - (time.time() - self._last_used)
        else:
            return 0

    def _offCooldown(self):
        # search for image if path is set
        if self.icon_path is not None:
            # search for icon
            return True if self.imageSearch() is not None else False
        else:
            return True if self._remainingTime() == 0 else False

    def imageSearch(self):
        found_coords = ahk.image_search(self.icon_path, upper_bound=self._icon_region[:2], lower_bound=self._icon_region[2:], color_variation=100)
        # just search where the icon is for efficiency
        # this will break if the hotbar is moved. Don't do that. Fix by restarting script.
        if self._update_icon_loc and found_coords is not None:
            self._icon_region = found_coords + (found_coords[0]+70, found_coords[1]+70)
        return found_coords


# 79 is numpad 1
heal = GameAction(79, cooldown=5.1, icon_path='heal.PNG')
# 80 is numpad 2
ccw = GameAction(80, cooldown=4.1, icon_path='ccw.PNG')
# 81 is numpad 3
csw = GameAction(81, cooldown=3.6, icon_path='csw.PNG')
# 75 is numpad 4
cmw = GameAction(75, cooldown=3.1, icon_path='cmw.PNG')
# 76 is numpad 5

# 77 is numpad 6
mccw = GameAction(77, cooldown=6.1, icon_path='mccw.PNG')
# 71 is numpad 7
mcsw_sla = GameAction(71, cooldown=9.5, icon_path='mcsw_sla.PNG')
# 72 is numpad 8
mcsw = GameAction(72, cooldown=6.1, icon_path='mcsw.PNG')
# 73 is numpad 9
mcmw = GameAction(73, cooldown=5.0, icon_path='mcmw.PNG')
# 82 is numpad 0
mclw = GameAction(82, cooldown=5.0, icon_path='mclw.PNG')


def massHeal(arg):
    while keyboard.is_pressed(arg.scan_code):
        mass_heal_mouse_event.wait()
        if mccw.offCooldown:
            mccw.sendAction()
            time.sleep(mccw.wait_time)
        elif mcsw_sla.offCooldown:
            mcsw_sla.sendAction()
            time.sleep(mcsw_sla.wait_time)
        elif mcsw.offCooldown:
            mcsw.sendAction()
            time.sleep(mcsw.wait_time)
        elif mcmw.offCooldown:
            mcmw.sendAction()
            time.sleep(mcmw.wait_time)
        elif mclw.offCooldown:
            mclw.sendAction()
            time.sleep(mclw.wait_time)

def spotHeal(arg):
    while keyboard.is_pressed(arg.scan_code):
        spot_heal_mouse_event.wait()
        if heal.offCooldown:
            heal.sendAction()
            time.sleep(heal.wait_time)
        elif ccw.offCooldown:
            ccw.sendAction()
            time.sleep(ccw.wait_time)
        elif csw.offCooldown:
            csw.sendAction()
            time.sleep(csw.wait_time)
        elif cmw.offCooldown:
            cmw.sendAction()
            time.sleep(cmw.wait_time)

if __name__ == "__main__":
    # handle mass heals
    mass_heal_mouse_event = threading.Event()
    keyboard.hook_key('alt', massHeal)
    mouse.on_button(mass_heal_mouse_event.set, buttons=X, types=DOWN)
    mouse.on_button(mass_heal_mouse_event.clear, buttons=X, types=UP)

    # handle spot heals
    spot_heal_mouse_event = threading.Event()
    #keyboard.hook_key('alt', spotHeal)
    mouse.on_button(spot_heal_mouse_event.set, buttons=X2, types=DOWN)
    mouse.on_button(spot_heal_mouse_event.clear, buttons=X2, types=UP)

    keyboard.wait('')
