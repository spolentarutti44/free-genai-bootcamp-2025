import { useState, useEffect } from 'react';
// import { Position, MapCell } from '../types'; // Removed non-existent import

// Define needed interfaces locally for now
interface Position {
  x: number;
  y: number;
}

interface MapCell {
  type: string;
  passable: boolean;
  symbol: string;
  color: string;
}

// Define Wisp interface (can be moved to types.ts later)
export interface Wisp {
  id: string;
  name: string;
  rarity: string;
  color: string;
  speed: number; 
  type: 'wisp';
  position: Position;
  captured: boolean;
  moveCounter: number; 
}

interface UseWispsProps {
  gameMap: MapCell[][];
  playerPosition: Position;
  mapWidth: number;
  mapHeight: number;
  isGameActive: boolean; // To prevent logic running when player pos is invalid (-1,-1)
  onWispInteraction: (message: string) => void; // Callback to set message in parent
}

export const useWisps = ({ 
  gameMap, 
  playerPosition, 
  mapWidth, 
  mapHeight,
  isGameActive, 
  onWispInteraction
}: UseWispsProps) => {

  const [wisps, setWisps] = useState<Wisp[]>([]);
  const [capturedWisps, setCapturedWisps] = useState<Wisp[]>([]);

  // --- Wisp Generation --- 
  // (This needs to be called appropriately, likely within a useEffect)
  const generateWisps = (currentMap: MapCell[][], playerPos: Position): Wisp[] => {
      console.log("[generateWisps Hook] Starting generation for player at:", playerPos);
      const numWisps = Math.floor(Math.random() * 3) + 1; // 1-3 wisps
      const generatedWisps: Wisp[] = [];
      const rarities = ['common', 'uncommon', 'rare'];
      const colors = ['#FF6347', '#1E90FF', '#32CD32', '#EE82EE', '#FFD700']; 
      const maxAttempts = 100;
      
      for (let i = 0; i < numWisps; i++) {
        let pos: Position | null = null; 
        let attempts = 0;
        while (attempts < maxAttempts && pos === null) {
          const potentialX = Math.floor(Math.random() * mapWidth);
          const potentialY = Math.floor(Math.random() * mapHeight);
          if (potentialX >= 0 && potentialX < mapWidth && potentialY >= 0 && potentialY < mapHeight) {
              if ( !(potentialX === playerPos.x && potentialY === playerPos.y) &&
                   !generatedWisps.some(w => w.position.x === potentialX && w.position.y === potentialY)) {
                  pos = { x: potentialX, y: potentialY }; 
              }
          }
          attempts++;
        } 

        if (pos !== null) {
          const rarity = rarities[Math.floor(Math.random() * rarities.length)];
          const color = colors[Math.floor(Math.random() * colors.length)];
          let speed = 3; 
          if (rarity === 'uncommon') speed = 2;
          if (rarity === 'rare') speed = 1;
    
          generatedWisps.push({
            id: `wisp-${Date.now()}-${i}`,
            name: `Wisp ${i + 1}`,
            rarity,
            color,
            speed,
            type: 'wisp',
            position: pos, 
            captured: false,
            moveCounter: Math.floor(Math.random() * speed)
          });
        } else {
          console.warn(`[generateWisps Hook] Could not find valid position for wisp ${i}`);
        }
      }
      console.log("[generateWisps Hook] Finished. Generated:", generatedWisps);
      return generatedWisps;
  }

  // Effect for Initial Wisp Generation & Regeneration on Map Change
  useEffect(() => {
      // Only generate if the game is active (player has a valid position)
      // and the map data is available.
      if (isGameActive && gameMap.length > 0 && playerPosition.x !== -1) {
          console.log("[useWisps Init Effect] Generating initial wisps.");
          const initialWisps = generateWisps(gameMap, playerPosition);
          setWisps(initialWisps);
          setCapturedWisps([]); // Reset captured wisps on new map/generation
      } else {
           // Reset wisps if game becomes inactive (e.g., map regenerating)
           setWisps([]);
           setCapturedWisps([]);
      }
  // Re-run ONLY when the map fundamentally changes (signalled by isGameActive potentially toggling)
  // or when the initial valid player position is set.
  // Using gameMap directly can cause excessive runs if its reference changes often.
  // isGameActive acts as a signal for major game state changes (like map gen). 
  }, [gameMap, isGameActive]); // Consider simplifying deps if map ref is stable


  // Effect for Wisp Movement and Capture Logic
  useEffect(() => {
      // Don't run if player position isn't valid yet or map isn't ready
      if (!isGameActive || gameMap.length === 0) {
          return;
      }
      // console.log(`[useWisps Logic] Running. Player at: (${playerPosition.x}, ${playerPosition.y})`);

      let interactionOccurred = false; 
      let captureAttemptedOnThisPos = false; 

      let currentWisps = [...wisps]; // Use local mutable copy
      const newlyCaptured: Wisp[] = [];

      // --- Capture Check --- 
      currentWisps = currentWisps.map((wisp) => {
        if (!wisp.captured && wisp.position.x === playerPosition.x && wisp.position.y === playerPosition.y) {
            // console.log(`[useWisps Capture] Player landed on Wisp ${wisp.id}! Attempting capture.`);
            captureAttemptedOnThisPos = true; 
            interactionOccurred = true;
            let captureChance = 0.7; 
            if (wisp.rarity === 'common') captureChance = 1.0; 
            if (wisp.rarity === 'uncommon') captureChance = 0.8;
            
            if (Math.random() < captureChance) {
              const capturedWisp = { ...wisp, captured: true };
              newlyCaptured.push(capturedWisp);
              onWispInteraction(`You captured a ${wisp.rarity} ${wisp.name}!`);
              // console.log(`[useWisps Capture] Wisp ${wisp.id} CAPTURED.`);
              return capturedWisp; 
            } else {
              onWispInteraction(`The ${wisp.rarity} ${wisp.name} escaped!`);
              // console.log(`[useWisps Capture] Wisp ${wisp.id} ESCAPED.`);
            }
        }
        return wisp; 
      });

      if (newlyCaptured.length > 0) {
        setCapturedWisps(prev => [...prev, ...newlyCaptured]);
      }

      // --- Wisp Movement --- 
      const movedWisps = currentWisps.map(wisp => {
        if (wisp.captured) return wisp;
        if (captureAttemptedOnThisPos && wisp.position.x === playerPosition.x && wisp.position.y === playerPosition.y) {
            return { ...wisp, moveCounter: 0 }; 
        }

        const newMoveCounter = (wisp.moveCounter + 1);
        if (newMoveCounter % wisp.speed !== 0) {
          return { ...wisp, moveCounter: newMoveCounter }; 
        }

        const dx = playerPosition.x - wisp.position.x;
        const dy = playerPosition.y - wisp.position.y;
        if (dx === 0 && dy === 0) return { ...wisp, moveCounter: 0 };

        const directions: {x: number, y: number}[] = [];
        // Move AWAY from player
        if (Math.abs(dx) > Math.abs(dy)) {
          if (dx !== 0) directions.push({ x: -Math.sign(dx), y: 0 });
          if (dy !== 0) directions.push({ x: 0, y: -Math.sign(dy) });
        } else {
          if (dy !== 0) directions.push({ x: 0, y: -Math.sign(dy) });
          if (dx !== 0) directions.push({ x: -Math.sign(dx), y: 0 });
        }

        let finalPosition = wisp.position;
        for (const direction of directions) {
          if (direction.x === 0 && direction.y === 0) continue;
          const newX = wisp.position.x + direction.x;
          const newY = wisp.position.y + direction.y;

          // Check bounds ONLY (ignore terrain, ignore player pos - they try to flee)
          if ( newX >= 0 && newX < mapWidth && newY >= 0 && newY < mapHeight /*&& 
               !(newX === playerPosition.x && newY === playerPosition.y) */) // Allow fleeing onto player temporarily?
          {
            finalPosition = { x: newX, y: newY };
            break; 
          }
        }

        return {
          ...wisp,
          position: finalPosition,
          moveCounter: 0 
        };
      });

      // Update state only if changes occurred
      if (JSON.stringify(wisps) !== JSON.stringify(movedWisps)) {
           setWisps(movedWisps);
      }
      
  // This effect depends on the player's position and the map structure.
  // isGameActive prevents running when initializing/resetting.
  }, [playerPosition, gameMap, isGameActive, mapWidth, mapHeight, onWispInteraction]); 

  // Return the state needed by the component
  return { wisps, capturedWisps };
}; 