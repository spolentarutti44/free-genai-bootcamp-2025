import React, { useState, useEffect } from 'react';
import '../styles/GameMap.css';
import { useWisps, Wisp } from '../hooks/useWisps'; // Import the hook and Wisp type

interface MapCell {
  type: string;
  passable: boolean;
  symbol: string;
  color: string;
}

interface Position {
  x: number;
  y: number;
}

interface SalishWord {
  id: string;
  english: string;
  salish: string;
}

interface DefaultGameMapProps {
  onPositionChange?: (position: Position) => void;
  playerProgress?: {[key: string]: boolean};
  apiBaseUrl?: string; // API base URL for fetching words
}

const DefaultGameMap: React.FC<DefaultGameMapProps> = ({ 
  onPositionChange, 
  playerProgress = {},
  apiBaseUrl = 'http://localhost:5001/' // Default API base URL
}) => {
  // Map dimensions
  const mapWidth = 20;
  const mapHeight = 15;
  
  // Map cell types definitions
  const cellTypes: {[key: string]: MapCell} = {
    grass: { type: 'grass', passable: true, symbol: '🌿', color: '#7cfc00' },
    water: { type: 'water', passable: false, symbol: '🌊', color: '#1e90ff' },
    tree: { type: 'tree', passable: false, symbol: '🌲', color: '#228b22' },
    mountain: { type: 'mountain', passable: false, symbol: '⛰️', color: '#a9a9a9' },
    path: { type: 'path', passable: true, symbol: '⬜', color: '#f5deb3' },
    treasure: { type: 'treasure', passable: true, symbol: '💎', color: '#ffd700' },
    house: { type: 'house', passable: false, symbol: '🏠', color: '#cd853f' },
    cave: { type: 'cave', passable: true, symbol: '🕳️', color: '#696969' }
  };
  
  // State variables
  const [gameMap, setGameMap] = useState<MapCell[][]>(() => generateMap());
  const [playerPosition, setPlayerPosition] = useState<Position>({ x: -1, y: -1 }); // Initial invalid position
  const [treasuresCollected, setTreasuresCollected] = useState<number>(0);
  const [message, setMessage] = useState<string>('Loading...');
  const [isGameActive, setIsGameActive] = useState<boolean>(false); // Flag for when player/map ready - ENSURE THIS IS PRESENT
  
  // Translation challenge states
  const [isTranslationChallengeActive, setIsTranslationChallengeActive] = useState<boolean>(false);
  const [currentWord, setCurrentWord] = useState<SalishWord | null>(null);
  const [selectedWord, setSelectedWord] = useState<string>("");
  const [pendingTreasurePosition, setPendingTreasurePosition] = useState<Position | null>(null);
  
  // API data states
  const [salishWords, setSalishWords] = useState<SalishWord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // --- Use the Wisp Hook --- 
  const { wisps, capturedWisps } = useWisps({
      gameMap,
      playerPosition,
      mapWidth,
      mapHeight,
      isGameActive: playerPosition.x !== -1, // Pass the active flag
      onWispInteraction: setMessage // Pass setMessage to the hook for feedback
  });

  // Fetch Salish words from the API on component mount
  useEffect(() => {
    const fetchSalishWords = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await fetch(`${apiBaseUrl}/words`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data && Array.isArray(data.items) && data.items.length > 0) {
          const words = data.items.map((item: any) => ({
            id: item.id || String(Math.random()),
            english: item.english,
            salish: item.salish
          })); 
          setSalishWords(words);
        } else {
          console.warn('API response not in expected format:', data);
          // Set fallback words
           setSalishWords([
            { id: '1', english: "hello", salish: "huy" },
            { id: '2', english: "thank you", salish: "huy' ch q'u" },
            { id: '3', english: "water", salish: "qʷəlúltxʷ" },
            { id: '4', english: "tree", salish: "sc'əɬálqəb" },
            { id: '5', english: "mountain", salish: "tukʷtukʷəʔtəd" }
          ]);
        }
      } catch (err) {
        console.error('Error fetching Salish words:', err);
        setError('Failed to load language data. Using sample data instead.');
        // Set fallback words
         setSalishWords([
            { id: '1', english: "hello", salish: "huy" },
            { id: '2', english: "thank you", salish: "huy' ch q'u" },
            { id: '3', english: "water", salish: "qʷəlúltxʷ" },
            { id: '4', english: "tree", salish: "sc'əɬálqəb" },
            { id: '5', english: "mountain", salish: "tukʷtukʷəʔtəd" }
          ]);
      } finally {
        // setIsLoading(false); // Loading is handled by map/player init now
      }
    };
    
    fetchSalishWords();
  }, [apiBaseUrl]);
  
  // Generate a random map
  function generateMap(): MapCell[][] {
    console.log("[generateMap] Generating new map...");
    const map: MapCell[][] = [];
    
    // Fill with grass initially
    for (let y = 0; y < mapHeight; y++) {
      const row: MapCell[] = [];
      for (let x = 0; x < mapWidth; x++) {
        row.push({...cellTypes.grass});
      }
      map.push(row);
    }
    
    // Generate water bodies
    const numWaterBodies = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numWaterBodies; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 3) + 2;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth) {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.7) {
              map[y][x] = {...cellTypes.water};
            }
          }
        }
      }
    }
    
    // Generate forests
    const numForests = Math.floor(Math.random() * 4) + 2;
    for (let i = 0; i < numForests; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 3) + 2;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.6) {
              map[y][x] = {...cellTypes.tree};
            }
          }
        }
      }
    }
    
    // Generate mountains
    const numMountains = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numMountains; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 2) + 1;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.8) {
              map[y][x] = {...cellTypes.mountain};
            }
          }
        }
      }
    }
    
    // Generate paths
    const numPaths = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numPaths; i++) {
      const startX = Math.floor(Math.random() * mapWidth);
      const startY = Math.floor(Math.random() * mapHeight);
      const endX = Math.floor(Math.random() * mapWidth);
      const endY = Math.floor(Math.random() * mapHeight);
      
      let currentX = startX;
      let currentY = startY;
      
      while (currentX !== endX || currentY !== endY) {
        // Ensure we don't overwrite non-grass cells with paths unless starting point
        if (map[currentY]?.[currentX]?.type === 'grass' || (currentX === startX && currentY === startY)) {
          map[currentY][currentX] = {...cellTypes.path};
        }
        
        if (Math.abs(currentX - endX) > Math.abs(currentY - endY)) {
          currentX += currentX < endX ? 1 : -1;
        } else {
          currentY += currentY < endY ? 1 : -1;
        }
        
        // Avoid going out of bounds during path generation
        currentX = Math.max(0, Math.min(currentX, mapWidth - 1));
        currentY = Math.max(0, Math.min(currentY, mapHeight - 1));
      }
      
      // Mark the end point as path if it's grass
      if (map[endY]?.[endX]?.type === 'grass') {
         map[endY][endX] = {...cellTypes.path};
      }
    }
    
    // Add some treasures
    const numTreasures = Math.floor(Math.random() * 5) + 3;
    for (let i = 0; i < numTreasures; i++) {
      const x = Math.floor(Math.random() * mapWidth);
      const y = Math.floor(Math.random() * mapHeight);
      if (map[y]?.[x]?.passable) {
        map[y][x] = {...cellTypes.treasure};
      }
    }
    
    // Add some houses
    const numHouses = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numHouses; i++) {
      const x = Math.floor(Math.random() * mapWidth);
      const y = Math.floor(Math.random() * mapHeight);
      // Ensure house doesn't overwrite treasure or cave
      if (map[y]?.[x]?.passable && map[y]?.[x]?.type !== 'treasure' && map[y]?.[x]?.type !== 'cave') {
        map[y][x] = {...cellTypes.house};
      }
    }
    
    // Add a cave
    const caveX = Math.floor(Math.random() * mapWidth);
    const caveY = Math.floor(Math.random() * mapHeight);
     // Ensure cave doesn't overwrite treasure or house
    if (map[caveY]?.[caveX]?.passable && map[caveY]?.[caveX]?.type !== 'treasure' && map[caveY]?.[caveX]?.type !== 'house') {
      map[caveY][caveX] = {...cellTypes.cave};
    }
    
    return map;
  };

  // Get a random translation challenge
  const getRandomTranslationChallenge = () => {
    if (salishWords.length === 0) {
      return {
        id: 'fallback',
        english: "hello",
        salish: "huy"
      };
    }
    
    const randomIndex = Math.floor(Math.random() * salishWords.length);
    return salishWords[randomIndex];
  };
  
  // Handle answer submission
  const handleAnswer = () => {
    if (!currentWord || !pendingTreasurePosition) return;
    
    if (selectedWord === currentWord.english) {
      // Correct answer
      setMessage(`Correct! "${currentWord.salish}" means "${currentWord.english}".`);
      setTreasuresCollected(prev => prev + 1);
      
      // Replace the treasure with a path in the map
      const newMap = [...gameMap];
      newMap[pendingTreasurePosition.y][pendingTreasurePosition.x] = {...cellTypes.path};
      setGameMap(newMap);
    } else {
      // Incorrect answer
      setMessage(`Incorrect. The correct answer for "${currentWord.salish}" was "${currentWord.english}".`);
    }
    
    // Reset the challenge
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");
  };
  
  // --- Initialization: Find Player Start & Set Active --- 
  useEffect(() => {
    console.log("[Initialization Effect] Running due to map change...");
    setIsLoading(true); // Ensure loading is true at the start of initialization
    setIsGameActive(false); // Deactivate game logic during init
    setMessage('Finding starting position...'); // Update loading message
    let foundStart = false;

    // Simplified search for any passable tile
    console.log("[Initialization Effect] Searching for passable start tile...");
    for (let y = 0; y < mapHeight; y++) {
      for (let x = 0; x < mapWidth; x++) {
        if (gameMap[y]?.[x]?.passable) {
          console.log(`[Initialization Effect] Found valid player start at (${x}, ${y})`);
          console.log("[Initialization Effect] Setting player position, activating game, disabling loading...");
          setPlayerPosition({ x, y });
          setIsGameActive(true); // ACTIVATE GAME
          setMessage('Use arrow keys or WASD to move. Capture the wisps!'); // Set initial game message
          setIsLoading(false); // <<< CRITICAL: Disable loading state
          foundStart = true;
          break;
        }
      }
      if (foundStart) break;
    }

    if (!foundStart) {
       console.error("[Initialization Effect] No valid starting position found on map!");
       setMessage('Error: Could not find a starting position on the map! Generate a new one?');
       setIsGameActive(false); // Keep game inactive
       setIsLoading(false); // <<< CRITICAL: Also disable loading on error to show message/map
    } else {
        console.log("[Initialization Effect] Initialization complete.");
    }
  }, [gameMap]); // Depend only on gameMap reference

  // Handle keyboard movement for Player
  useEffect(() => {
    // CORRECTED Condition: Only add listener if game is active and not in challenge
    if (!isGameActive || isTranslationChallengeActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      let newX = playerPosition.x;
      let newY = playerPosition.y;
      let intentToMove = false; 
      
      switch (e.key) {
        case 'ArrowUp': case 'w': case 'W': newY--; intentToMove = true; break;
        case 'ArrowDown': case 's': case 'S': newY++; intentToMove = true; break;
        case 'ArrowLeft': case 'a': case 'A': newX--; intentToMove = true; break;
        case 'ArrowRight': case 'd': case 'D': newX++; intentToMove = true; break;
        default: return; 
      }
      
      if (intentToMove) {
        // console.log(`[Player Move] Key '${e.key}'. Intending to move to (${newX}, ${newY}) from (${playerPosition.x}, ${playerPosition.y})`);
         
         if (newX < 0 || newX >= mapWidth || newY < 0 || newY >= mapHeight) {
            // console.log("[Player Move] Blocked: Out of bounds.");
             // Only update message if not showing wisp interaction
             if (!message.includes("captured") && !message.includes("escaped")) {
                setMessage("Can't move off the map!");
             }
            return;
         }

         if (gameMap[newY]?.[newX]?.passable) {
           // console.log(`[Player Move] Target (${newX}, ${newY}) is passable (${gameMap[newY][newX].type}).`);
           let interactionOccurred = false; 
           let specialTileMessage = '';

           const targetCellType = gameMap[newY][newX].type;
           if (targetCellType === 'treasure') {
             interactionOccurred = true;
             if (salishWords.length > 0) {
                const word = getRandomTranslationChallenge();
                setCurrentWord(word);
                setIsTranslationChallengeActive(true);
                setPendingTreasurePosition({ x: newX, y: newY });
                specialTileMessage = `Treasure! Translate: "${word.salish}"`;
                // console.log("[Player Move] Found Treasure - Starting Challenge.");
             } else {
                setTreasuresCollected(prev => prev + 1);
                specialTileMessage = 'Treasure collected! (No language data)';
                const newMap = [...gameMap]; newMap[newY][newX] = {...cellTypes.path};
                setGameMap(newMap);
                // console.log("[Player Move] Found Treasure - Collected (no words).");
             }
           } else if (targetCellType === 'cave') {
             interactionOccurred = true;
             specialTileMessage = 'You entered a mysterious cave... 🕳️';
             // console.log("[Player Move] Entered Cave.");
           }
           
           // Update Player Position -> Triggers Wisp Logic
           // console.log(`[Player Move] Setting player position to (${newX}, ${newY}).`);
           setPlayerPosition({ x: newX, y: newY });

           // Set message *before* wisp logic runs, wisp logic might override
           if (interactionOccurred) {
               setMessage(specialTileMessage);
           } else {
                // Default message only if no special tile and no pending wisp message
                if (!message.includes("captured") && !message.includes("escaped")) {
                     if (targetCellType === 'path') setMessage('On the path... ⬜');
                     else setMessage('Moving...');
                }
           }

           if (onPositionChange) {
             onPositionChange({ x: newX, y: newY });
           }

         } else {
           // Impassable Tile
           // console.log(`[Player Move] Blocked: Target (${newX}, ${newY}) is impassable (${gameMap[newY][newX]?.type}).`);
            // Only update message if not showing wisp interaction
            if (!message.includes("captured") && !message.includes("escaped")) {
                setMessage(`Can't move into ${gameMap[newY][newX].type}! ${gameMap[newY][newX].symbol}`);
            }
         }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  // Re-add listener if game becomes active or challenge ends
  }, [isGameActive, isTranslationChallengeActive, playerPosition, gameMap, onPositionChange, salishWords, message]); 
  
  // Regenerate Map Function
  const handleGenerateNewMap = () => {
    console.log("[handleGenerateNewMap] User clicked Generate New Map");
    setIsLoading(true); // Show loading while regenerating
    setPlayerPosition({ x: -1, y: -1 }); // Invalidate player position
    setMessage('Generating new map...');
    
    // Generate map (triggers initialization useEffect)
    setGameMap(generateMap()); 
    
    // Reset other states
    setTreasuresCollected(0);
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");
    // No need to reset wisps here, init effect handles it
  };

  return (
    <div className="sprite-game-container" tabIndex={0} /* Allow div to receive focus for key events */ >
      {isLoading ? (
        <div className="loading-message">{message}</div> // Show current message during load
      ) : (
        <>
          {error && <div className="error-message">{error}</div>}
          
          <div className="game-title-section">
            <h2 className="game-title">Salish Language Adventure</h2>
            <p className="game-subtitle">Explore, learn Salish words, and capture Wisps!</p>
          </div>
          
          <div className="game-stats">
            <div>Treasures: {treasuresCollected}</div>
            {playerPosition.x !== -1 && <div>Pos: ({playerPosition.x}, {playerPosition.y})</div>}
            <div>Words: {salishWords.length}</div>
            <div>Wisps Captured: {capturedWisps.length}</div>
          </div>
          
          <div className="sprite-map">
            {gameMap.map((row, y) => (
              <div key={y} className="map-row">
                {row.map((cell, x) => (
                  <div 
                    key={`${x}-${y}`} 
                    className={`map-cell ${cell.type}`}
                    style={{ backgroundColor: cell.color, position: 'relative' }}
                  >
                    {playerPosition.x === x && playerPosition.y === y ? 
                      <span className="player">@</span> : 
                      <span>{cell.symbol}</span>
                    }
                  </div>
                ))}
              </div>
            ))}
            {/* Render Wisps - Simplified Positioning */} 
            {wisps.map((wisp: Wisp) => {
               // Calculate position first for logging
               const wispLeft = `${wisp.position.x * 30}px`; // No offset
               const wispTop = `${wisp.position.y * 30}px`; // No offset
               // console.log(`[Render Wisp] ID: ${wisp.id}, Pos: (${wisp.position.x}, ${wisp.position.y}), CSS: left=${wispLeft}, top=${wispTop}`);

              return !wisp.captured && (
                <div key={wisp.id} 
                  className="wisp-entity" 
                  title={`${wisp.rarity} ${wisp.name}`}
                  style={{
                    position: 'absolute',
                    left: wispLeft, // Use calculated value
                    top: wispTop,   // Use calculated value
                    width: '14px',
                    height: '14px',
                    backgroundColor: wisp.color, 
                    borderRadius: '50%', 
                    zIndex: 10, 
                    border: '1px solid rgba(255, 255, 255, 0.5)', 
                    boxShadow: `0 0 5px ${wisp.color}` 
                  }}/>
              )
            })}
          </div>
          
          <div className="game-message">
            {message}
          </div>
          
          {isTranslationChallengeActive && currentWord && (
            <div className="translation-challenge">
              <p>Translate the following Salish word:</p>
              <p className="challenge-word">{currentWord.salish}</p>
              
              <select
                className="word-select"
                value={selectedWord}
                onChange={(e) => setSelectedWord(e.target.value)}
              >
                <option value="">Select a translation</option>
                {salishWords.map((word) => (
                  <option key={word.id} value={word.english}>{word.english}</option>
                ))}
              </select>
              
              <button className="submit-button" onClick={handleAnswer}>
                Submit Answer
              </button>
            </div>
          )}
          
          <div className="game-controls">
            <p>Use arrow keys or WASD to move</p>
            <button onClick={handleGenerateNewMap}>Generate New Map</button>
          </div>
        </>
      )}
    </div>
  );
};

export default DefaultGameMap; 