/**
 * Utility functions for generating the game map.
 */

// Define the structure for a map cell
export interface MapCell {
  type: string;
  passable: boolean;
  symbol: string;
  color: string;
}

// Map cell types definitions
export const cellTypes: {[key: string]: MapCell} = {
  grass: { type: 'grass', passable: true, symbol: '🌿', color: '#7cfc00' },
  water: { type: 'water', passable: false, symbol: '🌊', color: '#1e90ff' },
  tree: { type: 'tree', passable: false, symbol: '🌲', color: '#228b22' },
  mountain: { type: 'mountain', passable: false, symbol: '⛰️', color: '#a9a9a9' },
  path: { type: 'path', passable: true, symbol: '⬜', color: '#f5deb3' },
  treasure: { type: 'treasure', passable: true, symbol: '💎', color: '#ffd700' },
  house: { type: 'house', passable: false, symbol: '🏠', color: '#cd853f' },
  cave: { type: 'cave', passable: true, symbol: '🕳️', color: '#696969' }
};

/**
 * Generates a random game map and counts the treasures placed.
 * @param mapWidth The desired width of the map.
 * @param mapHeight The desired height of the map.
 * @returns An object containing the generated map (2D array) and the count of treasures placed.
 */
export function generateMap(mapWidth: number, mapHeight: number): { map: MapCell[][]; treasureCount: number } {
  console.log("[generateMap Util] Generating new map...");
  const map: MapCell[][] = [];
  let treasureCount = 0;

  // Fill with grass initially
  for (let y = 0; y < mapHeight; y++) {
    const row: MapCell[] = [];
    for (let x = 0; x < mapWidth; x++) {
      row.push({...cellTypes.grass});
    }
    map.push(row);
  }

  // Generate water bodies
  const numWaterBodies = Math.floor(Math.random() * 2) + 1;
  for (let i = 0; i < numWaterBodies; i++) {
    const centerX = Math.floor(Math.random() * mapWidth);
    const centerY = Math.floor(Math.random() * mapHeight);
    const radius = Math.floor(Math.random() * 3) + 2;

    for (let y = centerY - radius; y <= centerY + radius; y++) {
      for (let x = centerX - radius; x <= centerX + radius; x++) {
        if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth) {
          const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
          if (distance <= radius && Math.random() < 0.6) {
            map[y][x] = {...cellTypes.water};
          }
        }
      }
    }
  }

  // Generate forests
  const numForests = Math.floor(Math.random() * 3) + 1;
  for (let i = 0; i < numForests; i++) {
    const centerX = Math.floor(Math.random() * mapWidth);
    const centerY = Math.floor(Math.random() * mapHeight);
    const radius = Math.floor(Math.random() * 3) + 2;

    for (let y = centerY - radius; y <= centerY + radius; y++) {
      for (let x = centerX - radius; x <= centerX + radius; x++) {
        if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
          const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
          if (distance <= radius && Math.random() < 0.5) {
            map[y][x] = {...cellTypes.tree};
          }
        }
      }
    }
  }

  // Generate mountains
  const numMountains = Math.floor(Math.random() * 2) + 1;
  for (let i = 0; i < numMountains; i++) {
    const centerX = Math.floor(Math.random() * mapWidth);
    const centerY = Math.floor(Math.random() * mapHeight);
    const radius = Math.floor(Math.random() * 2) + 1;

    for (let y = centerY - radius; y <= centerY + radius; y++) {
      for (let x = centerX - radius; x <= centerX + radius; x++) {
        if (y >= 0 && y < mapHeight && x >= 0 && x < mapWidth && map[y][x].type === 'grass') {
          const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
          if (distance <= radius && Math.random() < 0.65) {
            map[y][x] = {...cellTypes.mountain};
          }
        }
      }
    }
  }

  // Generate paths
  const numPaths = Math.floor(Math.random() * 3) + 1;
  for (let i = 0; i < numPaths; i++) {
    const startX = Math.floor(Math.random() * mapWidth);
    const startY = Math.floor(Math.random() * mapHeight);
    const endX = Math.floor(Math.random() * mapWidth);
    const endY = Math.floor(Math.random() * mapHeight);

    let currentX = startX;
    let currentY = startY;

    while (currentX !== endX || currentY !== endY) {
      // Ensure we don't overwrite non-grass cells with paths unless starting point
      if (map[currentY]?.[currentX]?.type === 'grass' || (currentX === startX && currentY === startY)) {
        map[currentY][currentX] = {...cellTypes.path};
      }

      if (Math.abs(currentX - endX) > Math.abs(currentY - endY)) {
        currentX += currentX < endX ? 1 : -1;
      } else {
        currentY += currentY < endY ? 1 : -1;
      }

      // Avoid going out of bounds during path generation
      currentX = Math.max(0, Math.min(currentX, mapWidth - 1));
      currentY = Math.max(0, Math.min(currentY, mapHeight - 1));
    }

    // Mark the end point as path if it's grass
    if (map[endY]?.[endX]?.type === 'grass') {
       map[endY][endX] = {...cellTypes.path};
    }
  }

  // Add some treasures
  const numTreasures = Math.floor(Math.random() * 5) + 3;
  let treasuresPlaced = 0;
  let attempts = 0;
  const maxAttempts = numTreasures * 5;

  while (treasuresPlaced < numTreasures && attempts < maxAttempts) {
      const x = Math.floor(Math.random() * mapWidth);
      const y = Math.floor(Math.random() * mapHeight);
      if (map[y]?.[x]?.passable) {
          if (map[y][x].type !== 'treasure') {
              map[y][x] = {...cellTypes.treasure};
              treasuresPlaced++;
          }
      }
      attempts++;
  }
  treasureCount = treasuresPlaced;
  console.log(`[generateMap Util] Placed ${treasureCount} treasures.`);

  // Add some houses
  const numHouses = Math.floor(Math.random() * 3) + 1;
  for (let i = 0; i < numHouses; i++) {
    const x = Math.floor(Math.random() * mapWidth);
    const y = Math.floor(Math.random() * mapHeight);
    // Ensure house doesn't overwrite treasure or cave
    if (map[y]?.[x]?.passable && map[y]?.[x]?.type !== 'treasure' && map[y]?.[x]?.type !== 'cave') {
      map[y][x] = {...cellTypes.house};
    }
  }

  // Add a cave
  const caveX = Math.floor(Math.random() * mapWidth);
  const caveY = Math.floor(Math.random() * mapHeight);
   // Ensure cave doesn't overwrite treasure or house
  if (map[caveY]?.[caveX]?.passable && map[caveY]?.[caveX]?.type !== 'treasure' && map[caveY]?.[caveX]?.type !== 'house') {
    map[caveY][caveX] = {...cellTypes.cave};
  }

  return { map, treasureCount };
}; 