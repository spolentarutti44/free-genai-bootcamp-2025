import React, { useState, useEffect } from 'react';
import '../styles/GameMap.css';

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
  const [playerPosition, setPlayerPosition] = useState<Position>({ x: Math.floor(mapWidth / 2), y: Math.floor(mapHeight / 2) });
  const [treasuresCollected, setTreasuresCollected] = useState<number>(0);
  const [message, setMessage] = useState<string>('Use arrow keys or WASD to move.');
  
  // Translation challenge states
  const [isTranslationChallengeActive, setIsTranslationChallengeActive] = useState<boolean>(false);
  const [currentWord, setCurrentWord] = useState<SalishWord | null>(null);
  const [selectedWord, setSelectedWord] = useState<string>("");
  const [pendingTreasurePosition, setPendingTreasurePosition] = useState<Position | null>(null);
  
  // API data states
  const [salishWords, setSalishWords] = useState<SalishWord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
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
        
        // Check if data exists and has the expected structure with items array
        if (data && Array.isArray(data.items) && data.items.length > 0) {
          // Extract the words from the items array
          const words = data.items.map((item: any) => ({
            id: item.id || String(Math.random()), // Fallback to random ID if none exists
            english: item.english,
            salish: item.salish
          }));
          
          setSalishWords(words);
          return; // Exit early if we successfully set the words
        }
        
        console.warn('API response not in expected format:', data);
        // Fallback words if API doesn't return expected format
        setSalishWords([
          { id: '1', english: "hello", salish: "huy" },
          { id: '2', english: "thank you", salish: "huy' ch q'u" },
          { id: '3', english: "water", salish: "qʷəlúltxʷ" },
          { id: '4', english: "tree", salish: "sc'əɬálqəb" },
          { id: '5', english: "mountain", salish: "tukʷtukʷəʔtəd" }
        ]);
      } catch (err) {
        console.error('Error fetching Salish words:', err);
        setError('Failed to load language data. Using sample data instead.');
        
        // Use fallback words if API fails
        setSalishWords([
          { id: '1', english: "hello", salish: "huy" },
          { id: '2', english: "thank you", salish: "huy' ch q'u" },
          { id: '3', english: "water", salish: "qʷəlúltxʷ" },
          { id: '4', english: "tree", salish: "sc'əɬálqəb" },
          { id: '5', english: "mountain", salish: "tukʷtukʷəʔtəd" }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSalishWords();
  }, [apiBaseUrl]);
  
  // Generate a random map
  function generateMap(): MapCell[][] {
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
        map[currentY][currentX] = {...cellTypes.path};
        
        if (Math.abs(currentX - endX) > Math.abs(currentY - endY)) {
          currentX += currentX < endX ? 1 : -1;
        } else {
          currentY += currentY < endY ? 1 : -1;
        }
        
        // Avoid going out of bounds
        currentX = Math.max(0, Math.min(currentX, mapWidth - 1));
        currentY = Math.max(0, Math.min(currentY, mapHeight - 1));
      }
      
      // Mark the end point
      map[endY][endX] = {...cellTypes.path};
    }
    
    // Add some treasures
    const numTreasures = Math.floor(Math.random() * 5) + 3;
    for (let i = 0; i < numTreasures; i++) {
      const x = Math.floor(Math.random() * mapWidth);
      const y = Math.floor(Math.random() * mapHeight);
      if (map[y][x].passable) {
        map[y][x] = {...cellTypes.treasure};
      }
    }
    
    // Add some houses
    const numHouses = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numHouses; i++) {
      const x = Math.floor(Math.random() * mapWidth);
      const y = Math.floor(Math.random() * mapHeight);
      if (map[y][x].passable) {
        map[y][x] = {...cellTypes.house};
      }
    }
    
    // Add a cave
    const caveX = Math.floor(Math.random() * mapWidth);
    const caveY = Math.floor(Math.random() * mapHeight);
    if (map[caveY][caveX].passable) {
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
      setMessage(`Correct! The Salish word "${currentWord.salish}" means "${currentWord.english}" in English.`);
      setTreasuresCollected(prev => prev + 1);
      
      // Replace the treasure with a path in the map
      const newMap = [...gameMap];
      newMap[pendingTreasurePosition.y][pendingTreasurePosition.x] = {...cellTypes.path};
      setGameMap(newMap);
    } else {
      // Incorrect answer
      setMessage(`Incorrect. Try again! The correct translation of "${currentWord.salish}" is "${currentWord.english}".`);
    }
    
    // Reset the challenge
    setIsTranslationChallengeActive(false);
    setCurrentWord(null);
    setPendingTreasurePosition(null);
    setSelectedWord("");
  };
  
  // Handle keyboard movement
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't handle movement if a translation challenge is active
      if (isTranslationChallengeActive) return;
      
      let newX = playerPosition.x;
      let newY = playerPosition.y;
      
      switch (e.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
          newY = Math.max(0, playerPosition.y - 1);
          break;
        case 'ArrowDown':
        case 's':
        case 'S':
          newY = Math.min(mapHeight - 1, playerPosition.y + 1);
          break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
          newX = Math.max(0, playerPosition.x - 1);
          break;
        case 'ArrowRight':
        case 'd':
        case 'D':
          newX = Math.min(mapWidth - 1, playerPosition.x + 1);
          break;
        default:
          return;
      }
      
      // Check if the new position is passable
      if (gameMap[newY][newX].passable) {
        let newMessage = '';
        
        // Check for special interactions
        if (gameMap[newY][newX].type === 'treasure') {
          // Only start a translation challenge if we have words
          if (salishWords.length > 0) {
            // Found a treasure - start a translation challenge
            const word = getRandomTranslationChallenge();
            setCurrentWord(word);
            setIsTranslationChallengeActive(true);
            setPendingTreasurePosition({ x: newX, y: newY });
            newMessage = `You found a treasure! Translate the Salish word "${word.salish}" to English.`;
          } else {
            // No words available, just collect the treasure
            setTreasuresCollected(prev => prev + 1);
            newMessage = 'You found a treasure! (Language data not available)';
            
            // Replace the treasure with a path
            const newMap = [...gameMap];
            newMap[newY][newX] = {...cellTypes.path};
            setGameMap(newMap);
          }
        } else if (gameMap[newY][newX].type === 'cave') {
          newMessage = 'You entered a mysterious cave... 🕳️';
        } else if (gameMap[newY][newX].type === 'path') {
          newMessage = 'You are on a path. Where does it lead? ⬜';
        } else {
          newMessage = 'Moving through the terrain... 🌿';
        }
        
        setPlayerPosition({ x: newX, y: newY });
        setMessage(newMessage);
        
        if (onPositionChange) {
          onPositionChange({ x: newX, y: newY });
        }
      } else {
        setMessage(`Can't move there! That's a ${gameMap[newY][newX].type}. ${gameMap[newY][newX].symbol}`);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [playerPosition, gameMap, onPositionChange, isTranslationChallengeActive, salishWords]);
  
  // Find an initial passable position for the player
  useEffect(() => {
    // Look for a passable cell near the center
    for (let y = Math.floor(mapHeight / 2); y < mapHeight; y++) {
      for (let x = Math.floor(mapWidth / 2); x < mapWidth; x++) {
        if (gameMap[y][x].passable) {
          setPlayerPosition({ x, y });
          return;
        }
      }
    }
    
    // Fallback: scan the entire map
    for (let y = 0; y < mapHeight; y++) {
      for (let x = 0; x < mapWidth; x++) {
        if (gameMap[y][x].passable) {
          setPlayerPosition({ x, y });
          return;
        }
      }
    }
  }, [gameMap]);
  
  return (
    <div className="sprite-game-container">
      {isLoading ? (
        <div className="loading-message">Loading language data...</div>
      ) : (
        <>
          {error && <div className="error-message">{error}</div>}
          
          <div className="game-title-section">
            <h2 className="game-title">Salish Language Adventure</h2>
            <p className="game-subtitle">Explore the world and collect language treasures</p>
          </div>
          
          <div className="game-stats">
            <div>Treasures: {treasuresCollected}</div>
            <div>Position: ({playerPosition.x}, {playerPosition.y})</div>
            <div>Words in DB: {salishWords.length}</div>
          </div>
          
          <div className="sprite-map">
            {gameMap.map((row, y) => (
              <div key={y} className="map-row">
                {row.map((cell, x) => (
                  <div 
                    key={`${x}-${y}`} 
                    className={`map-cell ${cell.type}`}
                    style={{ backgroundColor: cell.color }}
                  >
                    {playerPosition.x === x && playerPosition.y === y ? 
                      <span className="player">X</span> : 
                      <span>{cell.symbol}</span>
                    }
                  </div>
                ))}
              </div>
            ))}
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
                {/* Show all words as options to make it more challenging */}
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
            <button onClick={() => setGameMap(generateMap())}>Generate New Map</button>
          </div>
        </>
      )}
    </div>
  );
};

export default DefaultGameMap; 