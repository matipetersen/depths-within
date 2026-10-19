# 🎮 Hotkey Quick Reference Card

Print this page and keep it handy while playing!

## ⚡ Most Used (Learn These First)

```
T    Wait / Advance turn
D    Dive (e.g., "d 200" for 200m)
S    Surface
F    Fire torpedo
R    Sonar scan
SU   Supply status
Q    Quit game
```

## 📋 All Hotkeys by Category

### Navigation
```
T  or [Space]  Wait / Advance turn
W              Wait (full name)
D              Dive (needs depth, e.g., "d 250")
S              Surface
```

### Combat
```
F    Fire torpedo at target
A    Aim at target
R    Sonar scan for enemies
```

### Information & Systems
```
ST   Full game status (everything)
C/I  Compartments & systems status
P    Player submarine status
J/L  Journal / Game logs
LO   Lore & crew stories
```

### Crew Management
```
CR   Crew roster
M    Crew morale report
```

### Supplies
```
SU   Supply status
RA   Ration level (strict/reduced/normal/abundant)
     Example: "ra strict"
```

### Espionage
```
SP   Spy network status
ES   Eliminate spy
     Example: "es Klaus"
```

### Encounters
```
EN   Encounter status
RE   Resolve encounter
     Example: "re weapons" or "re flee"
```

### Game
```
H/?   Show this help
Q    Quit game
```

## 💡 Pro Tips

**1. Auto-Tick Magic**
```
✅ "ra strict" → auto-ticks (it's an action)
✅ "su" → no tick (just viewing)
✅ "f" → auto-ticks (combat action)
✅ "m" → no tick (just checking morale)
```

**2. Rapid Gameplay**
```
> r              (sonar scan - no tick)
> st             (status check - no tick)
> f              (fire - AUTO-TICK!)
> [wait]         (next turn - AUTO-TICK!)
> r              (sonar - no tick)
```

**3. Full Commands Still Work**
```
"supplies" works like "su"
"crew_morale" works like "m"
"sonar" works like "r"
"ration_level strict" works like "ra strict"
```

**4. Category Help**
```
> h crew     (show crew-related commands only)
> h combat   (show combat commands only)
> h systems  (show system commands only)
```

## 🎯 Common Scenarios

### "I want to survive"
```
> su                    (check supplies)
> ra reduced            (reduce consumption)
> d 300                 (go deep to hide)
> st                    (check status)
> [wait]                (let time pass)
```

### "I want to attack"
```
> r                     (find targets with sonar)
> f                     (fire torpedo)
> r                     (check if hit)
> s                     (surface to escape)
```

### "Crew is getting stressed"
```
> m                     (check morale)
> cr                    (see who's stressed)
> [maybe take a break]  (advance turns carefully)
```

### "Supplies low"
```
> su                    (check supplies)
> ra strict             (emergency rationing)
> d 400                 (full dive to conserve)
> [surface soon]
```

## 📖 Reading the Display

When you start the game, you'll see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEPTHS WITHIN - Submarine Roguelike
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK REFERENCE:
  [T] Wait      [D] Dive      [S] Surface
  [F] Fire      [R] Sonar     [SU] Supplies
  [CR] Crew     [M] Morale    [H] Help

Type a hotkey or command, then press Enter:
> 
```

## 🔤 Understanding Arguments

Some commands take arguments:

```
"d 300"         → Dive to 300 meters
"ra strict"     → Set ration level to strict
"es Klaus"      → Eliminate spy named Klaus
"re weapons"    → Resolve encounter using weapons
```

Without arguments:
```
"d"             → Shows current depth
"ra"            → Shows current ration level
"re"            → Shows current encounter and options
```

## ⚙️ Settings & Modes

```
Still use full commands for these:
- ascii (toggle ASCII mode)
- color (toggle color mode)
- quit (quit game)
```

## ❌ Troubleshooting

**Q: My command didn't work**
```
A: Check spelling. Hotkeys are case-insensitive.
   "D" = "d" = "dive" - all work!
```

**Q: Why did the game auto-tick when I didn't want it to?**
```
A: Some commands auto-tick (actions):
   fire, dive, surface, ration_level, eliminate_spy, resolve_encounter
   
   Others don't (info):
   supplies, status, help, crew_list, morale
```

**Q: How do I undo an action?**
```
A: You can't - the game saves all actions.
   Manage your depth, supplies, and crew carefully!
```

**Q: Can I customize hotkeys?**
```
A: Not yet! Currently fixed.
   We're planning custom rebinding for next update.
```

## 📊 Cheat Sheet

| What You Want | What You Type | Auto-Ticks? |
|---------------|--------------|------------|
| Check supplies | `su` | ❌ No |
| Dive deep | `d 400` | ✅ Yes |
| Fire torpedo | `f` | ✅ Yes |
| Check morale | `m` | ❌ No |
| Sonar scan | `r` | ❌ No |
| Wait one turn | `t` | ✅ Yes |
| See status | `st` | ❌ No |
| Find crew member | `cr` | ❌ No |
| Ration food | `ra strict` | ✅ Yes |
| Kill a spy | `es Klaus` | ✅ Yes |
| Resolve battle | `re weapons` | ✅ Yes |

## 🎓 Learning Path

**Session 1 (Just Survive):**
```
Learn: T (wait), D (dive), S (surface), SU (supplies)
Practice: Dive deep, manage supplies, surface
```

**Session 2 (Learn Combat):**
```
Learn: F (fire), R (sonar), A (aim)
Practice: Find enemy, fire, dive, escape
```

**Session 3 (Manage Crew):**
```
Learn: CR (crew), M (morale), RA (ration)
Practice: Keep crew happy, manage food
```

**Session 4 (Advanced):**
```
Learn: SP (spy), ES (eliminate), RE (resolve)
Practice: Spy network, encounters, complex tactics
```

## 🚀 Speed Running Tips

**Fastest Hotkey Combos:**
```
1. Evasion:    "d 400" → "r" → "s"         (dive, sonar, surface)
2. Attack:     "r" → "f" → "a" → "f"       (sonar, fire, aim, fire)
3. Rest:       "t" → "t" → "t"             (advance turns quietly)
4. Supply:     "su" → "ra st" → "d 300"    (ration and dive)
```

## 📝 Notes

- Hotkeys are case-insensitive (T = t = [Space] for wait)
- You can always use full command names if you forget the hotkey
- The game auto-saves after each turn
- Losses are permanent (roguelike mode)
- Each playthrough is unique

---

**Version:** Phase 14.5  
**Last Updated:** 2024  
**Status:** Ready to play! 🎮

Print this page and keep it nearby. Soon you'll be playing by muscle memory!
