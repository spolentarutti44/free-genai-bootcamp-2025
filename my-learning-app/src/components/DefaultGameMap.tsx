import React, { useState, useEffect, useCallback } from 'react';
import '../styles/GameMap.css';
import { useWisps, Wisp } from '../hooks/useWisps'; // Import the hook and Wisp type
import BattlePopover from './BattlePopover'; // Import the BattlePopover
// Import the new hook and the WordData interface
import { useWords, WordData } from '../hooks/useWords';
// Import the map generator utility and MapCell interface
import { generateMap, MapCell, cellTypes } from '../utils/mapGenerator'; // Added cellTypes

interface Position {
  x: number;
  y: number;
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
  
  // State variables
  const [initialMapData, setInitialMapData] = useState(() => {
    console.log("[Initial State] Generating initial map data...");
    const { map, treasureCount } = generateMap(mapWidth, mapHeight);
    console.log(`[Initial State] Initial map generated with ${treasureCount} treasures.`);
    return { map, treasureCount };
  });
  const [gameMap, setGameMap] = useState<MapCell[][]>(initialMapData.map);
  const [totalTreasuresOnMap, setTotalTreasuresOnMap] = useState<number>(initialMapData.treasureCount);
  const [playerPosition, setPlayerPosition] = useState<Position>({ x: -1, y: -1 });
  const [mapGenerationKey, setMapGenerationKey] = useState<number>(0); // Key to trigger init
  const [treasuresCollectedThisMap, setTreasuresCollectedThisMap] = useState<number>(0); // Renamed state
  const [totalScore, setTotalScore] = useState<number>(0); // New state for persistent score
  const [message, setMessage] = useState<string>('Initializing...'); // Updated initial message
  const [isGameActive, setIsGameActive] = useState<boolean>(false); // Flag for when player/map ready
  
  // --- Language Selection State ---
  const [selectedLanguage, setSelectedLanguage] = useState<'salish' | 'italian'>(() => {
    return (localStorage.getItem('selectedLanguage') as 'salish' | 'italian') || 'salish';
  });

  // Persist language selection
  useEffect(() => {
    localStorage.setItem('selectedLanguage', selectedLanguage);
  }, [selectedLanguage]);
  
  // --- Use the new words hook --- 
  const { words, isLoading: isLoadingWords, error: wordsError } = useWords({ apiBaseUrl, selectedLanguage });
  // Determine overall loading state: true if words are loading OR player hasn't been placed
  const isLoading = isLoadingWords || playerPosition.x === -1;

  // Translation challenge states
  const [isTranslationChallengeActive, setIsTranslationChallengeActive] = useState<boolean>(false);
  const [currentWord, setCurrentWord] = useState<WordData | null>(null); // Use WordData
  const [selectedWord, setSelectedWord] = useState<string>("");
  const [pendingTreasurePosition, setPendingTreasurePosition] = useState<Position | null>(null);
  // --- Add state for the translation options ---
  const [translationOptions, setTranslationOptions] = useState<string[]>([]);

