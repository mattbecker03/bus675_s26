# Reflection: OOP Design Decisions

Write 2-3 paragraphs reflecting on your object-oriented design. Some questions to consider:

- Why did you structure your classes the way you did?
- What inheritance relationships did you use and why?
- What was challenging about managing multiple interacting objects?
- If you had more time, what would you refactor or add?
- How does this experience connect to working with OOP in analytics/ML codebases?

---

[
I partially designed my classes becuase it was the default but internally it made me think why is it formatted like this. For example the main Character class acted as a baseline with states and built in abilites to make newer classes easier to implement. Also the location class made it extremely modular to add on additional enemies, directions, and items.

Again as listed above I had the character and enemies inherit from the Character class along with more specific enemies inheriting from the enemy class to make combat and placing them around the map easier.

It was originally difficult to delete items and enemies after being defeated, along with that the potion interactions and adding to the players max health took some thinking to implement. Finally cycling through the gameplay loop made me think of when to add specific features and more features I'd like to add in the future such as healing during combat and automatically picking up items when discovering a new location. One more feature I'd like to add is picking which specific enemy you'd attack per level if we added multiple in the future.

I might have gone ahead of myself in the previous section but I'd love to add the ability to heal or use potions during combat, upgrade with XP and put levels into specific stats, and pick up or loot enemies when defeated. Along with vastly expanding the map to make it more discovery based.

This experience could help data cleaning and the preprocessing steps. An example I want to try after this experience is using this as building blocks for the Data project in Brets class. Our current project is 4 steps and I'd like to make a base step and be able to modify and try out different preprocessing or model steps to help discover and refine our process step by step. This might also help interpretation and clarify between other classmates when sharing code.

]
