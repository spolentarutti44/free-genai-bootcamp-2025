import React, { useState, useEffect, useCallback } from 'react';
import GameMap from './GameMap';
import ProgressTracker from './ProgressTracker';
import VocabularyTracker from './VocabularyTracker';

interface Word {
    id: number;
    kanji: string;
    romaji: string;
    english: string;
}

function Game() {
    const [words, setWords] = useState<Word[]>([]);
    const [currentWordIndex, setCurrentWordIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [gameMap, setGameMap] = useState<string[][]>([
        ['#', '#', '#', '#', '#'],
        ['#', 'S', ' ', ' ', '#'],
        ['#', ' ', '#', ' ', '#'],
        ['#', ' ', ' ', 'E', '#'],
        ['#', '#', '#', '#', '#'],
    ]); // Example map
    const [playerPosition, setPlayerPosition] = useState({ row: 1, col: 1 }); // Start position

    useEffect(() => {
        // Fetch words from the backend API
        const fetchWords = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/words'); // Explicitly use 127.0.0.1
                const data = await response.json();
                setWords(data.items); // Assuming the API returns a list of words in the 'items' field
            } catch (error) {
                console.error("Error fetching words:", error);
            }
        };

        fetchWords();
    }, []);

    const handleAnswer = (selectedWord: string) => {
        if (words[currentWordIndex].english === selectedWord) {
            setScore(score + 1);
        }
        if (currentWordIndex < words.length - 1) {
            setCurrentWordIndex(currentWordIndex + 1);
        } else {
            alert("Game Over! Your score: " + score);
        }
    };

    // useCallback hook to memoize the handleKeyDown function
    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        let newRow = playerPosition.row;
        let newCol = playerPosition.col;

        switch (event.key) {
            case 'ArrowUp':
                newRow -= 1;
                break;
            case 'ArrowDown':
                newRow += 1;
                break;
            case 'ArrowLeft':
                newCol -= 1;
                break;
            case 'ArrowRight':
                newCol += 1;
                break;
            default:
                return; // Do nothing if it's not an arrow key
        }

        // Check if the new position is valid
        if (newRow >= 0 && newRow < gameMap.length && newCol >= 0 && newCol < gameMap[0].length && gameMap[newRow][newCol] !== '#') {
            setPlayerPosition({ row: newRow, col: newCol });
        } else {
            console.log("You can't go that way!");
        }
    }, [playerPosition, gameMap]); // Dependencies for useCallback

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);

        // Cleanup the event listener when the component unmounts
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [handleKeyDown]); // Dependency for useEffect

    if (words.length === 0) {
        return <div>Loading...</div>;
    }

    return (
        <div className="flex flex-col">
            <ProgressTracker current={currentWordIndex + 1} total={words.length} />
            <VocabularyTracker words={words.slice(0, currentWordIndex + 1)} />
            <GameMap map={gameMap} playerPosition={playerPosition} />
        </div>
    );
}

export default Game; 