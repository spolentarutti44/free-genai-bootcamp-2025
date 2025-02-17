import React from 'react';

interface ProgressTrackerProps {
    current: number;
    total: number;
}

function ProgressTracker({ current, total }: ProgressTrackerProps) {
    return (
        <div className="mb-4">
            Progress: {current} / {total}
        </div>
    );
}

export default ProgressTracker; 