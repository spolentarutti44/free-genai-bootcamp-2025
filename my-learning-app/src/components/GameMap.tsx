import React from 'react';

interface GameMapProps {
    map: string[][]; // 2D array representing the map
    playerPosition: { row: number; col: number };
}

function GameMap({ map, playerPosition }: GameMapProps) {
    return (
        <div className="game-map">
            {map.map((row, rowIndex) => (
                <div key={rowIndex} className="game-row">
                    {row.map((cell, colIndex) => {
                        let cellContent = cell;
                        let isPlayer = rowIndex === playerPosition.row && colIndex === playerPosition.col;

                        return (
                            <span
                                key={colIndex}
                                className={`game-cell ${isPlayer ? 'player-cell' : ''}`}
                            >
                                {isPlayer ? 'P' : cellContent}
                            </span>
                        );
                    })}
                </div>
            ))}
        </div>
    );
}

export default GameMap; 