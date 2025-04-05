import React, { useState, useEffect, useRef } from 'react';

// Updated phases for the new mechanic
type BattlePhase = 'battle' | 'success' | 'fail';
type MarkerDirection = 'left' | 'right'; // For oscillation

interface BattlePopoverProps {
  // wordToGuess removed
  wispRarity: number; // Lower number = harder/faster (e.g., 1=rare, 2=uncommon, 3=common)
  onClose: (result: { caught: boolean; treasureMultiplier: number }) => void; 
}

// Constants for the mini-game
const BAR_WIDTH = 300; // px width of the visual bar
const MARKER_WIDTH = 10; // px width of the marker
const CENTER_TARGET = 50; // Target position (center)
const SUCCESS_THRESHOLD = 15; // +/- from center for success
const MAX_BOUNCES = 12; // 6 full back-and-forth cycles
const BASE_SPEED_MS = 10; // Decreased for faster default speed

const BattlePopover: React.FC<BattlePopoverProps> = ({ wispRarity, onClose }) => {
  const [phase, setPhase] = useState<BattlePhase>('battle');
  // userGuess, isCorrect, correctGuess removed
  const [markerPosition, setMarkerPosition] = useState(100); // Start at the right (100%)
  const [markerDirection, setMarkerDirection] = useState<MarkerDirection>('left'); // Start moving left
  const [bounceCount, setBounceCount] = useState(0);
  const [isStopped, setIsStopped] = useState(false);
  const intervalRef = useRef<number | null>(null);

  // --- Game Loop Effect --- 
  useEffect(() => {
    if (phase !== 'battle' || isStopped) return;

    const speedMultiplier = wispRarity; 
    const intervalDuration = BASE_SPEED_MS * speedMultiplier;

    intervalRef.current = setInterval(() => {
        // Use functional updates for state that depends on previous state
        setMarkerPosition(prevPos => {
            let nextPos = prevPos;
            if (markerDirection === 'left') {
                nextPos = prevPos - 1;
            } else {
                nextPos = prevPos + 1;
            }

            // Check for edge hits BEFORE updating position state
            if (nextPos <= 0 || nextPos >= 100) {
                // Hit an edge, reverse direction and count bounce
                const newDirection = nextPos <= 0 ? 'right' : 'left';
                const newBounceCount = bounceCount + 1;
                
                // Update direction and bounce count state
                setMarkerDirection(newDirection);
                setBounceCount(newBounceCount);

                 // Ensure position doesn't go beyond bounds visually
                nextPos = Math.max(0, Math.min(100, nextPos));

                // Check if max bounces reached
                if (newBounceCount >= MAX_BOUNCES) {
                    console.log("Max bounces reached!");
                    clearInterval(intervalRef.current!);
                    setIsStopped(true);
                    setTimeout(() => setPhase('fail'), 300); // Fail slightly faster
                    return nextPos; // Return clamped position before failing
                }
            }
            return nextPos;
        });
    }, intervalDuration);

    // Cleanup interval
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  // Dependencies now include markerDirection and bounceCount as they influence the interval logic
  }, [phase, isStopped, wispRarity, markerDirection, bounceCount]);

  // --- Spacebar Listener Effect --- 
  useEffect(() => {
    if (phase !== 'battle' || isStopped) return; 

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code === 'Space' || event.key === ' ') {
        event.preventDefault();
        if (intervalRef.current) {
           clearInterval(intervalRef.current);
        }
        setIsStopped(true);

        const currentPos = markerPosition; // Capture position when stopped
        const distance_from_center = Math.abs(currentPos - CENTER_TARGET);
        console.log(`Stopped at: ${currentPos}, Distance from center: ${distance_from_center}`);

        if (distance_from_center <= SUCCESS_THRESHOLD) {
            setPhase('success');
        } else {
            setPhase('fail');
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  // Re-add markerPosition to deps to ensure handler has latest value
  }, [phase, isStopped, markerPosition]); 

  // Effect to automatically close on success/fail after a delay
  useEffect(() => {
    if (phase === 'success') {
      setTimeout(() => onClose({ caught: true, treasureMultiplier: 2 }), 1500); 
    } else if (phase === 'fail') {
      setTimeout(() => onClose({ caught: false, treasureMultiplier: 1 }), 1500);
    }
     // `escaped` phase removed
  }, [phase, onClose]);


  return (
    <div style={styles.overlay}>
      <div style={styles.popover}>
        {/* Phase 1: Initial Check Removed */} 
        
        {/* Phase 2: Battle Mini-game */} 
        {phase === 'battle' && (
          <>
            <h2>Catch the Wisp!</h2>
            <p>Press SPACE when the marker is in the green zone!</p>
            <div style={{ ...styles.battleBarContainer, width: `${BAR_WIDTH}px` }}>
              {/* Green Success Zone */} 
              <div style={{...
                  styles.zone,
                  backgroundColor: 'rgba(0, 255, 0, 0.3)',
                  left: `${CENTER_TARGET - SUCCESS_THRESHOLD}%`, 
                  width: `${SUCCESS_THRESHOLD * 2}%`
              }}></div>
              {/* Marker */}
              <div style={{
                  ...styles.marker,
                  // Use state directly for marker position
                  left: `calc(${markerPosition}% - ${MARKER_WIDTH / 2}px)` 
              }}></div>
            </div>
             <p style={{marginTop: '10px', fontSize: '0.9em', color: '#666'}}> 
                Bounces: {bounceCount} / {MAX_BOUNCES}
             </p>
          </>
        )}

         {/* Phase 3: Success */} 
         {phase === 'success' && (
          <>
            <h2>Success!</h2>
            <p>You caught the wisp!</p>
             {/* Auto closes via useEffect */} 
          </>
         )}

         {/* Phase 4: Fail */} 
         {phase === 'fail' && (
          <>
            <h2>Oh No!</h2>
            <p>The wisp got away!</p>
            {/* Auto closes via useEffect */} 
          </>
         )}

        {/* Phase 5: Escaped Removed */} 
      </div>
    </div>
  );
};

// Basic styling - consider moving to a CSS file
const styles: { [key: string]: React.CSSProperties } = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  popover: {
    background: 'white',
    padding: '25px',
    borderRadius: '8px',
    textAlign: 'center',
    width: '90%',
    maxWidth: '450px', // Slightly wider for the bar
    boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
    color: '#333',
  },
  input: { // Kept for potential future use, but not used now
    padding: '10px',
    marginRight: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    width: 'calc(70% - 22px)',
  },
  button: { // Kept for potential future use
    padding: '10px 15px',
    borderRadius: '4px',
    border: 'none',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
  },
  battleBarContainer: {
      marginTop: '20px',
      height: '30px', // Can adjust height
      backgroundColor: '#eee',
      position: 'relative',
      border: '1px solid #ccc',
      borderRadius: '5px',
      overflow: 'hidden', // Hide parts of marker if it goes past edges
      margin: '20px auto' // Center the bar
  },
  zone: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    // backgroundColor set dynamically
  },
  marker: {
      position: 'absolute',
      top: '-2px', // Slight offset to overlap border nicely
      bottom: '-2px',
      width: `${MARKER_WIDTH}px`,
      backgroundColor: '#dc3545', // Red marker
      border: '1px solid #8b0000',
      borderRadius: '2px',
      zIndex: 2,
      // left position set dynamically
  }
};

export default BattlePopover; 