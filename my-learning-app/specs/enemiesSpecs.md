## Wisps

-Add these files to the my-learning-app-src-components
-First basic enemy in the game that should be a wisp which will appear as a smaller colored dot on the map that tries to get to the player

# my-learning-api changes
    - Create backend qdrant for storing enemies
        -Wisps should have a few feature randomly generated
            - Name
            - Rarity 
            - Color
            - Speed
            - Enemy Type(set to wisp)
    - Create backend qdrant for storing Enemy_Catelog
        -this will be a combination of the player and the enemy id with the enemy type ultimately
        -date caught

# my-learning-app changes
    - Create frontend logic to generate random quantity of wisps per map between 0-3 
    - Create agentic layer using langgraph for the frontend for the wisp to move slowly away from the player
    - Use the agentic layer to decide based on the rarity,color and speed how the wisp should react and how hard it should be to capture
    - Wisps should not move outside the boundries of the map and should move like the player one space at a time but opposite direction so it moves towards the player
    - Wisps will randomly start on a space in the game map