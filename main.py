# dependencies: pillow
import pyautogui
import time
import threading


class GameAction(threading.Thread):
    """
    Define a class containing each game action. This class will have all properties
    needed to handle in-game actions
    """
    def __init__(self, keybind, cooldown, icon_path=None, update_icon_loc=True, use_grayscale=True, wait_time=0.2):
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
        self._icon_region = [0, 0, 1366, 768]
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
        self._wait_time = wait_time

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
            time.sleep(self._wait_time)
            failed = self._offCooldown()
            if not failed:
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
        pyautogui.hotkey(*self._keybind)
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
            found_coords = self._imageSearch()
            if found_coords is not None:
                return True
            else:
                return False
        else:
            if self._remainingTime() == 0:
                return True
            else:
                return False

    def _imageSearch(self):
        found_coords = pyautogui.locateOnScreen(self.icon_path, region=self._icon_region, grayscale=self._use_grayscale)
        if self._update_icon_loc:
            # just search where the icon is for efficiency
            # this will break if the hotbar is moved. Don't do that. Fix by restarting script.
            if found_coords is not None:
                self._icon_region = found_coords
        return found_coords


my_action = GameAction(('shift', 'm'), cooldown=7.0, icon_path='image.png')

time.sleep(5)
while True:
    if my_action.offCooldown:
        my_action.sendAction()
    time.sleep(.01)
