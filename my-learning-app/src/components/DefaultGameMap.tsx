import React, { useState, useEffect, useCallback } from 'react';
import '../styles/GameMap.css';
import { useWisps, Wisp } from '../hooks/useWisps'; // Import the hook and Wisp type
import BattlePopover from './BattlePopover'; // Import the BattlePopover

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

interface WordData {
  id: string;
  english: string;
  targetWord: string; // Generic field for the selected language's word
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
  const [playerPosition, setPlayerPosition] = useState<Position>({ x: -1, y: -1 });
  const [mapGenerationKey, setMapGenerationKey] = useState<number>(0); // Key to trigger init
  const [treasuresCollected, setTreasuresCollected] = useState<number>(0);
  const [message, setMessage] = useState<string>('Loading...');
  const [isGameActive, setIsGameActive] = useState<boolean>(false); // Flag for when player/map ready
  
  // --- Language Selection State ---
  const [selectedLanguage, setSelectedLanguage] = useState<'salish' | 'italian'>(() => {
    return (localStorage.getItem('selectedLanguage') as 'salish' | 'italian') || 'salish';
  });

  // Persist language selection
  useEffect(() => {
    localStorage.setItem('selectedLanguage', selectedLanguage);
  }, [selectedLanguage]);
  
  // Translation challenge states
  const [isTranslationChallengeActive, setIsTranslationChallengeActive] = useState<boolean>(false);
  const [currentWord, setCurrentWord] = useState<WordData | null>(null); // Use WordData
  const [selectedWord, setSelectedWord] = useState<string>("");
  const [pendingTreasurePosition, setPendingTreasurePosition] = useState<Position | null>(null);

  // Battle Popover States
  const [isBattleActive, setIsBattleActive] = useState<boolean>(false);
  const [encounteredWisp, setEncounteredWisp] = useState<Wisp | null>(null);
  
  // API data states
  const [words, setWords] = useState<WordData[]>([]); // Renamed from salishWords
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // --- Handler for Wisp Encounter (Wrapped in useCallback) --- 
  const handleWispEncounter = useCallback((wisp: Wisp) => {
      console.log(`[DefaultGameMap] Encountered wisp: ${wisp.id}`);
      setEncounteredWisp(wisp);
      setIsBattleActive(true);
      setMessage(`Encountered a ${wisp.rarity} ${wisp.name}!`);
  }, [setMessage, setEncounteredWisp, setIsBattleActive]); // Dependencies: functions that change state

  // --- Use the Wisp Hook --- 
  // Note: updateWispCaptureStatus is now stable IF we wrap it in useCallback inside useWisps
  const { wisps, capturedWisps, updateWispCaptureStatus } = useWisps({
      gameMap,
      playerPosition,
      mapWidth,
      mapHeight,
      isGameActive: playerPosition.x !== -1 && !isBattleActive, 
      onWispEncounter: handleWispEncounter // Pass the memoized handler
  });

  // --- Handler for Battle Popover Close (Wrapped in useCallback) --- 
  const handleBattleClose = useCallback((result: { caught: boolean; treasureMultiplier: number }) => {
      console.log(`[DefaultGameMap] Battle closed. Result:`, result);
      if (encounteredWisp) {
          // updateWispCaptureStatus reference should be stable after we modify useWisps
          updateWispCaptureStatus(encounteredWisp.id, result.caught);
          if (result.caught) {
              setMessage(`Successfully caught the ${encounteredWisp.rarity} ${encounteredWisp.name}! You got ${result.treasureMultiplier}x treasure!`);
              setTreasuresCollected(prev => prev + result.treasureMultiplier);
          } else {
              setMessage(`The ${encounteredWisp.rarity} ${encounteredWisp.name} got away...`);
          }
      }
      setIsBattleActive(false);
      setEncounteredWisp(null);
  }, [encounteredWisp, updateWispCaptureStatus, setMessage, setTreasuresCollected, setIsBattleActive, setEncounteredWisp]);