  // Battle Popover States
  const [isBattleActive, setIsBattleActive] = useState<boolean>(false);
  const [encounteredWisp, setEncounteredWisp] = useState<Wisp | null>(null);
  
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
      isGameActive: playerPosition.x !== -1 && !isBattleActive && !isLoading, // Also check overall isLoading
      onWispEncounter: handleWispEncounter // Pass the memoized handler
  });

  // --- Handler for Battle Popover Close (Wrapped in useCallback) --- 
  const handleBattleClose = useCallback((result: { caught: boolean; treasureMultiplier: number }) => {
      console.log(`[DefaultGameMap] Battle closed. Result:`, result);
      if (encounteredWisp) {
          // updateWispCaptureStatus reference should be stable after we modify useWisps
          updateWispCaptureStatus(encounteredWisp.id, result.caught);
          if (result.caught) {
              // Update total score based on wisp capture multiplier
              const scoreGained = result.treasureMultiplier; 
              setMessage(`Successfully caught the ${encounteredWisp.rarity} ${encounteredWisp.name}! Score +${scoreGained}!`);
              setTotalScore(prev => prev + scoreGained); // Add multiplier to total score
          } else {
              setMessage(`The ${encounteredWisp.rarity} ${encounteredWisp.name} got away...`);
          }
      }
      setIsBattleActive(false);
      setEncounteredWisp(null);
  }, [encounteredWisp, updateWispCaptureStatus, setMessage, setTotalScore, setIsBattleActive, setEncounteredWisp]); // Added setTotalScore

  // Get a random translation challenge
  const getRandomTranslationChallenge = () => {
    if (words.length === 0) { // Use words state from hook
      // Return a generic fallback based on language
      return {
        id: 'fallback',
        english: "word", 
        targetWord: selectedLanguage === 'italian' ? "parola" : "skʷəkʷƛ̓" // Example generic words
      };
    }
    
    const randomIndex = Math.floor(Math.random() * words.length); // Use words state from hook
    return words[randomIndex]; // Use words state from hook
  };
  
  // Function to trigger map regeneration (used by button and auto-reset)
  const regenerateMap = useCallback((preserveScore: boolean) => {
    console.log("[regenerateMap] Triggered. Preserve score:", preserveScore);
    setMessage('Generating new map...');
    setIsGameActive(false);
    setIsBattleActive(false);
    setEncounteredWisp(null);
    setPlayerPosition({ x: -1, y: -1 }); // Reset player position to trigger re-init

    // Generate new map data
    const { map: newMap, treasureCount: newTreasureCount } = generateMap(mapWidth, mapHeight);
    setGameMap(newMap);
    setTotalTreasuresOnMap(newTreasureCount);
    console.log(`[regenerateMap] New map generated with ${newTreasureCount} treasures.`);

    // Reset map-specific states
    setTreasuresCollectedThisMap(0);
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");

    if (!preserveScore) {
      console.log("[regenerateMap] Resetting total score.");
      setTotalScore(0); // Reset total score only if not preserving
    } else {
       console.log("[regenerateMap] Preserving total score:", totalScore); // Log score being preserved
    }


    setMapGenerationKey(prevKey => prevKey + 1); // Increment key to trigger initialization effect
  }, [ // Dependencies: All state setters used within
      setMessage, setIsGameActive, setIsBattleActive, setEncounteredWisp, 
      setPlayerPosition, setGameMap, setTotalTreasuresOnMap, 
      setTreasuresCollectedThisMap, setIsTranslationChallengeActive, 
      setCurrentWord, setPendingTreasurePosition, setSelectedWord, 
      setMapGenerationKey, setTotalScore, totalScore // Include totalScore in deps for logging
  ]);

  // Handle answer submission for Treasure challenge (Wrapped in useCallback)
  const handleTreasureAnswer = useCallback(() => {
    if (!currentWord || !pendingTreasurePosition) return;
    
    let messageText = '';
    let correct = false;
    if (selectedWord === currentWord.english) {
        correct = true;
        messageText = `Correct! "${currentWord.targetWord}" means "${currentWord.english}". Score +1!`; 
        // Update total score and treasures collected on this map
        setTotalScore(prev => prev + 1);
        setTreasuresCollectedThisMap(prev => prev + 1); // This will trigger the useEffect below
    } else {
        messageText = `Incorrect. The correct answer for "${currentWord.targetWord}" was "${currentWord.english}". The treasure vanished...`;
    }
    
    // Replace the treasure with a path regardless of answer
    const pos = pendingTreasurePosition; // Capture position before resetting state
    setGameMap(prevMap => {
        const newMap = prevMap.map(row => [...row]); 
        if (pos) { // Check if position exists (it should)
           newMap[pos.y][pos.x] = {...cellTypes.path};
        }
        return newMap;
    });
    
    setMessage(messageText);
    
    // Reset the challenge state immediately
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");

    // Map regeneration check is now handled by the useEffect watching treasuresCollectedThisMap

  }, [currentWord, pendingTreasurePosition, selectedWord, setGameMap, setMessage, setTotalScore, setTreasuresCollectedThisMap, setIsTranslationChallengeActive, setCurrentWord, setPendingTreasurePosition, setSelectedWord]); // Dependencies updated
  
  // --- Effect to Check for Map Completion ---
  useEffect(() => {
    // Only run if treasures have been collected AND we know the total number
    if (treasuresCollectedThisMap > 0 && totalTreasuresOnMap > 0 && treasuresCollectedThisMap >= totalTreasuresOnMap) {
      console.log(`[Map Completion Check] All ${totalTreasuresOnMap} treasures collected! Regenerating map.`);
      setMessage(`Map Cleared! Score: ${totalScore + 1}. Generating new map...`); // Show score before regeneration starts
      // Regenerate map, preserving the score
      regenerateMap(true); 
    }
  // Depend on the count of treasures collected on this map and the total expected
  }, [treasuresCollectedThisMap, totalTreasuresOnMap, regenerateMap, totalScore, setMessage]);


  // --- Initialization: Find Player Start & Set Active --- 
  useEffect(() => {
    console.log("[Initialization Effect] Running due to map change...");
    setIsGameActive(false); // Keep game inactive during init
    let foundStart = false;

    // Determine initial message based on word loading status
    if (isLoadingWords) {
      setMessage('Loading language data...');
    } else if (wordsError) {
      setMessage(wordsError); // Prioritize showing the word fetch error
    } else {
      setMessage('Placing character on map...'); // If words loaded, show map init message
    }

    console.log("[Initialization Effect] Searching for passable start tile...");
    for (let y = 0; y < mapHeight; y++) {
      for (let x = 0; x < mapWidth; x++) {
        if (gameMap[y]?.[x]?.passable) {
          console.log(`[Initialization Effect] Found valid player start at (${x}, ${y})`);
          setPlayerPosition({ x, y });

          // Activate game and set final message only when words are also ready (loaded or errored)
          if (!isLoadingWords) {
            console.log("[Initialization Effect] Activating game.");
            setIsGameActive(true); // ACTIVATE GAME
            setMessage(wordsError ? wordsError : `Use arrow keys or WASD to move. Learn ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'}!`);
          } else {
            // If words are still loading, keep the loading message
            setMessage('Loading language data...'); 
          }
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
       setPlayerPosition({ x: -1, y: -1 }); // Explicitly set invalid position
    } else {
        console.log("[Initialization Effect] Initialization complete (player position found).");
    }
    // Depend on map key, word loading state, word error, and language. Removed gameMap.
  }, [mapGenerationKey, isLoadingWords, wordsError, selectedLanguage]); 

  // Handle keyboard movement for Player
  useEffect(() => {
    // Prevent movement if overall loading is true, game isn't active, or popups are open
    if (isLoading || !isGameActive || isTranslationChallengeActive || isBattleActive) return;

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
             if (words.length > 0) { // Use words from hook
                const word = getRandomTranslationChallenge();
                
                // --- Generate Translation Options ---
                const correctAnswer = word.english;
                const otherWords = words.filter(w => w.id !== word.id);
                
                // Shuffle other words to get random incorrect options
                const shuffledOthers = [...otherWords].sort(() => 0.5 - Math.random());
                
                // Take up to 4 incorrect options
                const incorrectOptions = shuffledOthers.slice(0, 4).map(w => w.english);
                
                // Combine correct and incorrect, then shuffle the final list
                let options = [correctAnswer, ...incorrectOptions];
                // Ensure we have exactly 5 options if possible, padding if needed (though unlikely with enough words)
                while (options.length < 5 && shuffledOthers.length > options.length -1) {
                   // This logic might be redundant if words.length > 5, but handles edge case
                   options.push(shuffledOthers[options.length - 1].english);
                }
                options = options.sort(() => 0.5 - Math.random()); 
                // --- End Generate Options ---

                setTranslationOptions(options); // Set the options state
                setCurrentWord(word);
                setIsTranslationChallengeActive(true);
                setPendingTreasurePosition({ x: newX, y: newY });
                setSelectedWord(""); // Reset selection
                specialTileMessage = `Treasure! Translate: "${word.targetWord}"`;
             } else {
                setTreasuresCollectedThisMap(prev => prev + 1);
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
  // Dependencies updated: use combined isLoading, removed selectedLanguage (implicit via words/wordsError)
  }, [isLoading, isGameActive, isTranslationChallengeActive, isBattleActive, playerPosition, gameMap, onPositionChange, words, wordsError, setPlayerPosition, setMessage, setCurrentWord, setIsTranslationChallengeActive, setPendingTreasurePosition, setTreasuresCollectedThisMap, setGameMap]); 
  
  // Regenerate Map Function (Wrapped in useCallback) - Now uses the shared regenerateMap function
  const handleGenerateNewMap = useCallback(() => {
    console.log("[handleGenerateNewMap] User clicked Generate New Map");
    regenerateMap(true); // Call the shared function, preserving score
  }, [regenerateMap]); // Dependency is the memoized regenerateMap function


  // --- Dynamic Title based on Language ---
  const gameTitle = selectedLanguage === 'italian' ? 'Italian Language Adventure' : 'Salish Language Adventure';
  const gameSubtitle = `Explore, learn ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'} words, and capture Wisps!`;
  const translatePrompt = `Translate the following ${selectedLanguage === 'italian' ? 'Italian' : 'Salish'} word:`;

  return (
    <div className="sprite-game-container" tabIndex={0} /* Allow div to receive focus for key events */ >
      {isLoading ? ( // Use combined isLoading state
        <div className="loading-message">{message}</div> // Show current message during load/init
      ) : (
        <>
          {/* Show wordsError only if it exists and words are not currently loading */}
          {wordsError && !isLoadingWords && <div className="error-message">{wordsError}</div>} 
          
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
                  // Disable select while words for that language are loading
                  disabled={isLoadingWords} 
                  onChange={(e) => setSelectedLanguage(e.target.value as 'salish' | 'italian')}
                >
                  <option value="salish">Salish</option>
                  <option value="italian">Italian</option>
                </select>
            </div>
          </div>
          
          <div className="game-stats">
            {/* Updated to show totalScore */}
            <div>Score: {totalScore}</div> 
            {/* Show treasures collected on current map / total for current map */}
            <div>Treasures Found (Map): {treasuresCollectedThisMap} / {totalTreasuresOnMap}</div> 
            {/* Add min-width to prevent layout shift */}
            {playerPosition.x !== -1 && <div style={{ minWidth: '85px', textAlign: 'left' }}>Pos: ({playerPosition.x}, {playerPosition.y})</div>}
            {/* Use words state from hook, show loading/error status */}
            <div>Words Loaded ({selectedLanguage}): {words.length} {isLoadingWords ? '(Loading...)' : ''}{wordsError ? '(Error!)' : ''}</div> 
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
                {/* --- Use translationOptions state for dropdown --- */}
                {translationOptions.map((option, index) => ( 
                  <option key={`${currentWord?.id}-${index}`} value={option}>{option}</option> // Use index for key as options can repeat across challenges
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
            {/* Disable button based on combined isLoading state */}
            <button onClick={handleGenerateNewMap} disabled={isLoading}>Generate New Map (Keep Score)</button> 
          </div>
        </>
      )}
    </div>
  );
};

export default DefaultGameMap; 