import React, { useState, useEffect } from 'react';
import GameMap from './GameMap';
import Input from './Input';
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

    const handleCommand = (command: string) => {
        // Process the command (e.g., "north", "south", "east", "west")
        let newRow = playerPosition.row;
        let newCol = playerPosition.col;

        switch (command.toLowerCase()) {
            case 'north':
                newRow -= 1;
                break;
            case 'south':
                newRow += 1;
                break;
            case 'east':
                newCol += 1;
                break;
            case 'west':
                newCol -= 1;
                break;
            default:
                console.log("Invalid command");
                return;
        }

        // Check if the new position is valid
        if (newRow >= 0 && newRow < gameMap.length && newCol >= 0 && newCol < gameMap[0].length && gameMap[newRow][newCol] !== '#') {
            setPlayerPosition({ row: newRow, col: newCol });
        } else {
            console.log("You can't go that way!");
        }
    };

    if (words.length === 0) {
        return <div>Loading...</div>;
    }

    return (
        <div className="flex flex-col">
            <ProgressTracker current={currentWordIndex + 1} total={words.length} />
            <VocabularyTracker words={words.slice(0, currentWordIndex + 1)} />
            <GameMap map={gameMap} />
            <Input onEnter={handleCommand} />
        </div>
    );
}

export default Game; 