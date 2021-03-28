#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance, force

;# some logic is in for game_icon = false but it breaks without an icon

class GameAction{	
	;# how large the square of the hotbar icon is.
	static icon_dim := 50
	;# how long the game takes to animate an action or how long the global cooldown is
	static game_animation_time := 1050
	;# delay. Depends on network latency, screen refresh rate, etc.
	static game_delay := 100
	
	;# for troubleshooting purposes
	static enable_msgbox := false
	
	__New(aIcon, aCooldown, aKey, aAlt:=false, aSub:=false, aBlocks:=1050)
	{
		;# instantiate this object
		this.game_icon := aIcon
		this.cooldown := aCooldown
		this.keybind := aKey
		
		;# search entire screen for 
		this.icon_region_upper_x := 0
		this.icon_region_upper_y := 0
		this.icon_region_lower_x := A_ScreenWidth
		this.icon_region_lower_y := A_ScreenHeight
		
		this.alt_action := aAlt
		this.subsequent_action := aSub
		this.off_cooldown := true
		
		;# how long to prevent other actions
		this.block_time := aBlocks
		
		;# for storing tickcount
		this.last_used_time := 0
	}
	
	checkSuccess()
	{
		;# short pause for screen delay, network delay, etc..
		sleep this.game_delay
		
		;# if we found the icon, global cooldown was not starting, thus the action failed
		;# if we don't have an icon, we can only assume the action succeeded
		if (this.game_icon != false and this.searchForIcon())
		{
			if (this.enable_msgbox)
			{
				MsgBox the action failed
			}
			this.off_cooldown := true
			return false
		}
		else
		{
			;# the action looks like it was successful, so set the flags
			this.off_cooldown := false
			this.last_used_time := A_TickCount
			
			;# block sending hotkeys during the global cooldown or animation time
			sleep this.block_time
			return true
		}
		
	}
	
	timeHasElapsed()
	{
		time_elapsed := A_TickCount - this.last_used_time
		if (time_elapsed > this.cooldown)
		{
			this.off_cooldown := true
			return true
		}
		else
		{
			this.off_cooldown := false
			return false
		}
	}
	
	sendAction()
	{
		;# check if cooldown has elapsed
		
		;# send the action if it is off cooldown, or check if it's available
		if ((this.timeHasElapsed() and this.game_icon = false) or this.searchForIcon())
		{
			if (this.enable_msgbox)
			{
				MsgBox % "sending " . this.game_icon
			}
			
			SendInput % this.keybind
			
			;# check if action went on cooldown
			this.checkSuccess()
			
			;# send the subsequent action if this action succeeded (if it went on cooldown (future: or if success was returned by an alternate action)
			if (this.subsequent_action != false and not this.off_cooldown)
			{
				if (this.enable_msgbox)
				{
					MsgBox % "now trying subsequent action for " . this.game_icon
				}
				
				this.subsequent_action.sendAction()
			}
		}
		
		;# send the alternate action if this is on cooldown. Receiving feedback for if the was successful would get complicated (maybe? look into)
		else if (this.alt_action != false)
		{
			if (this.enable_msgbox)
			{
				MsgBox % "now trying alt action for " . this.game_icon
			}
			
			this.alt_action.sendAction()
			
			;# send the subsequent action if this action succeeded (if it went on cooldown (future: or if success was returned by an alternate action)
			if (this.subsequent_action != false and not this.alt_action.off_cooldown)
			{
				if (this.enable_msgbox)
				{
					MsgBox % "now trying subsequent action for " . this.game_icon
				}
				
				this.subsequent_action.sendAction()
			}
		}
	}
	searchForIcon()
	{
		if (this.game_icon = false)
		{
			return false
		}
		;# does not take %this.var%?
		image := this.game_icon
		ImageSearch, FoundX, FoundY, this.icon_region_upper_x, this.icon_region_upper_y, this.icon_region_lower_x, this.icon_region_lower_y, *4 %A_ScriptDir%\%image%
		if (ErrorLevel = 2)
		{
			if (this.enable_msgbox){
				MsgBox Could not conduct the search.
				IfNotExist, %A_ScriptDir%\%image%
					MsgBox Error: Your file either doesn't exist or isn't in this location.
			}
		}
		
		if (ErrorLevel = 0)
		{
			if (this.enable_msgbox)
			{
				MsgBox % "The icon was found at " . FoundX . "x" . FoundY . " with search region " . this.icon_region_upper_x . "x" . this.icon_region_upper_y . " x " . this.icon_region_lower_x . "x" . this.icon_region_lower_y	
			}
			;# shrink the dimensions for efficiency. Hotbars are expected to stay in place
			this.icon_region_upper_x := FoundX
			this.icon_region_upper_y := FoundY
			this.icon_region_lower_x := FoundX + this.icon_dim
			this.icon_region_lower_y := FoundY + this.icon_dim
			return true
		}
		;# did not find icon if fell through previous if statement
		return false
	}
}


