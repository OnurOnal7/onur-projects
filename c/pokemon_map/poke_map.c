#include <stdio.h>
#include <stdlib.h>
#include <ncurses.h>
#include <time.h>

// Size of the map.
#define LENGTH 80
#define WIDTH 21

// Struct for a character and its location.
typedef struct {
    int x;
    int y;
    char biomeType;
} Cell;

Cell exitCells[4];
int neighbors[8][2] = {{-1, -1}, {0, -1}, {1, -1}, {-1, 0}, {1, 0}, {-1, 1}, {0, 1}, {1, 1}};

void generate_map();
void generate_borders(char ch);
void swap(char *a, char *b);
void growth_algorithm(Cell seedCells[], int size);
void expandRegion(Cell seedCells[], int size);
void drawPath();
void pokemon_center_or_pokemart(char ch);

int main(int argc, char *argv[]) {
    initscr(); // Initializes ncurses.
    srand(time(NULL)); // Seeds the random number generator.
    generate_map();
    refresh(); // Refreshes screen.
    getch(); // Waits for user input.
    endwin(); // Ends ncurses.
 
    return 0;
}

// Generates the map.
void generate_map() {
    generate_borders('%');

    // Region seeds are 3 x 2 for total of 6 seeds.
    int seedSpacingY = WIDTH / 3;
    int seedSpacingX = LENGTH / 4;
    int seedLocations[6][2];

    // Stores seed locations in 2D array.
    int k = 0;
    for (int i = seedSpacingY; i < WIDTH; i += seedSpacingY) {
        for (int j = seedSpacingX; j < LENGTH; j += seedSpacingX) {
            seedLocations[k][0] = j;
            seedLocations[k][1] = i;
            k++;
        }
    }

    Cell seedCells[6];
    char biomes[6] = {':', ':', '.', '.', '~', '%'};
    int size = sizeof(seedLocations) / sizeof(seedLocations[0]);

    // Generates seed randomly within a 5 x 5 box of the exact seed location.
    for (int i = 0; i < size; i++) {
        int x = (rand() % 5) + (seedLocations[i][0] - 2);
        int y = (rand() % 5) + (seedLocations[i][1] - 2);

        // Randomly selects a biome.
        int biomesSize = (sizeof(biomes) / sizeof(biomes[0])) - i;
        int randBiomeIndex = rand() % biomesSize;

        // Plants the seed.
        mvaddch(y, x, biomes[randBiomeIndex]);

        // Stores the seed and its location.
        seedCells[i] = (Cell){x, y, biomes[randBiomeIndex]};

        // Moves used biome to the end of array and deletes it.
        swap(&biomes[randBiomeIndex], &biomes[biomesSize - 1]);   
    }

    growth_algorithm(seedCells, size);

    // Fills in remaining spots in the map.
    int randNum;
    int randGrass = rand() % 2;
    for (int i = 0; i < WIDTH; i++) {
        for (int j = 0; j < LENGTH; j++) {
            if (mvinch(i, j) == ' ') {
                randNum = (rand() % 100) + 1;

                if ((randNum % 20) < 1) {
                    mvaddch(i, j, '^');
                }
                else {
                    if (randGrass == 0) {
                        mvaddch(i, j, '.');
                    }
                    else {
                        mvaddch(i, j, ':');
                    }
                }
            }
            else if ((mvinch(i, j) == '.') || (mvinch(i, j) == ':')) {
                randNum = (rand() % 100) + 1;

                if ((randNum % 20) < 1) {
                    mvaddch(i, j, '^');
                }
            }
        }
    }
    drawPath();

    pokemon_center_or_pokemart('M');
    pokemon_center_or_pokemart('C');

    // Cleans up the leaking regions.
    mvaddch(WIDTH, LENGTH, '%');
    for (int i = WIDTH + 1; i < 25; i++) {
        for (int j = 0; j < LENGTH; j++) {
            mvaddch(i, j, ' ');
        }
    }
}

