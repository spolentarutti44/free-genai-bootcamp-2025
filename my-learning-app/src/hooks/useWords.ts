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
    const fetchAllWords = async () => {
      setIsLoading(true);
      setError(null);
      setWords([]); // Clear previous words

      try {
        console.log(`[useWords] Fetching total count for language: ${selectedLanguage}`);
        // Step 1: Fetch total count
        const countResponse = await fetch(`${apiBaseUrl}/words?language=${selectedLanguage}&page=1&per_page=1`);
        
        if (!countResponse.ok) {
          throw new Error(`API error (count fetch): ${countResponse.status} - ${countResponse.statusText}`);
        }
        
        const countData = await countResponse.json();
        const totalWords = countData?.total;

        console.log(`[useWords] Total words available for ${selectedLanguage}: ${totalWords}`);

        if (totalWords && totalWords > 0) {
          // Step 2: Fetch all words using the total count
          console.log(`[useWords] Fetching all ${totalWords} words for ${selectedLanguage}...`);
          const allWordsResponse = await fetch(`${apiBaseUrl}/words?language=${selectedLanguage}&page=1&per_page=${totalWords}`);

          if (!allWordsResponse.ok) {
            throw new Error(`API error (all words fetch): ${allWordsResponse.status} - ${allWordsResponse.statusText}`);
          }

          const allWordsData = await allWordsResponse.json();
          console.log('[useWords] API Response (all words):', allWordsData);

          if (allWordsData && Array.isArray(allWordsData.items)) {
            const fetchedWords = allWordsData.items.map((item: any) => ({
              id: item.id || String(Math.random()), 
              english: item.english,
              // Use target_word if available, otherwise fallback based on language (though API should ideally provide target_word)
              targetWord: item.target_word || item[selectedLanguage] || `[Missing Target Word]`, 
            }));
            setWords(fetchedWords);
             console.log(`[useWords] Successfully loaded ${fetchedWords.length} words.`);
          } else {
             console.warn('[useWords] API response for all words not in expected format:', allWordsData);
             setError(`Warning: Could not parse all ${selectedLanguage} words from API. Using sample data.`);
             setWords(getFallbackWords(selectedLanguage));
          }
        } else {
          // No words found based on count
          console.log(`[useWords] No words found for ${selectedLanguage} via API count.`);
          setWords([]); // Set to empty array if count is 0 or undefined
          // Optionally set an info message instead of an error if 0 is valid
          // setError(`Info: No ${selectedLanguage} words currently available.`); 
        }

      } catch (err: any) {
        console.error(`[useWords] Error fetching ${selectedLanguage} words:`, err);
        setError(`Failed to load ${selectedLanguage} language data. Using sample data instead. (${err.message})`);
        setWords(getFallbackWords(selectedLanguage));
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllWords();
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