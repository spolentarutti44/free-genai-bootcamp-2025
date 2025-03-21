import { useState, useEffect } from 'react'
import './App.css'
import DefaultGameMap from './components/DefaultGameMap'

// You can set this based on environment variables in a real app
const API_BASE_URL = 'http://localhost:5001/api';

const App: React.FC = () => {
  const [playerProgress, setPlayerProgress] = useState<{[key: string]: boolean}>({})
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    // Set the document title
    document.title = 'SLP Lang Learn';
    
    // Ensure the game map gets focus when the component mounts
    setIsLoaded(true);
    
    // Add focus handling to make keyboard controls work properly
    const handleFocus = () => {
      const gameContainer = document.querySelector('.sprite-game-container');
      if (gameContainer) {
        gameContainer.setAttribute('tabindex', '0');
        (gameContainer as HTMLElement).focus();
      }
    };
    
    window.addEventListener('click', handleFocus);
    
    // Call handleFocus after a short delay to ensure the DOM has updated
    setTimeout(handleFocus, 100);
    
    return () => {
      window.removeEventListener('click', handleFocus);
    };
  }, []);

  // Handle player position changes
  const handlePositionChange = (position: { x: number, y: number }) => {
    console.log(`Player moved to position: (${position.x}, ${position.y})`);
    // You could add game logic here based on player position
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo-container">
          <div className="app-logo">🌎</div>
        </div>
        <h1>SLP Lang Learn</h1>
        <p className="header-subtitle">Explore, Discover, and Learn Salish Language</p>
      </header>
      
      <main className="app-main">
        {isLoaded && (
          <DefaultGameMap 
            onPositionChange={handlePositionChange} 
            playerProgress={playerProgress}
            apiBaseUrl={API_BASE_URL}
          />
        )}
        
        <div className="instruction-card">
          <h2>How to Play</h2>
          <p>
            Use <kbd>↑</kbd> <kbd>↓</kbd> <kbd>←</kbd> <kbd>→</kbd> arrows or <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> keys to move.
          </p>
          <p>
            Find treasures 💎 to learn Salish words and phrases!
          </p>
          {!isLoaded && <p className="loading-text">Loading game map...</p>}
        </div>
      </main>
      
      <footer className="app-footer">
        <p>© 2024 SLP Lang Learn - Learning through exploration</p>
      </footer>
    </div>
  )
}

export default App