// Adds the pokemon center or pokemart at the start of one of the paths.
void pokemon_center_or_pokemart(char ch) {
    while (1) {
        int randNum = rand() % 4;
        int randSide = rand() % 2;
        if (randNum == 0) {
            if (randSide == 1) {
                if ((mvinch(exitCells[0].y - 2, exitCells[0].x + 1) == 'M') ||
                    (mvinch(exitCells[0].y - 2, exitCells[0].x + 1) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[0].y - 2) - i, (exitCells[0].x + 1) + j, ch);
                        }
                    }
                    break;
                }
            }  
            else {
                if ((mvinch(exitCells[0].y - 2, exitCells[0].x - 1) == 'M') ||
                    (mvinch(exitCells[0].y - 2, exitCells[0].x - 1) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[0].y - 2) - i, (exitCells[0].x - 1) - j, ch);
                        }
                    }
                    break;
                }
            }
        }
        else if (randNum == 1) {
            if (randSide == 1) {
                if ((mvinch(exitCells[1].y - 1, exitCells[1].x - 2) == 'M') ||
                    (mvinch(exitCells[1].y - 1, exitCells[1].x - 2) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[1].y - 1) - j, (exitCells[1].x - 2) - i, ch);
                        }
                    }
                    break;
                }
            }  
            else {
                if ((mvinch(exitCells[1].y + 1, exitCells[1].x - 2) == 'M') ||
                    (mvinch(exitCells[1].y + 1, exitCells[1].x - 2) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[1].y + 1) + j, (exitCells[1].x - 2) - i, ch);
                        }
                    }
                    break;
                }
            }
        }
        else if (randNum == 2) {
            if (randSide == 1) {
                if ((mvinch(exitCells[2].y + 2, exitCells[2].x - 1) == 'M') ||
                    (mvinch(exitCells[2].y + 2, exitCells[2].x - 1) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[2].y + 2) + i, (exitCells[2].x - 1) - j, ch);
                        }
                    }
                    break;
                }
            } 
            else {
                if ((mvinch(exitCells[2].y + 2, exitCells[2].x + 1) == 'M') ||
                    (mvinch(exitCells[2].y + 2, exitCells[2].x + 1) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[2].y + 2) + i, (exitCells[2].x + 1) + j, ch);
                        }
                    }
                    break;
                }
            } 
        }
        else {
            if (randSide == 1) {
                if ((mvinch(exitCells[3].y + 1, exitCells[3].x + 2) == 'M') ||
                    (mvinch(exitCells[3].y + 1, exitCells[3].x + 2) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[3].y + 1) + j, (exitCells[3].x + 2) + i, ch);
                        }
                    }
                    break;
                }
            }
            else {
                if ((mvinch(exitCells[3].y - 1, exitCells[3].x + 2) == 'M') ||
                    (mvinch(exitCells[3].y - 1, exitCells[3].x + 2) == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            mvaddch((exitCells[3].y - 1) - j, (exitCells[3].x + 2) + i, ch);
                        }
                    }
                    break;
                }
            }  
        } 
    } 
}

// Function that draws the W-E and N-S paths.
void drawPath() {
    int coordY;
    int coordX;
    
    // Draws the W-E path.
    for (int i = 0; i < WIDTH; i++) {
        if (mvinch(i, 0) == '#') {
            coordY = i;
            break;
        }
    }
    int randNumX = (rand() % LENGTH / 2) + 20;

    for (int i = 0; i < randNumX; i++) {
        mvaddch(coordY, i, '#');

        if (i == (randNumX - 1)) {
            coordX = i;
        }
    }
    
    if (exitCells[1].y > coordY) {
        for (int i = coordY; i <= exitCells[1].y; i++) {
            mvaddch(i, coordX, '#');

            if (i == exitCells[1].y) {
                coordY = i;
                break;
            }
        }
    }
    else if (exitCells[1].y < coordY) {
        for (int i = coordY; i >= exitCells[1].y; i--) {
            mvaddch(i, coordX, '#');

            if (i == exitCells[1].y) {
                coordY = i;
                break;
            }
        }
    }
    
    for (int i = coordX; i < exitCells[1].x; i++) {
        mvaddch(coordY, i, '#');
    }

    // Draws the N-S path.
    for (int i = 0; i < LENGTH; i++) {
        if (mvinch(0, i) == '#') {
            coordX = i;
            break;
        }
    }
    int randNumY = (rand() % WIDTH / 2) + 5;

    for (int i = 0; i < randNumY; i++) {
        mvaddch(i, coordX, '#');

        if (i == (randNumY - 1)) {
            coordY = i;
        }
    }
    
    if (exitCells[0].x > coordX) {
        for (int i = coordX; i <= exitCells[0].x; i++) {
            mvaddch(coordY, i, '#');

            if (i == exitCells[0].x) {
                coordX = i;
                break;
            }
        }
    }
    else if (exitCells[0].x < coordX) {
        for (int i = coordX; i >= exitCells[0].x; i--) {
            mvaddch(coordY, i, '#');

            if (i == exitCells[0].x) {
                coordX = i;
                break;
            }
        }
    }
    
    for (int i = coordY; i < exitCells[0].y; i++) {
        mvaddch(i, coordX, '#');
    }
}

