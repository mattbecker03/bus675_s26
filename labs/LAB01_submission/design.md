# Game Design Document

## Theme / Setting
[What's your theme? Fantasy, sci-fi, horror, action movie, etc.?]
- Dark fantasy landscape filled with demigods, monsters (Elden ring)

## Player's Goal
[What does the player need to accomplish to win?]
- Go through levels and find artifacts, level up, and defeat levels boss

## Locations (4-6)
[List your locations and sketch how they connect]
- 6 locations linear progression
Intro (Limgrave): 1 is the intro level with base level monsters and items, (Stormveil) 2 is an easy boss fight
Intermidate (Caelid): 3 is intermediate level with more advanced items, (Redmane castle) 4 is an intermediate boss
Advanced(Altus Plateau): 5 is harder monsters with even more items to gear up for the final boss, (Volcano Manor) 6 is the final boss

```
                     [ LIMGRAVE ] <-----> [ Round Table Hold ]
                         |
                         v
                     [ STORMVEIL ] <-----> [ LIURNIA ]
                         |
                         v
                     [ CAELID ] <-----> [ Cathedral of Dragon Communion ]
                         |
                         v
                  [ REDMANE CASTLE ]
                         |
                         v
                  [ ALTUS PLATEAU ] <-----> [ Mountain Top of the Giants ]
                         |
                         v
                  [ VOLCANO MANOR ]
```

## Enemies (2-4 types)
- Basic enemies the get harder throughout levels, and bosses which also level up becoming more difficult
Basic enemy 1 (Tree Spirit): 20 health, 0 damage, 0 shield
Intermidate enemy 2 (Knights Calvary): 25 health, 0 damage, 0 shield
Advanced enemy 3 (Magma Wyrm): 30 health, 0 damage, 0 shield

Boss 1 (Margit): 50 health, 4 damage, 10 shield
Boss 2 (Commander O'Neil): 60 health, 20 damage, 25 shield
Boss 3 (Ancient Dragon Lansseax): 100 health, 30 damage, 30 shield

## Win Condition
[How does the player win?]
- Player wins by defeating the final boss

## Lose Condition
[How does the player lose?]
- Player dies if health reaches 0

## Class Hierarchy
[Sketch your class design]

Character
    - Player
    - Basic enemy
        - Boss enemy
        - Regular enemy

```
Character (base class)
├── Player
└── Enemy
    ├── Tree Spirit (weak enemy)
    ├── Knights Calvary (medium enemy)
    ├── Magma Wyrm (hard enemy)
    ├── Margit (easy boss)
    ├── Commander O'Neil (medium boss)
    └── Magma Wyrm (final challenge)

Location
    Level 1, Boss 1
    Level 2, Boss 2
    Level 3, Boss 3

Item (optional)
├── Strength potion (+ 10 strength)
├── Health potion (+20 health, +10 max health)
├── Shield (+ 10 defence)

Game
```

## Additional Notes
[Any other design decisions, ideas, or plans]
