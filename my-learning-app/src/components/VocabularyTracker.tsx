import React from 'react';

interface Word {
    id: number;
    kanji: string;
    romaji: string;
    english: string;
}

interface VocabularyTrackerProps {
    words: Word[];
}

function VocabularyTracker({ words }: VocabularyTrackerProps) {
    return (
        <div>
            <h3>Vocabulary:</h3>
            <ul>
                {words.map((word) => (
                    <li key={word.id}>
                        {word.kanji} ({word.romaji}) - {word.english}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default VocabularyTracker; 