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

                        if (rowIndex === playerPosition.row && colIndex === playerPosition.col) {
                            cellContent = 'P'; // Player
                        }

                        return (
                            <span key={colIndex} className="game-cell">
                                {cellContent}
                            </span>
                        );
                    })}
                </div>
            ))}
        </div>
    );
}

export default GameMap; 