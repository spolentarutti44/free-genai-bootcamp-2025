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
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', 'X', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
        ['*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*', '*'],
    ]);
    const [playerPosition, setPlayerPosition] = useState({ row: 4, col: 4 }); // Start position
    const [message, setMessage] = useState(''); // State for displaying messages
    const [selectedWord, setSelectedWord] = useState<string | undefined>(undefined); // State for selected word
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const [canMove, setCanMove] = useState(true); // Initially, the player can move

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

    const showDropdown = () => {
        setIsDropdownVisible(true);
        setCanMove(false); // Disable movement when the dropdown appears
    };

    const handleAnswer = () => {
        if (!selectedWord) {
            setMessage("Please select a word.");
            return;
        }

        if (words[currentWordIndex].english === selectedWord) {
            setScore(score + 1);
            setMessage("Correct!");
            setIsDropdownVisible(false);
            setCanMove(true); // Enable movement after correct answer
        } else {
            setMessage(`Incorrect. The correct answer was ${words[currentWordIndex].english}`);
        }

        if (currentWordIndex < words.length - 1) {
            setCurrentWordIndex(currentWordIndex + 1);
            setSelectedWord(undefined); // Reset selected word
        } else {
            setMessage("Game Over! Your score: " + score); // Set game over message
        }
    };

    // useCallback hook to memoize the handleKeyDown function
    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        if (!canMove) {
            return; // Prevent movement if canMove is false
        }

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
        if (newRow >= 0 && newRow < gameMap.length && newCol >= 0 && newCol < gameMap[0].length && gameMap[newRow][newCol] === '*') {
            setPlayerPosition({ row: newRow, col: newCol });
            setMessage(''); // Clear any previous message

            // Update the game map to reflect the player's new position
            const newGameMap = gameMap.map((row, rowIndex) =>
                row.map((cell, colIndex) => {
                    if (rowIndex === newRow && colIndex === newCol) {
                        return 'X'; // Set the new position to 'X'
                    } else if (rowIndex === playerPosition.row && colIndex === playerPosition.col) {
                        return '*'; // Set the old position back to '*'
                    } else {
                        return cell; // Keep the other cells as they were
                    }
                })
            );
            setGameMap(newGameMap);

            // Randomly show the dropdown after a successful move
            if (Math.random() < 0.5) { // Adjust the probability as needed
                showDropdown();
            }

        } else {
            setMessage("You can't go that way!"); // Set the message
        }
    }, [playerPosition, gameMap, canMove]); // Dependencies for useCallback

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

    const currentWord = words[currentWordIndex];

    return (
        <div className="flex flex-col h-screen">
            <ProgressTracker current={currentWordIndex + 1} total={words.length} />
            <VocabularyTracker words={words.slice(0, currentWordIndex + 1)} />
            <GameMap map={gameMap} playerPosition={playerPosition} />
            {message && <div className="message">{message}</div>} {/* Display the message */}

            {isDropdownVisible && (
                <div className="p-4">
                    <p>Translate the following word:</p>
                    <p className="font-bold">{currentWord.kanji} ({currentWord.romaji})</p>

                    <select
                        className="w-[180px] border border-gray-300 rounded-md py-2 px-3"
                        value={selectedWord}
                        onChange={(e) => setSelectedWord(e.target.value)}
                    >
                        <option value="">Select a translation</option>
                        {words.map((word) => (
                            <option key={word.id} value={word.english}>{word.english}</option>
                        ))}
                    </select>

                    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4" onClick={handleAnswer}>
                        Submit Answer
                    </button>
                </div>
            )}
        </div>
    );
}

export default Game; 