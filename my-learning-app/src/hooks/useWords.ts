import { useState, useEffect } from 'react';

// Define the structure for a word entry
export interface WordData {
  id: string;
  english: string;
  targetWord: string; // Generic field for the selected language's word
}

interface UseWordsProps {
  apiBaseUrl: string;
  selectedLanguage: 'salish' | 'italian';
}

interface UseWordsReturn {
  words: WordData[];
  isLoading: boolean;
  error: string | null;
}

// Custom hook to fetch words based on the selected language
export const useWords = ({ apiBaseUrl, selectedLanguage }: UseWordsProps): UseWordsReturn => {
  const [words, setWords] = useState<WordData[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWords = async () => {
      try {
        // Reset state for the new fetch operation
        setIsLoading(true);
        setError(null);
        setWords([]); // Clear previous words

        console.log(`[useWords] Fetching words for language: ${selectedLanguage}`);
        const response = await fetch(`${apiBaseUrl}/words?language=${selectedLanguage}`);

        if (!response.ok) {
          throw new Error(`API error: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[useWords] API Response:', data);

        if (data && Array.isArray(data.items) && data.items.length > 0) {
          const fetchedWords = data.items.map((item: any) => ({
            id: item.id || String(Math.random()), // Ensure ID exists
            english: item.english,
            targetWord: item.target_word || `[Missing Target Word]`, // Use the correct field
          }));
          setWords(fetchedWords);
        } else {
          console.warn('[useWords] API response not in expected format or empty:', data);
          // Set language-specific fallback words if API data is missing/invalid
          setError(`Warning: No ${selectedLanguage} words found in API. Using sample data.`);
          setWords(getFallbackWords(selectedLanguage));
        }
      } catch (err: any) {
        console.error(`[useWords] Error fetching ${selectedLanguage} words:`, err);
        setError(`Failed to load ${selectedLanguage} language data. Using sample data instead. (${err.message})`);
        // Set language-specific fallback words on error
        setWords(getFallbackWords(selectedLanguage));
      } finally {
        // Ensure loading state is turned off after fetch attempt
        setIsLoading(false);
      }
    };

    fetchWords();
    // Dependency array: refetch whenever the API URL or language changes
  }, [apiBaseUrl, selectedLanguage]);

  // Helper function to get fallback words based on language
  const getFallbackWords = (language: 'salish' | 'italian'): WordData[] => {
    if (language === 'italian') {
      return [
        { id: 'it1', english: "hello", targetWord: "ciao" },
        { id: 'it2', english: "thank you", targetWord: "grazie" },
        { id: 'it3', english: "water", targetWord: "acqua" },
        { id: 'it4', english: "tree", targetWord: "albero" },
        { id: 'it5', english: "mountain", targetWord: "montagna" }
      ];
    } else { // Default to Salish fallback
      return [
        { id: 'sa1', english: "hello", targetWord: "huy" },
        { id: 'sa2', english: "thank you", targetWord: "huy' ch q'u" },
        { id: 'sa3', english: "water", targetWord: "qʷəlúltxʷ" },
        { id: 'sa4', english: "tree", targetWord: "sc'əɬálqəb" },
        { id: 'sa5', english: "mountain", targetWord: "tukʷtukʷəʔtəd" }
      ];
    }
  };

  // Return the state variables needed by the component
  return { words, isLoading: isLoading, error };
}; 