# Tower_Game

# Tower Defense

A feature-rich, wave-based tower defense game built with **Python and Pygame**. Strategically place towers, defend against increasingly powerful enemies, manage your in-game economy, and invest in permanent upgrades to survive as many waves as possible.

## Features

Tower Defence Gameplay

* **9 tower types** with different roles, abilities, and combat characteristics.
* **14 enemy types**, ranging from basic and fast enemies to armoured units, regenerating enemies, and powerful bosses.
* **Wave-based progression** with increasing difficulty and rewards.
* **Tower placement system** with position validation to prevent overlapping towers and placement too close to the enemy path.
* **Tower upgrades** for damage, range, fire rate, and special abilities, with up to five upgrade levels per category.
* **Tower health and repairs**, adding another layer of resource management.

### Power-ups

Purchase and activate powerful abilities to turn the tide of battle:

| Power-up      | Effect                                |
| ------------- | ------------------------------------- |
| Air Strike    | Damage enemies across the battlefield |
| Freeze All    | Temporarily immobilise enemies        |
| Double Damage | Increase damage output                |
| Money Boost   | Gain additional economic resources    |
| Repair Lives  | Recover lost lives                    |
| Time Slow     | Slow the pace of combat               |
| Lightning     | Unleash an electrical attack          |
| Nuke          | Deliver a powerful area attack        |


Permanent Progression

Invest in permanent upgrades to improve future runs, including:

* Starting money
* Interest generation
* Tower discounts
* Increased damage, range, and fire rate
* Additional lives
* Wave skipping

Permanent upgrades persist when restarting the game, allowing progression across multiple attempts.


Economy and Scoring

* Earn money and score by defeating enemies.
* Receive rewards for completing waves.
* Earn additional bonuses for reaching milestone waves.
* Gain extra rewards for defeating formidable enemy types.
* Generate passive income through the interest upgrade.
* Manage spending between towers, upgrades, repairs, and power-ups.


Interface and Controls

* Graphical interface with dedicated tower, power-up, and permanent-upgrade shops.
* Real-time displays for money, lives, wave number, and score.
* Visual indicators for selected towers, upgrade levels, and active effects.
* Pause functionality, notifications, and a game-over screen.
* Keyboard shortcuts for selecting towers and activating power-ups.


## Controls

| Key          | Action                                                  |
| ------------ | ------------------------------------------------------- |
| Left Click | Select towers, interact with the shop, and place towers |
| 1-9      | Select a tower type                                     |
| Space      | Start the next wave                                     |
| P          | Pause or resume                                         |
| Z          | Activate Air Strike                                     |
| X          | Activate Freeze All                                     |
| C          | Activate Double Damage                                  |
| V          | Activate Nuke                                           |
| T          | Activate Time Slow                                      |
| R          | Restart after game over                                 |
| Q          | Quit the game                                           |

Power-ups must be purchased before they can be used. Tower types also unlock progressively as you advance through the waves.

## How to Play

1. Select an available tower from the shop.
2. Place it strategically beside the enemy path.
3. Start a wave and let your towers attack approaching enemies.
4. Earn money by defeating enemies and completing waves.
5. Upgrade your towers, purchase power-ups, and repair damaged defences.
6. Invest in permanent upgrades to strengthen future runs.
7. Survive increasingly difficult waves while maximising your score.

The game ends when your lives reach zero. Stronger enemies deal more damage if they escape, making target prioritisation and resource management increasingly important.

## Built With

* **Python** - Core game logic, state management, and gameplay systems.
* **Pygame** - Rendering, input handling, event processing, and the game loop.
* **Object-oriented programming** - Organisation of gameplay entities and systems.
* **Vector-based calculations** - Positioning, distance checks, and combat interactions.

## Project Highlights

This project brings together several interconnected systems:

* Real-time game-loop and event handling.
* Enemy spawning, movement, combat, and wave progression.
* Tower targeting, projectiles, and upgradeable statistics.
* In-game currency, rewards, and economic progression.
* Temporary effects and permanent upgrade systems.
* Dynamic graphical rendering and interactive shop interfaces.



## Future Improvements

Potential extensions include:

* Save files for persistent progression between sessions.
* Additional maps, paths, and difficulty settings.
* Improved enemy pathfinding and tower targeting options.
* Balancing tools and gameplay statistics.
* Sound effects, music, and additional visual effects.
* Automated tests for core gameplay and economy systems.
