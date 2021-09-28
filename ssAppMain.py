# -*- coding: utf-8 -*-
# Screaming Strike main implementation
# Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
# License: GPL V2.0 (See copying.txt for details)
import dialog
import random
import glob
import os
import threading
import gettext
import platform
import platform_utils.paths
import urllib.request
import sound_lib.sample
import bgtsound
import buildSettings
import collection
import gameField
import gameModes
import gameOptions
import gameResult
import globalVars
import itemVoicePlayer
import scorePostingAdapter
import scoreViewAdapter
import stats
import updateClient
import window
import dialog

platform_utils.paths.prepare_app_data_path(buildSettings.GAME_NAME)
appDataPath = platform_utils.paths.app_data_path(buildSettings.GAME_NAME)
COLLECTION_DATA_FILENAME = appDataPath + "/collection.dat"
STATS_DATA_FILENAME = appDataPath + "/stats.dat"
LAST_VERSION_FILENAME = appDataPath + "/lastVersion.dat"
OPTIONS_FILENAME = appDataPath + "/options.dat"


class ssAppMain(window.SingletonWindow):
    """
    The game's main application class.

    Instantiate this class, call initialize method, then call run method to start the application. Other methods are internally used and should not be called from outside of the class.
    """

    def __init__(self):
        super().__init__()

    def initialize(self):
        """
        Initializes the app. returns True on success or False on failure.

        :rtype: bool
        """
        super().initialize(640, 480, buildSettings.GAME_NAME + " (" + str(buildSettings.GAME_VERSION) + ")")
        globalVars.appMain = self
        # data path patch
        files = glob.glob("data/*.dat")
        if len(files) > 0:
            import shutil
            for elem in files:
                shutil.copyfile(elem, appDataPath + "/" + os.path.basename(elem))
                os.remove(elem)
            # end files
        # end patch required
        # Load sounds
        self.updateChecker = updateClient.Checker()
        self.updateChecker.initialize(buildSettings.GAME_VERSION, buildSettings.UPDATE_SERVER_ADDRESS)
        self.updateChecker.run()
        self.updateDownloader = None  # Not downloading
        self.thread_loadSounds = threading.Thread(target=self.loadSounds)
        self.thread_loadSounds.setDaemon(True)
        self.thread_loadSounds.start()
        self.options = gameOptions.GameOptions()
        self.options.initialize(OPTIONS_FILENAME)
        self.itemVoices = self.getItemVoicesList()
        self.locales = self.getLocalesList()
        self.initTranslation()
        self.music = bgtsound.sound()
        self.musicData = sound_lib.sample.Sample("data/sounds/stream//bg.ogg")
        self.music.load(self.musicData)
        self.music.volume = self.options.bgmVolume
        self.numScreams = len(glob.glob("data/sounds/scream*.ogg"))
        self.collectionStorage = collection.CollectionStorage()
        self.collectionStorage.initialize(self.numScreams, COLLECTION_DATA_FILENAME)
        self.statsStorage = stats.StatsStorage()
        self.statsStorage.initialize(STATS_DATA_FILENAME)
        self.exiting = False  # True only within the onExit trap
        return True

    def initTranslation(self):
        """
        Initializes translation.
        """
        self.translator = gettext.translation("messages", "locale", languages=[self.options.language], fallback=True)
        self.translator.install()

    def resetItemVoice(self):
        """
        Resets the speaker voice settings. This function searches voices and set the first found one as default. If no voice is available, it disables item speaking.
        """
        if len(self.itemVoices) == 0:
            self.options.itemVoice = ""
        else:
            self.options.itemVoice = self.itemVoices[0]

    def getItemVoicesList(self):
        """
        Searches for available voices as item speaker. It returns detected voice names as a list.

        :rtype: list
        """
        lst = []
        for elem in glob.glob("data/voices/*"):
            if os.path.isdir(elem):
                lst.append(os.path.basename(elem))
        return lst

    def getLocalesList(self):
        """
        Searches for available languages. Returns the list of found languages.

        :rtype: list
        """
        lst = []
        for elem in glob.glob("locale/*"):
            if os.path.isdir(elem):
                lst.append(os.path.basename(elem))
        return lst

    def loadSounds(self):
        """Preloads ingame sounds into memory. This is for enhancing performance while playing the game. """
        self.sounds = {}
        files = glob.glob("data/sounds/*.ogg")
        for elem in files:
            self.sounds[os.path.basename(elem)] = sound_lib.sample.Sample(elem)
    # end loadSounds

    def getNumScreams(self):
        """
        Returns the number of auto-detected screams.

        :rtype: int
        """
        return self.numScreams

    def intro(self):
        """Plays the intro sound. It blocks when the sound is playing, then starts the game music. """
        introsound = bgtsound.sound()
        introsound.stream("data/sounds/stream/ssIntro.ogg")
        introsound.play()
        while(introsound.playing):
            self.frameUpdate()
            if self.keyPressed(window.K_RETURN):
                introsound.fadeout(900)
                self.wait(1000)
                break
            # end skipping with enter
        # end while intro is playing
        self.thread_loadSounds.join()
        self.updateChecker.wait()
        self.music.play_looped()
    # end intro

    def createMenu(self, title, default=None):
        """Creates a menu instance and returns it.

        :param title: Menu title.
        :type title: str
        :param default: Default selections.
        :type default: List.
        """
        m = window.menu()
        m.initialize(self, title, default, self.sounds["cursor.ogg"], self.sounds["confirm.ogg"], self.sounds["confirm.ogg"])
        return m

    def appendModeMenus(self, m):
        """
        Appends all game modes to the specified menu.

        :param m: Menu.
        :type m: window.Menu
        """
        m.append(_("Normal mode") + "&1")
        m.append(_("Arcade mode") + "&2")
        m.append(_("Classic mode") + "&3")
        m.append(_("Burden mode") + "&4")

    def mainmenu(self):
        """
        Shows the main menu and returns what was selected as index.

        :rtype: int
        """
        updateProgressTimer = window.Timer()
        m = self.createMenu(_("Main menu. Use your up and down arrows to choose an option, then press enter to confirm"))
        self.appendUpdateMessage(m)
        self.appendModeMenus(m)
        m.append(_("Collection") + " %d/%d &C" % (self.collectionStorage.getUnlocked(), self.collectionStorage.getTotal()))
        m.append(_("View the scoreboard") + "&v")
        m.append(_("Read the manual") + "&r")
        m.append(_("Erase data") + "&E")
        m.append(_("Options") + "&o")
        m.append(_("Quit") + "&Q")

        m.open()
        while(True):
            self.frameUpdate()
            if self.updateDownloader:
                if updateProgressTimer.elapsed >= 300:
                    updateProgressTimer.restart()
                    m.modify(0, self.generateUpdateProgress())
                # end timer
            # end update downloading
            if self.keyPressed(window.K_ESCAPE):
                return False
            selected = m.frameUpdate()
            if selected is not None and selected >= 0:
                return selected
        # end loop
    # end mainmenu

    def appendUpdateMessage(self, m):
        """Appends update-related top message to the specified menu."""
        upresult = self.updateChecker.getLastResult()
        if upresult == updateClient.RET_NOT_SUPPORTED:
            m.append(_("Update checking is disabled in this build of %(gamename)s.") % {"gamename": buildSettings.GAME_NAME})
        elif upresult == updateClient.RET_CONNECTION_ERROR:
            m.append(_("There was an error while retrieving software update information (%(error)s). Please try again later.") %
                     {"error": self.updateChecker.getLastError()})
        elif upresult == updateClient.RET_USING_LATEST:
            m.append(_("You're playing the latest version! When a new update is found, you will be notified here."))
        elif upresult == updateClient.RET_NEW_VERSION_AVAILABLE:
            if not self.updateDownloader:  # Not yet downloaded
                m.append(_("There is a new version of the game! Press enter here to download it."))
            else:
                m.append(self.generateUpdateProgress())
            # end whether downloading
        # end new version is available
        # end appendUpdateMessage

    def generateUpdateProgress(self):
        """Generates a string representing the progress of update downloading.

        :rtype: str
        """
        if self.updateDownloader.isWorking():
            return _("Downloading the new version (%(current)dK/%(total)dK (%(percent)d%%)") % {
                "current": self.updateDownloader.getReceivedSize() / 1024,
                "total": self.updateDownloader.getTotalSize() / 1024,
                "percent": self.updateDownloader.getPercentage()}
        else:
            if self.updateDownloader.hasSucceeded():
                return _("The new version has been downloaded to %(location)s.") % {"location": self.updateDownloader.getLocalName()}
            else:
                return _("Failed to download the new update (%(reason)s). Press enter to retry.") % {"reason": self.updateDownloader.getLastError()}

    def run(self):
        """
        Starts the game. initialize method must be successfully called prior to call this method. It returns when the game is exited.
        """
        if self.intro() is False:
            return
        self.checkChangeLog()
        while(True):
            selected = self.mainmenu()
            if selected is False or selected == 10:
                self.exit()
            if selected == 0:
                if self.updateChecker.getLastResult() == updateClient.RET_NEW_VERSION_AVAILABLE:
                    self.downloadUpdate()
                continue
            # end the update notification area
            if selected == 5:
                self.collectionDialog()
                continue
            if selected == 6:
                self.viewScoreboard()
                continue
            if selected == 7:
                self.displayManual()
                continue
            if selected == 8:
                self.eraseDataDialog()
                continue
            # end erase data
            if selected == 9:
                self.optionsDialog()
                continue
            # end options
            self.play(gameModes.ALL_MODES_STR[selected - 1])
        # end while
    # end run

    def downloadUpdate(self):
        """Sets the download of the new update."""
        if self.updateDownloader and self.updateDownloader.hasSucceeded():
            return
        if self.updateDownloader and self.updateDownloader.isWorking():
            return
        url = buildSettings.UPDATE_PACKAGE_URL[platform.system()]
        local = buildSettings.UPDATE_PACKAGE_LOCAL_NAME[platform.system()]
        if url == "" or local == "":
            self.message(_("This build of %(gamename)s doesn't have download location set.") % {"gamename": buildSettings.GAME_NAME})
            return
        # end download location not set
        self.say(_("Select the folder where you want to download the installer."))
        fld = self.folderSelect(_("Select the folder where you want to download the installer."))
        if not fld:
            return
        bgtsound.playOneShot(self.sounds["confirm.ogg"])
        local = os.path.join(fld, local)
        if os.path.isfile(local):
            if not self.yesno(_("Warning"), local + _(" already exists. Do you want to overwrite?")):
                return
        # end overwriting confirmation
        self.updateDownloader = updateClient.Downloader()
        self.updateDownloader.initialize(url, local, self._downloadComplete)
        self.updateDownloader.run()

    def _downloadComplete(self):
        # Little bit dirty, but unless I do this, the sound object is gc-ed.
        if self.updateDownloader.hasSucceeded():
            self.downloadcomp = bgtsound.sound()
            self.downloadcomp.stream("data/sounds/stream/download.ogg")
            self.downloadcomp.play()
        else:
            self.downloadcomp = bgtsound.sound()
            self.downloadcomp.stream("data/sounds/stream/error.ogg")
            self.downloadcomp.play()

    def play(self, mode):
        """Plays the specified mode.

        :param mode: Mode in string.
        :type mode: str
        """
        self.triggerBeforeStartTips(mode)
        result = self.gamePlay(mode)
        self.resetMusicPitch()
        self.reviewCollection(result)
        self.resultScreen(result)
        if result.score > 0 and result.validateScore() is True:
            self.scorePostDialog(result)

    def triggerBeforeStartTips(self, mode):
        """Shows the mode-specific tip.

        :param mode: Mode.
        :type mode: str
        """
        k = "playcount_" + mode
        if self.statsStorage.get(k) == 0:
            self.statsStorage.increment(k)
            if mode == gameModes.ALL_MODES_STR[0]:
                self.showTip(
                    _("This is the new standard mode of %(gamename)s. Use your left and right arrows to move to the same position as an enemy and spacebar to punch! But remember, they need to be close enough to be hit by your fist. Compared to the previous version, you get bonus points when leveling up. Also, you have chances to get bonuses if you achieve more than 5 consecutive hits!") % {
                        "gamename": buildSettings.GAME_NAME})
            elif mode == gameModes.ALL_MODES_STR[1]:
                self.showTip(
                    _("This is the new arcade mode of %(gamename)s! From the new version, items that fall faster are more likely to be good, and slower ones are more likely to be bad. You can obtain an item by punching it, or destroy it by combining your up arrow when punching. Carefully choose which item to obtain!") % {
                        "gamename": buildSettings.GAME_NAME})
            elif mode == gameModes.ALL_MODES_STR[2]:
                self.showTip(_("This is the old-fashioned game mode! You don't get bonuses based on accuracy, so you can punch, punch, punch punch punch and punch! This mode has a sharper levelup curb, meaning that you can collect screams really fast!"))
            elif mode == gameModes.ALL_MODES_STR[3]:
                self.showTip(_("Welcome to this new and exciting burden mode! In this mode, every item gives you a nasty effect, and each nasty effect boosts points you gain! Guess what? The more you torture yourself, the more point boost you get! Oh, but if you die because of your own torturous act, hahahahahaha, you stupid! Good luck!"))

    def showTip(self, tip):
        """Shows the ingame tip.

        :param tip: Tip to show.
        :type tip: str
        """
        self.message(_("Tip: %s (Press enter to close this tip)") % tip)

    def collectionDialog(self):
        """Shows the collection dialog. Returns when user pressed escape and left the dialog."""
        c = collection.CollectionDialog()
        c.run(self)

    def viewScoreboard(self):
        """Displays the scoreboard view. Returns when user closed the dialog."""
        m = self.createMenu(_("Please select the game mode to view"))
        self.appendModeMenus(m)
        m.append(_("Back"))
        while(True):
            m.open()
            while(True):
                self.frameUpdate()
                r = m.frameUpdate()
                if r is None:
                    continue
                break
            # end loop
            if r == -1 or m.isLast(r):
                break
            # Start retrieving
            adapter = buildSettings.getScoreViewAdapter()
            ret = adapter.get(gameModes.ALL_MODES_STR[r])
            if ret == scoreViewAdapter.RET_UNAVAILABLE:
                self.message(_("This build of %(gamename)s does not support scoreboard viewing.") % {"gamename": buildSettings.GAME_NAME})
                continue
            # end not supported
            m2 = self.createMenu(_("Score table for %(mode)s") % {"mode": gameModes.ALL_MODES_STR[r]})
            for elem in ret:
                m2.append(elem)
            # end append
            m2.append(_("Back"))
            m2.open()
            while(True):
                self.frameUpdate()
                if m2.frameUpdate():
                    break
            # end while score table vie is active
        # end while the mode selection menu is active
    # end viewScoreboard

    def displayManual(self):
        """Shows the manual reading dialog. Returns when user presses escape."""
        fname = "readme_" + self.options.language[0:2] + ".txt"
        if not os.path.isfile(fname):
            self.message(
                _("The manual written in the selected language doesn't seem to exist. If you can write one and contribute, please create %(filename)s and contact the developer.") % {
                    "filename": fname})
            return
        # end not exist
        f = open(fname, "r", encoding="UTF-8")
        m = self.createMenu(
            _("Use your up and down arrows to read the manual. You can navigate to each section by using shortcut keys 1 to 9. Press escape to close"))
        for line in f:
            if line != "\n":
                m.append(line.rstrip())
        # end addition
        f.close()
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if r is None:
                continue
            if r == -1:
                break
            self.say(m.getString(m.getCursorPos()))
        # end loop
    # end displayManual

    def eraseDataDialog(self):
        """Shows the erase data dialog. Returns when user leaves this menu."""
        m = self.createMenu(_("Select the data to erase"), [_("Highscores"), _("Collections"), _("Back")])
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if r is None:
                continue
            if r == -1 or m.isLast(r):
                break
            if not self.keyPressing(window.K_LSHIFT) and not self.keyPressing(window.K_RSHIFT):
                self.say(_("Hold shift and enter to erase."))
                continue
            # end confirmation
            if r == 0:
                self.statsStorage.resetHighscores()
                self.say(_("Your highscores are all reset!"))
                continue
            if r == 1:
                self.collectionStorage.reset()
                self.say(_("Your collections are all reset!"))
                continue
            # end what to reset
        # end while
    # end eraseDataDialog

    def optionsDialog(self):
        """Shows the game options menu. It returns when the menu is closed and all required i/o is finished."""
        backup = gameOptions.GameOptions()
        backup.initialize(self.options)
        m = self.createMenu(
            _("Options Menu, use your up and down arrows to choose an option, left and right arrows to change values, enter to save or escape to discard changes"))
        m.append(_("Background music volume"))
        m.append(_("Left panning limit"))
        m.append(_("Right panning limit."))
        m.append(_("Item announcement voice"))
        m.append(_("Language (restart to apply)"))
        m.open()
        while(True):
            self.frameUpdate()
            ret = m.frameUpdate()
            if self.keyPressed(window.K_LEFT):
                self.optionChange(m.getCursorPos(), -1)
            if self.keyPressed(window.K_RIGHT):
                self.optionChange(m.getCursorPos(), 1)
            if ret is None:
                continue
            if ret == -1:
                self.options = gameOptions.GameOptions()
                self.options.initialize(backup)
                self.say(_("Changes discarded."))
                self.music.volume = self.options.bgmVolume
                return True
            # end if
            if ret >= 0:
                self.say(_("Settings saved"))
                self.options.save(OPTIONS_FILENAME)
                return True

    def optionChange(self, cursor, direction):
        """Changes a specific game option. Used in the optionsMenu method.

        :param cursor: the cursor position in the settings menu
        :type cursor: int
        :param direction: Which arrow key was pressed (0=left / 1=right)
        :type direction: int
        """
        if cursor == 0:  # BGM volume
            if direction == 1 and self.options.bgmVolume == self.options.BGMVOLUME_POSITIVE_BOUNDARY:
                return
            if direction == -1 and self.options.bgmVolume == self.options.BGMVOLUME_NEGATIVE_BOUNDARY:
                return
            if direction == 1:
                self.options.bgmVolume += 2
            if direction == -1:
                self.options.bgmVolume -= 2
            self.music.volume = self.options.bgmVolume
            self.say("%d" % (abs(-30 - self.options.bgmVolume) * 0.5))
            return
        # end bgm volume
        if cursor == 1:  # left panning limit
            if direction == 1 and self.options.leftPanningLimit == self.options.LEFTPANNINGLIMIT_POSITIVE_BOUNDARY:
                return
            if direction == -1 and self.options.leftPanningLimit == self.options.LEFTPANNINGLIMIT_NEGATIVE_BOUNDARY:
                return
            if direction == 1:
                self.options.leftPanningLimit += 5
            if direction == -1:
                self.options.leftPanningLimit -= 5
            s = bgtsound.sound()
            s.load(self.sounds["change.ogg"])
            s.pan = self.options.leftPanningLimit
            s.play()
            return
    # end left panning limit
        if cursor == 2:  # right panning limit
            if direction == 1 and self.options.rightPanningLimit == self.options.RIGHTPANNINGLIMIT_POSITIVE_BOUNDARY:
                return
            if direction == -1 and self.options.rightPanningLimit == self.options.RIGHTPANNINGLIMIT_NEGATIVE_BOUNDARY:
                return
            if direction == 1:
                self.options.rightPanningLimit += 5
            if direction == -1:
                self.options.rightPanningLimit -= 5
            s = bgtsound.sound()
            s.load(self.sounds["change.ogg"])
            s.pan = self.options.rightPanningLimit
            s.play()
            return
        # end left panning limit
        if cursor == 3:  # item voice
            c = 0
            for n in self.itemVoices:  # which are we selecting?
                if self.options.itemVoice == n:
                    break
                c += 1
            # detected the current option
            if direction == 1 and c == len(self.itemVoices) - 1:
                return  # clipping
            if direction == -1 and c == 0:
                return  # clipping
            c += direction
            self.pl = itemVoicePlayer.ItemVoicePlayer()
            if not self.pl.initialize(self.itemVoices[c]):
                self.say(_("%(voice)s cannot be loaded.") % {"voice": self.itemVoices[c]})
                return
            self.say(self.itemVoices[c])
            self.pl.test()
            self.options.itemVoice = self.itemVoices[c]
            return
        # end item voices
        if cursor == 4:  # language
            c = 0
            for n in self.locales:  # which are we selecting?
                if n == self.options.language:
                    break
                c += 1
            # detected the current option
            if direction == 1 and c == len(self.locales) - 1:
                return  # clipping
            if direction == -1 and c == 0:
                return  # clipping
            c += direction
            self.say(self.locales[c])
            self.options.language = self.locales[c]
            return
        # end item voices

    # end optionChange

    def gamePlay(self, mode):
        """
        Starts the gameplay. It returns when the gameplay is finished or exited. If it is finished with a result, returns the result. Otherwise, returns None.

        :rtype: gameResult.GameResult
        """
        self.say(_("%(playmode)s, high score %(highscore)s, start!") % {"playmode": mode, "highscore": self.statsStorage.get("hs_" + mode)})
        field = gameField.GameField()
        if random.randint(0, 4999) == 1:
            self.resetMusicPitch(200)
            field.initialize(3, 20, mode, self.options.itemVoice, True)
        else:
            field.initialize(3, 20, mode, self.options.itemVoice)
        field.setLimits(self.options.leftPanningLimit, self.options.rightPanningLimit)
        while(True):
            self.frameUpdate()
            if self.keyPressed(window.K_ESCAPE):
                field.abort()
                result = gameResult.GameResult()
                result.initialize(field)
                result.aborted = True
                return result
            # end abort
            if self.keyPressed(window.K_TAB):
                self.pauseGame(field)
            if field.frameUpdate() is False:
                break
        # end while
        field.clear()
        self.wait(2000)
        s = bgtsound.sound()
        s.load(self.sounds["dead.ogg"])
        s.pitch = random.randint(70, 130)
        s.play()
        self.wait(800)
        with open("result.txt", mode='a', encoding='utf-8') as f:
            f.write(field.exportLog())
        r = gameResult.GameResult()
        r.initialize(field)
        return r

    def pauseGame(self, field):
        """Pauses the current field.

        :param field: Field to pause.
        :type field: gameField.GameField
        """
        result = gameResult.GameResult()
        result.initialize(field)
        field.setPaused(True)
        m = self.createMenu(_("Game paused"))
        m.append(_("Press enter or escape to resume. Use your up and down arrows to view current stats."))
        m.append(_("Score: %(score)d") % {"score": result.score})
        if result.highscore is not None:
            m.append(_("You are updating your high score. Currently plus %(distance)d (last: %(last)d)") %
                     {"distance": result.highscore - result.previousHighscore, "last": result.previousHighscore})
        m.append(_("Punches: %(punches)d, hits: %(hits)d, accuracy: %(accuracy).2f%%") %
                 {"punches": result.punches, "hits": result.hits, "accuracy": result.hitPercentage})
        m.append(_("This game is currently lasting for %(time)s.") % {"time": result.lastedString})
        m.append(_("Level: %(level)d, player HP: %(hp)d.") % {"level": result.level, "hp": field.player.lives})
        if field.player.autoDestructionRemaining > 0:
            m.append(_("You have %(amount)d stored destructions. You will be protected automatically instead of consuming these.") %
                     {"amount": field.player.autoDestructionRemaining})
        if len(field.player.itemEffects) > 0:
            m.append(_("Active item effects: %(fx)d") % {"fx": len(field.player.itemEffects)})
        for elem in field.player.itemEffects:
            m.append(elem.summarize())
        # end item effects
        m.append(_("-- Last 10 logs --"))
        entries = 10  # default
        index = len(result.log) - 10
        if index < 0:
            index = 0
            entries = len(result.log)
        # end clipping
        for i in range(entries):
            m.append(result.log[index])
            index += 1
        # end log
        m.open()
        while(True):
            self.frameUpdate()
            if m.frameUpdate() is not None:
                break
        # end menu loop
        field.setPaused(False)
    # end pauseGame

    def reviewCollection(self, result):
        """Shows unlocked collections, if any.

        :param result: result to look.
        :type result: gameResult.GameResult
        """
        num = len(result.unlockedCollection)
        if num == 0:
            return
        bgtsound.playOneShot(self.sounds["unlock.ogg"])
        self.wait(500)
        s = _("collection") if num == 1 else _("collections")
        m = self.createMenu(_("Unlocked %(number)d %(collection)s!") % {"number": num, "collection": s})
        for elem in result.unlockedCollection:
            m.append(str(elem))
        # end for
        m.append(_("Close"))
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if r is None:
                continue
            if r == -1 or m.isLast(r):
                break
            bgtsound.playOneShot(self.sounds["scream%s.ogg" % m.getString(m.getCursorPos())])
        # end while
    # end reviewCollection

    def resultScreen(self, result):
        """Shows the game results screen."""
        m = self.createMenu(_("Game result"))
        m.append(_("Final score: %(score)d") % {"score": result.score})
        if result.highscore is not None:
            m.append(_("New high score! Plus %(distance)d (last: %(last)d)") %
                     {"distance": result.highscore - result.previousHighscore, "last": result.previousHighscore})
            bgtsound.playOneShot(self.sounds["highscore.ogg"])
            self.statsStorage.set("hs_" + result.mode, result.highscore)
        # end if highscore
        m.append(_("Punches: %(punches)d, hits: %(hits)d, accuracy: %(accuracy).2f%%") %
                 {"punches": result.punches, "hits": result.hits, "accuracy": result.hitPercentage})
        for elem in result.getModeSpecificResults():
            m.append(elem)
        # end append mode specific results

        m.append(_("This game lasted for %(time)s.") % {"time": result.lastedString})
        m.append(_("You reached level %(level)d.") % {"level": result.level})
        m.append(result.log, shortcut=False)
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if r is not None:
                break
        # end while
    # end resultDialog

    def scorePostDialog(self, result):
        """
        Shows the 'Do you want to post this score?' dialog. The result to post must be specified by the result parameter.

Returns False when the game is closed. Otherwise True.

        :param result: Result to post
        :type result: gameResult.GameResult
        """
        if self.yesno(_("Score posting"), _("Do you want to post this score to the scoreboard?")) is True:  # post
            while(True):
                self.say(_("Please input your name."))
                name = self.input(_("Name entry"), _("Please input your name."))
                if name is None:
                    return
                if name != "":
                    break
            # end blank name checking
            adapter = buildSettings.getScorePostingAdapter()
            ret = adapter.post(name, result)
            if ret == scorePostingAdapter.RET_UNAVAILABLE:
                self.message(_("This build of %(gamename)s does not support score posting. Sorry!") % {"gamename": buildSettings.GAME_NAME})
                return
            # end unavailable
            if ret == scorePostingAdapter.RET_CONNECTION_ERROR:
                self.message(_("There was an error while posting your score (%(error)s). Please try again later.") %
                             {"error": adapter.getLastError()})
                return
            # end connection error
            if ret == scorePostingAdapter.RET_TOO_LOW:
                self.message(_("Your score was posted, but you were not ranked in. Better luck next time!"))
                return
            # end connection error
            self.message(_("Congratulations! Your score has ranked in position %(pos)d! Keep up your great work!") % {"pos": ret})
            return

    def changeMusicPitch_relative(self, p):
        """
        Changes the game music's pitch relatively. Positive values will increase (speedup), and negative values will decrease (slow down). If it hits either of the boundaries (50 lowest, 400 highest), this method does nothing.

        :param p: Amount
        :type p: int
        """
        if self.music.pitch + p > 400:
            return
        self.music.pitch += p
    # end changeMusicPitch_relative

    def resetMusicPitch(self, val=100):
        """
        Resets the music's pitch to default. The pitch change will be processed gradually and this method returns when the music is reverted to the normal speed.
        """
        while(True):
            if abs(self.music.pitch - val) <= 2:
                break
            if self.music.pitch < val:
                self.music.pitch += 2
            else:
                self.music.pitch -= 2
            self.wait(100)
        # end while
        self.music.pitch = val
    # end resetMusicPitch

    def yesno(self, title, top):
        """Shows the yes/ no dialog.

        :param title: Menu title.
        :type title: str
        :param top: Message shown at the top of the menu.
        :type top: str
        :rtype: bool
        """
        m = self.createMenu(title)
        m.append(top)
        m.append(_("Yes") + "&Y")
        m.append(_("No") + "&N")
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if not r:
                continue
            if r > 0:
                break
            if r == -1:
                r = 2
                break
            # end escape
        # end loop
        return True if r == 1 else False

    def message(self, msg):
        """
        Shows a simple message dialog. This method is blocking; it won't return until user dismisses the dialog. While this method is blocking, onExit still works as expected.

        :param msg: Message to show.
        :type msg: str
        """
        self.say(msg)
        while(True):
            self.frameUpdate()
            if True in (
                self.keyPressed(
                    window.K_LEFT), self.keyPressed(
                    window.K_RIGHT), self.keyPressed(
                    window.K_UP), self.keyPressed(
                    window.K_DOWN)):
                self.say(msg)  # Message repeat
            if self.keyPressed(window.K_RETURN):
                break
        # end frame update
        bgtsound.playOneShot(self.sounds["confirm.ogg"])
    # end message

    def onExit(self):
        """Extended onExit callback."""
        exiting = self.exiting
        self.exiting = True
        if not exiting:  # alt+f4 twice will forcefully shut down the app, otherwise, ask player to wait for update download
            if self.updateDownloader:
                self.checkUpdateDownloadFinish()
        self.collectionStorage.save(COLLECTION_DATA_FILENAME)
        self.statsStorage.save(STATS_DATA_FILENAME)
        # Manually free samples here because leaving them for GC causes lots of exceptions when frozen
        for elem in self.sounds.values():
            elem.free()
        return True

    def checkUpdateDownloadFinish(self):
        """Shows a menu where players can wait the update download to finish."""
        if not self.updateDownloader.isWorking():
            return
        m = self.createMenu(_("Update downloading is still in progress"))
        m.append(self.generateUpdateProgress())
        m.append(_("Forcefully shutdown"))
        updateProgressTimer = window.Timer()
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if self.updateDownloader:
                if self.updateDownloader.isWorking() is False:
                    self.message(_("Download job has ended! Press enter to close the application."))
                    break
                # end complete
                if updateProgressTimer.elapsed >= 300:
                    updateProgressTimer.restart()
                    m.modify(0, self.generateUpdateProgress())
                # end timer
            # end update downloading
            if r is None:
                continue
            if r == 1:
                break
            self.say(_("Choose 'Forcefully shutdown' or alt+f4 to abort the download."))
        # end loop
    # end checkUpdateDownloadFinish

    def checkChangeLog(self):
        """Checks if this version is run for the first time. If it is, show the changelog file."""
        if not os.path.isfile(LAST_VERSION_FILENAME):
            self.writeLastVersion()
            self.showChangeLog()
            return
        # end file does not exist
        f = open(LAST_VERSION_FILENAME, "r")
        v = float(f.read())
        f.close()
        self.writeLastVersion()
        if v != buildSettings.GAME_VERSION:
            self.writeLastVersion()
            self.showChangeLog()
        # end if show changelog?
    # end checkChangeLog

    def writeLastVersion(self):
        """Writes the last version number to file."""
        f = open(LAST_VERSION_FILENAME, "w")
        f.write("%.2f" % buildSettings.GAME_VERSION)
        f.close()
    # end writeLastVersion

    def showChangeLog(self):
        """Shows the changelog."""
        fname = "changelog_" + self.options.language[0:2] + ".txt"
        if not os.path.isfile(fname):
            self.message(
                _("The changelog file written in the selected language doesn't seem to exist. If you can write one and contribute, please create %(filename)s and contact the developer.") % {
                    "filename": fname})
            return
        # end not exist
        f = open(fname, "r", encoding="UTF-8")
        m = self.createMenu(_("Changelog"))
        for line in f:
            if line != "\n":
                m.append(line.rstrip())
        # end addition
        f.close()
        m.open()
        while(True):
            self.frameUpdate()
            r = m.frameUpdate()
            if r is None:
                continue
            break
        # end loop
    # end displayManual
# end class ssAppMain