// Carries out the growth algorithm for each region.
void growth_algorithm(Cell seedCells[], int size) {
    expandRegion(seedCells, size);

    // Extrapolates region to entire map after expanding the region of each seed. 
    for (int i = 1; i < WIDTH; i++) {
        for (int j = 1; j < LENGTH; j++) {
            for (int k = 0; k < size; k++) {
                if (mvinch(i, j) == seedCells[k].biomeType) {
                    seedCells[k].x = j;
                    seedCells[k].y = i;
                    expandRegion(seedCells, size);
                }
            }
        }
    }
}

// Implements the growth algorithm for a random region.
void expandRegion(Cell seedCells[], int size) {
    int num = 0;
    Cell region;

    // Expands seed region for each seed.
    while (num < 6) {
        int neighborsSize = sizeof(neighbors) / sizeof(neighbors[0]);
        int n = neighborsSize;
        region = seedCells[num];

        // Expands region to available neighbors.
        for (int i = 0; i < neighborsSize; i++) {
            int randNeighborIndex = rand() % n;
            int newX = region.x + neighbors[randNeighborIndex][0];
            int newY = region.y + neighbors[randNeighborIndex][1];

            if (mvinch(newY, newX) == ' ') {
                mvaddch(newY, newX, region.biomeType);

                region.x = newX;
                region.y = newY;
            }
            else if (mvinch(newY, newX) == region.biomeType) {
                continue;
            }
            else {
                break;
            }
        }
        num++;
    }
}
    
// Swaps two characters.
void swap(char *a, char *b) {
    char temp = *a;
    *a = *b;
    *b = temp;
}

// Function that draws the borders of the map.
void generate_borders(char ch) {
    // Draws borders.
    mvhline(0, 0, ch, LENGTH);
    mvhline(WIDTH, 0, ch, LENGTH);
    mvvline(0, 0, ch, WIDTH);
    mvvline(0, LENGTH, ch, WIDTH);


    int exitRandN = (rand() % (LENGTH - 20)) + 10;
    int exitRandS = (rand() % (LENGTH - 20)) + 10;
    int exitRandE = (rand() % (WIDTH / 2)) + 5;
    int exitRandW = (rand() % (WIDTH / 2)) + 5;

    // Draws exit points at borders.
    mvaddch(0, exitRandN, '#');
    mvaddch(WIDTH, exitRandS, '#');
    mvaddch(exitRandE, LENGTH, '#');
    mvaddch(exitRandW, 0, '#');

    exitCells[0].x = exitRandS;     // South gate.
    exitCells[0].y = WIDTH;         
    exitCells[0].biomeType = '#';

    exitCells[1].x = LENGTH;        // East gate.
    exitCells[1].y = exitRandE;     
    exitCells[1].biomeType = '#';

    exitCells[2].x = exitRandN;     // North gate.
    exitCells[2].y = 0;     
    exitCells[2].biomeType = '#';

    exitCells[3].x = 0;              // West gate.
    exitCells[3].y = exitRandW;     
    exitCells[3].biomeType = '#';
}