;# define spot heals: icon, cooldown, in-game keybind, try if on cooldown, subsequent action, instant or not (optional, default true so not included here)
global cmw := new GameAction("cmw.png", 3100, "^{Numpad4}") 
global csw := new GameAction("csw.png", 3100, "^{Numpad3}", cmw)
global ccw := new GameAction("ccw.png", 4100, "^{Numpad2}", csw)
global heal := new GameAction("heal.png", 5100, "^{Numpad1}", ccw)

Hotkey, !XButton1, SpotHealLabel
Hotkey, +!XButton1, SpotHealLabel

;# define mass heals
global mclw := new GameAction("mclw.png", 5100, "^{Numpad0}") 
global mcmw := new GameAction("mcmw.png", 5100, "^{Numpad9}", mclw) 
global mcsw := new GameAction("mcsw.png", 6100, "^{Numpad8}", mcmw)
global mcsw_sla := new GameAction("mcsw_sla.png", 9100, "^{Numpad7}", mcsw)
global mccw := new GameAction("mccw.png", 6100, "^{Numpad6}", mcsw_sla)

Hotkey, !XButton2, MassHealLabel
Hotkey, +!XButton2, MassHealLabel

;# define special heals
global break_ench := new GameAction("break_ench.png", 5100, "!{Numpad3}")
global remove_curse_then_heal := new GameAction("remove_curse.png", 4100, "!{Numpad1}", break_ench, heal)

Hotkey, ^XButton1, SpecialHealLabel
Hotkey, +^XButton1, SpecialHealLabel

;# define raises
global raise := new GameAction("raise.png", 9100, "!{Numpad0}")
global res := new GameAction("res.png", 11100, "!{Numpad9}", raise)
global true_res := new GameAction("true_res.png", 13100, "!{Numpad8}", res)

Hotkey, ^!XButton1, ResLabel
Hotkey, +^!XButton1, ResLabel

;# define boosts
global reaper := new GameAction(false, 40100, "^{NumpadDiv}", false, false, 100)
global aureon := new GameAction("aureon.png", 600100, "^{NumpadSub}", reaper)
global ascend := new GameAction("ascend.png", 300100, "^{NumpadMult}", aureon)

Hotkey, ^MButton, DCBoostLabel

;# define dodges
global meld := new GameAction("meld.png", 120100, "{NumpadMult}")
global illusionist := new GameAction("illusion.png", 180100, "{NumpadDiv}", meld)

Hotkey, !MButton, DodgeLabel
Hotkey, +!MButton, DodgeLabel

;##############################################################################################
;# End of definitions, begin labels
Return
; Spot Heals -- Heal -> CCW -> CSW -> CMW
SpotHealLabel:
heal.sendAction()
Return

; Mass Heals -- MCCW -> MCSW-SLA -> MCSW -> MCMW -> MCLW
MassHealLabel:
mccw.sendAction()
Return

; Special Heals -- Heal then remove curse
SpecialHealLabel:
remove_curse_then_heal.sendAction()
Return

; Raise -- True res, res, then raise
ResLabel:
true_res.sendAction()
Return

; DC boosts - Ascend, Aureon, then reaper
DCBoostLabel:
ascend.sendAction()
Return

DodgeLabel:
illusionist.sendAction()
Return
