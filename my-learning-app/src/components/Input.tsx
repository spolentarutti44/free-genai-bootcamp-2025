import React, { useState } from 'react';

interface InputProps {
    onEnter: (command: string) => void;
}

function Input({ onEnter }: InputProps) {
    const [command, setCommand] = useState('');

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setCommand(event.target.value);
    };

    const handleInputKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            onEnter(command);
            setCommand('');
        }
    };

    return (
        <div>
            <input
                type="text"
                value={command}
                onChange={handleInputChange}
                onKeyDown={handleInputKeyDown}
                placeholder="Enter command"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            />
        </div>
    );
}

export default Input; 