  // Fetch words from the API based on selected language
  useEffect(() => {
    const fetchWords = async () => { // Renamed from fetchSalishWords
      try {
        setIsLoading(true);
        setError(null);
        setWords([]); // Clear previous words on language change
        
        console.log(`Fetching words for language: ${selectedLanguage}`);
        // Include language in the API call
        const response = await fetch(`${apiBaseUrl}/words?language=${selectedLanguage}`); 
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data && Array.isArray(data.items) && data.items.length > 0) {
          const fetchedWords = data.items.map((item: any) => ({
            id: item.id || String(Math.random()), // Ensure ID exists
            english: item.english,
            // Use the correct field 'target_word' from the API payload
            targetWord: item.target_word || `[Missing Target Word]`, // Changed from item[selectedLanguage]
          })); 
          setWords(fetchedWords); // Use setWords
        } else {
          console.warn('API response not in expected format or empty:', data);
          // Set language-specific fallback words
          if (selectedLanguage === 'italian') {
             setWords([
               { id: 'it1', english: "hello", targetWord: "ciao" },
               { id: 'it2', english: "thank you", targetWord: "grazie" },
               { id: 'it3', english: "water", targetWord: "acqua" },
               { id: 'it4', english: "tree", targetWord: "albero" },
               { id: 'it5', english: "mountain", targetWord: "montagna" }
             ]);
          } else { // Default to Salish fallback
             setWords([
               { id: 'sa1', english: "hello", targetWord: "huy" },
               { id: 'sa2', english: "thank you", targetWord: "huy' ch q'u" },
               { id: 'sa3', english: "water", targetWord: "qʷəlúltxʷ" },
               { id: 'sa4', english: "tree", targetWord: "sc'əɬálqəb" },
               { id: 'sa5', english: "mountain", targetWord: "tukʷtukʷəʔtəd" }
             ]);
          }
        }
      } catch (err) {
        console.error(`Error fetching ${selectedLanguage} words:`, err);
        setError(`Failed to load ${selectedLanguage} language data. Using sample data instead.`);
        // Set language-specific fallback words on error
        if (selectedLanguage === 'italian') {
           setWords([
             { id: 'it1', english: "hello", targetWord: "ciao" },
             { id: 'it2', english: "thank you", targetWord: "grazie" },
             { id: 'it3', english: "water", targetWord: "acqua" },
             { id: 'it4', english: "tree", targetWord: "albero" },
             { id: 'it5', english: "mountain", targetWord: "montagna" }
           ]);
        } else {
           setWords([
             { id: 'sa1', english: "hello", targetWord: "huy" },
             { id: 'sa2', english: "thank you", targetWord: "huy' ch q'u" },
             { id: 'sa3', english: "water", targetWord: "qʷəlúltxʷ" },
             { id: 'sa4', english: "tree", targetWord: "sc'əɬálqəb" },
             { id: 'sa5', english: "mountain", targetWord: "tukʷtukʷəʔtəd" }
           ]);
        }
      } finally {
        // Ensure loading state is turned off after fetch attempt
        setIsLoading(false); 
      }
    };
    
    fetchWords();
  // Add selectedLanguage to dependency array to refetch on change
  }, [apiBaseUrl, selectedLanguage]); 
  
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
    const numWaterBodies = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < numWaterBodies; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 3) + 2;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth) {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.6) {
              map[y][x] = {...cellTypes.water};
            }
          }
        }
      }
    }
    
    // Generate forests
    const numForests = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numForests; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 3) + 2;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.5) {
              map[y][x] = {...cellTypes.tree};
            }
          }
        }
      }
    }
    
    // Generate mountains
    const numMountains = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < numMountains; i++) {
      const centerX = Math.floor(Math.random() * mapWidth);
      const centerY = Math.floor(Math.random() * mapHeight);
      const radius = Math.floor(Math.random() * 2) + 1;
      
      for (let y = centerY - radius; y <= centerY + radius; y++) {
        for (let x = centerX - radius; x <= centerX + radius; x++) {
          if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
            const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
            if (distance <= radius && Math.random() < 0.65) {
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
    if (words.length === 0) { // Use words state
      // Return a generic fallback based on language
      return {
        id: 'fallback',
        english: "word", 
        targetWord: selectedLanguage === 'italian' ? "parola" : "skʷəkʷƛ̓" // Example generic words
      };
    }
    
    const randomIndex = Math.floor(Math.random() * words.length); // Use words state
    return words[randomIndex]; // Use words state
  };
  
  // Handle answer submission for Treasure challenge (Wrapped in useCallback)
  const handleTreasureAnswer = useCallback(() => {
    if (!currentWord || !pendingTreasurePosition) return;
    
    let messageText = '';
    let correct = false;
    if (selectedWord === currentWord.english) {
        correct = true;
        // Use targetWord in the feedback message
        messageText = `Correct! "${currentWord.targetWord}" means "${currentWord.english}". Treasure collected!`; 
        setTreasuresCollected(prev => prev + 1);
    } else {
        // Use targetWord in the feedback message
        messageText = `Incorrect. The correct answer for "${currentWord.targetWord}" was "${currentWord.english}". The treasure vanished...`;
    }
    
    // Replace the treasure with a path regardless of answer
    // Use functional update for setGameMap to avoid dependency on gameMap itself
    setGameMap(prevMap => {
        const newMap = prevMap.map(row => [...row]); // Create deep copy
        if (pendingTreasurePosition) { // Check if position exists
           newMap[pendingTreasurePosition.y][pendingTreasurePosition.x] = {...cellTypes.path};
        }
        return newMap;
    });
    
    setMessage(messageText);
    
    // Reset the challenge
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");
  }, [currentWord, pendingTreasurePosition, selectedWord, setGameMap, setMessage, setTreasuresCollected, setIsTranslationChallengeActive, setCurrentWord, setPendingTreasurePosition, setSelectedWord]);
  
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
          // Update initial message based on language
          setMessage(`Use arrow keys or WASD to move. Learn ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'}!`); 
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
  }, [mapGenerationKey]); // Depend only on mapGenerationKey

  // Handle keyboard movement for Player
  useEffect(() => {
    if (!isGameActive || isTranslationChallengeActive || isBattleActive) return;

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
         if (newX < 0 || newX >= mapWidth || newY < 0 || newY >= mapHeight) {
             setMessage("Can't move off the map!");
            return;
         }

         const targetCell = gameMap[newY]?.[newX];

         if (targetCell?.passable) {
           let interactionOccurred = false; 
           let specialTileMessage = '';

           const targetCellType = targetCell.type;
           if (targetCellType === 'treasure') {
             interactionOccurred = true;
             if (words.length > 0) {
                const word = getRandomTranslationChallenge();
                setCurrentWord(word);
                setIsTranslationChallengeActive(true);
                setPendingTreasurePosition({ x: newX, y: newY });
                specialTileMessage = `Treasure! Translate: "${word.targetWord}"`;
             } else {
                setTreasuresCollected(prev => prev + 1);
                specialTileMessage = 'Treasure collected! (No language data)';
                // Use functional update for setGameMap
                setGameMap(prevMap => {
                    const newMap = prevMap.map(row => [...row]);
                    newMap[newY][newX] = {...cellTypes.path};
                    return newMap;
                });
             }
           } else if (targetCellType === 'cave') {
             interactionOccurred = true;
             specialTileMessage = 'You entered a mysterious cave... 🕳️';
           }
           
           // Update Player Position -> Triggers Wisp Logic hook effect
           setPlayerPosition({ x: newX, y: newY });

           if (interactionOccurred) {
               setMessage(specialTileMessage);
           } else {
                 if (targetCellType === 'path') setMessage('On the path... ⬜');
                 else setMessage('Moving...');
           }

           if (onPositionChange) {
             onPositionChange({ x: newX, y: newY });
           }

         } else if (targetCell) { // Check if targetCell exists before accessing type/symbol
           // Impassable Tile
            setMessage(`Can't move into ${targetCell.type}! ${targetCell.symbol}`);
         }
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  // Dependencies include states controlling the listener and potentially gameMap for checking passability
  }, [isGameActive, isTranslationChallengeActive, isBattleActive, playerPosition, gameMap, onPositionChange, words, setPlayerPosition, setMessage, setCurrentWord, setIsTranslationChallengeActive, setPendingTreasurePosition, setTreasuresCollected, setGameMap, selectedLanguage]); // Added words and selectedLanguage dependency
  
  // Regenerate Map Function (Wrapped in useCallback)
  const handleGenerateNewMap = useCallback(() => {
    console.log("[handleGenerateNewMap] User clicked Generate New Map");
    setIsLoading(true);
    setPlayerPosition({ x: -1, y: -1 });
    setMessage('Generating new map...');
    setIsGameActive(false); 
    setIsBattleActive(false); 
    setEncounteredWisp(null);
    
    // Regenerate map and trigger initialization by updating the key
    setGameMap(() => generateMap()); 
    setMapGenerationKey(prevKey => prevKey + 1); // Increment key
    
    // Reset other states
    setTreasuresCollected(0);
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");
  }, [
    // List all the state setters used
    setIsLoading, setPlayerPosition, setMessage, setIsGameActive, setIsBattleActive, 
    setEncounteredWisp, setGameMap, setTreasuresCollected, setIsTranslationChallengeActive, 
    setCurrentWord, setPendingTreasurePosition, setSelectedWord, setMapGenerationKey
  ]);

  // Helper to get a relevant word for the battle popover (Wrapped in useCallback)
  const getWordForBattle = useCallback((): string => {
      if (words.length > 0) { // Use words state
          const randomWord = words[Math.floor(Math.random() * words.length)]; // Use words state
          return randomWord.english; 
      }
      return "placeholder";
  }, [words]); // Depends on words state

  // --- Dynamic Title based on Language ---
  const gameTitle = selectedLanguage === 'italian' ? 'Italian Language Adventure' : 'Salish Language Adventure';
  const gameSubtitle = `Explore, learn ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'} words, and capture Wisps!`;
  const translatePrompt = `Translate the following ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'} word:`;

  return (
    <div className="sprite-game-container" tabIndex={0} /* Allow div to receive focus for key events */ >
      {isLoading ? (
        <div className="loading-message">{message}</div> // Show current message during load
      ) : (
        <>
          {error && <div className="error-message">{error}</div>}
          
          <div className="game-title-section">
            {/* Dynamic Title and Subtitle */}
            <h2 className="game-title">{gameTitle}</h2>
            <p className="game-subtitle">{gameSubtitle}</p>
            {/* --- Language Selection Dropdown --- */}
            <div className="language-selector">
                <label htmlFor="language-select">Choose Language: </label>
                <select 
                  id="language-select" 
                  value={selectedLanguage} 
                  onChange={(e) => setSelectedLanguage(e.target.value as 'salish' | 'italian')}
                >
                  <option value="salish">Salish</option>
                  <option value="italian">Italian</option>
                </select>
            </div>
          </div>
          
          <div className="game-stats">
            <div>Treasures: {treasuresCollected}</div>
            {playerPosition.x !== -1 && <div>Pos: ({playerPosition.x}, {playerPosition.y})</div>}
            {/* Use words state */}
            <div>Words Loaded ({selectedLanguage}): {words.length}</div> 
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
            {/* Render Wisps - Ensure they render correctly based on state */}
            {wisps.map((wisp: Wisp) => { 
               if (wisp.captured) return null; // Don't render captured wisps on map

               // Calculate position first for logging
               const wispLeft = `${wisp.position.x * 30}px`; // Adjust multiplier if cell size changes
               const wispTop = `${wisp.position.y * 30}px`;  // Adjust multiplier if cell size changes
               // console.log(`[Render Wisp] ID: ${wisp.id}, Pos: (${wisp.position.x}, ${wisp.position.y}), CSS: left=${wispLeft}, top=${wispTop}`);

              return (
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
              {/* Dynamic prompt */}
              <p>{translatePrompt}</p> 
              {/* Use targetWord */}
              <p className="challenge-word">{currentWord.targetWord}</p> 
              
              <select
                className="word-select"
                value={selectedWord}
                onChange={(e) => setSelectedWord(e.target.value)}
              >
                <option value="">Select a translation</option>
                {/* Provide options based on loaded words */}
                {/* Use words state */}
                {words.map((word) => ( 
                  <option key={word.id} value={word.english}>{word.english}</option>
                ))}
              </select>
              
              <button className="submit-button" onClick={handleTreasureAnswer}> {/* Changed handler */}
                Submit Answer
              </button>
            </div>
          )}

          {/* Render Battle Popover Conditionally */} 
          {isBattleActive && encounteredWisp && (
              <BattlePopover
                  wispRarity={encounteredWisp.rarity === 'rare' ? 3 : encounteredWisp.rarity === 'uncommon' ? 2 : 1}
                  onClose={handleBattleClose}
              />
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