import React from 'react';

interface GameMapProps {
    map: string[][]; // 2D array representing the map
}

function GameMap({ map }: GameMapProps) {
    return (
        <div>
            <h3>Game Map:</h3>
            <pre>
                {map.map((row, rowIndex) => (
                    <div key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                            <span key={cellIndex}>{cell}</span>
                        ))}
                        <br />
                    </div>
                ))}
            </pre>
        </div>
    );
}

export default GameMap; 