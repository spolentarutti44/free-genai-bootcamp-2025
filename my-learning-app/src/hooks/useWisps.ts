import { useState, useEffect, useCallback } from 'react';
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
  rarity: string; // Keep as string ('common', 'uncommon', 'rare')
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
  // Changed: Callback now expects the encountered Wisp object
  onWispEncounter: (wisp: Wisp) => void;
}

export const useWisps = ({
  gameMap,
  playerPosition,
  mapWidth,
  mapHeight,
  isGameActive,
  onWispEncounter // Renamed for clarity
}: UseWispsProps) => {

  const [wisps, setWisps] = useState<Wisp[]>([]);
  const [capturedWisps, setCapturedWisps] = useState<Wisp[]>([]); // Still useful for tracking total captured

  // --- Wisp Generation --- 
  const generateWisps = useCallback((currentMap: MapCell[][], playerPos: Position): Wisp[] => {
    // Wrapped generation in useCallback - depends on mapWidth/Height
    // Although unlikely to change, it's safer if these were dynamic.
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
              // Ensure spawn is not ON the player initially
              if ( !(potentialX === playerPos.x && potentialY === playerPos.y) &&
                   currentMap[potentialY]?.[potentialX]?.passable && // Ensure spawn on passable terrain
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
  }, [mapWidth, mapHeight]); // Dependency on map dimensions

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
           console.log("[useWisps Init Effect] Game not active or map not ready. Resetting wisps.");
           setWisps([]);
           setCapturedWisps([]);
      }
  // Re-run ONLY when the map fundamentally changes (signalled by isGameActive potentially toggling)
  // or when the initial valid player position is set.
  }, [gameMap, isGameActive, generateWisps]); // Removed playerPosition dependence here, generation happens on map/activity change


  // Effect for Wisp Movement and Encounter Triggering
  useEffect(() => {
      if (!isGameActive || gameMap.length === 0 || playerPosition.x === -1) {
          return;
      }
      console.log(`[useWisps Effect] Running. Player at: (${playerPosition.x}, ${playerPosition.y})`); // Log entry

      let interactionTriggered = false;
      let currentWisps = wisps; // Read current state

      // --- Encounter Check --- 
      for (const wisp of currentWisps) {
          // Log positions just before the check
          console.log(`[useWisps Check] Comparing Player (${playerPosition.x},${playerPosition.y}) with Wisp ${wisp.id} at (${wisp.position.x},${wisp.position.y}), Captured: ${wisp.captured}`);

          // Check if wisp is not captured and within 2 spaces of the player
          if (!wisp.captured && 
              Math.abs(wisp.position.x - playerPosition.x) <= 1 && 
              Math.abs(wisp.position.y - playerPosition.y) <= 1) 
          {
              console.log(`[useWisps Encounter] MATCH FOUND! Triggering encounter for Wisp ${wisp.id}.`);
              onWispEncounter(wisp); 
              interactionTriggered = true;
              break; 
          }
      }
      
      if (interactionTriggered) {
          return; 
      }

      // --- Wisp Movement (Only if no interaction occurred) --- 
      let wispsMoved = false;
      let counterChanged = false; // Add flag for counter changes
      const movedWisps = currentWisps.map(wisp => {
        if (wisp.captured) return wisp; // Skip captured wisps

        const originalCounter = wisp.moveCounter;
        const newMoveCounter = (wisp.moveCounter + 1);
        let finalPosition = wisp.position; // Initialize final position

        if (newMoveCounter % wisp.speed !== 0) {
          // Not time to move yet
          // Check if counter actually changed before setting flag
          if (newMoveCounter !== originalCounter) {
             counterChanged = true;
          }
          return { ...wisp, moveCounter: newMoveCounter };
        }

        // Time to move
        const currentCounter = 0; // Counter resets after move attempt

        const dx = playerPosition.x - wisp.position.x;
        const dy = playerPosition.y - wisp.position.y;
        if (dx === 0 && dy === 0) return { ...wisp, moveCounter: 0 }; 

        const directions: {x: number, y: number}[] = [];
        if (Math.abs(dx) > Math.abs(dy)) {
          if (dx !== 0) directions.push({ x: -Math.sign(dx), y: 0 });
          if (dy !== 0) directions.push({ x: 0, y: -Math.sign(dy) });
        } else {
          if (dy !== 0) directions.push({ x: 0, y: -Math.sign(dy) });
          if (dx !== 0) directions.push({ x: -Math.sign(dx), y: 0 });
        }
        if(directions.length > 0) { 
           const primaryDir = directions[0];
           if(primaryDir.x !== 0) { 
                directions.push({x: 0, y: 1});
                directions.push({x: 0, y: -1});
           } else { 
                directions.push({x: 1, y: 0});
                directions.push({x: -1, y: 0});
           }
        }
        directions.push({x: 0, y: 0});

        for (const direction of directions) {
          const newX = wisp.position.x + direction.x;
          const newY = wisp.position.y + direction.y;

          if ( newX >= 0 && newX < mapWidth &&
               newY >= 0 && newY < mapHeight &&
               gameMap[newY]?.[newX]?.passable && 
               !(newX === playerPosition.x && newY === playerPosition.y) 
             ) 
          {
            finalPosition = { x: newX, y: newY };
            break; 
          }
        }

        // Check for changes
        if (finalPosition.x !== wisp.position.x || finalPosition.y !== wisp.position.y) {
             wispsMoved = true; // Position changed
        }
        if (currentCounter !== originalCounter) {
            counterChanged = true; // Counter changed (reset in this case)
        }

        return {
          ...wisp,
          position: finalPosition,
          moveCounter: currentCounter
        };
      });

      // Update state only if position OR counter changed
      if (wispsMoved || counterChanged) {
           // console.log(`[useWisps Logic] Updating state. Moved: ${wispsMoved}, Counter Changed: ${counterChanged}`);
           setWisps(movedWisps);
      }
      
  // Dependencies remain the same
  }, [playerPosition, isGameActive, gameMap, mapWidth, mapHeight, onWispEncounter]); 

  // Function to update wisp state after battle (MEMOIZED)
  const updateWispCaptureStatus = useCallback((wispId: string, caught: boolean) => {
      console.log(`[updateWispCaptureStatus Hook] Called for wisp ${wispId}, caught: ${caught}`);
      setWisps(prevWisps => {
          let wispFoundAndChanged = false;
          const updatedWisps = prevWisps.map(w => {
              if (w.id === wispId) {
                   // Only mark as changed if the status is actually different
                  if (w.captured !== caught) { 
                     wispFoundAndChanged = true;
                     if(caught) {
                         console.log(`[updateWispCaptureStatus Hook] Wisp ${wispId} was not captured, now marking as captured.`);
                          // Add to captured list if newly caught
                         console.log(`[updateWispCaptureStatus Hook] Calling setCapturedWisps for wisp ${wispId}`);
                         setCapturedWisps(prevCaptured => {
                             // Avoid duplicates - check if already in list
                             if (!prevCaptured.some(cw => cw.id === wispId)) {
                                console.log(`[updateWispCaptureStatus Hook] Adding wisp ${wispId} to capturedWisps list.`);
                                // Need the actual wisp object here!
                                return [...prevCaptured, { ...w, captured: true }]; // Add the updated wisp
                             }
                             console.log(`[updateWispCaptureStatus Hook] Wisp ${wispId} already in capturedWisps list.`);
                             return prevCaptured; // No change if already present
                         });
                     }
                     return { ...w, captured: caught }; // Return updated wisp for the main 'wisps' array
                  }
              }
              return w;
          });
          // Only return a new array reference if a wisp's status actually changed
          return wispFoundAndChanged ? updatedWisps : prevWisps; 
      });
  }, [setWisps, setCapturedWisps]);

  // Return the states and the update function
  return { wisps, capturedWisps, updateWispCaptureStatus };
}; 