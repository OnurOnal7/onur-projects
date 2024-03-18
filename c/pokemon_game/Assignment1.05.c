#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>
#include <time.h>
#include <unistd.h>
#include <stdbool.h>
#include <limits.h>

// Size of the map.
#define MAP_LENGTH 80
#define MAP_WIDTH 21

// Colors.
#define CP_GREY 1
#define CP_BLUE 2
#define CP_GREEN 3
#define CP_DARK_GREEN 4
#define CP_BRIGHT_YELLOW 5
#define CP_BROWN 6
#define CP_RED 7
#define CP_BRIGHT_BLUE 8
#define CP_BRIGHT_RED 9
#define CP_ORANGE 10
#define CP_PURPLE 11
#define CP_PINK 12
#define CP_YELLOW 13
#define CP_CREAM 14
#define CP_TURQUOISE 15

// Size of the world.
#define WORLD_SIZE 401

// Struct for a character and its location.
typedef struct {
    int x;
    int y;
    char biomeType;
    int sequenceNumber;
    int direction[2];
    char placeHolder;
    int order;
} Cell;

// Struct that encapsulates the logic of the entire map.
typedef struct {
    char mapChars[MAP_WIDTH][MAP_LENGTH];
    int topologicalGridHiker[MAP_WIDTH][MAP_LENGTH];
    int topologicalGridOther[MAP_WIDTH][MAP_LENGTH];
    Cell exitCells[4];
    Cell *characters;
} Map;

// Define the priority queue node
struct PQNode {
    Cell data;
};

// Define the priority queue structure
struct PriorityQueue {
    struct PQNode *heap;
    int capacity;
    int size;
};

// Create a priority queue
struct PriorityQueue* createPriorityQueue(int capacity) {
    struct PriorityQueue* pq = (struct PriorityQueue*) malloc(sizeof(struct PriorityQueue));
    pq->capacity = capacity;
    pq->size = 0;
    pq->heap = (struct PQNode*) malloc(capacity * sizeof(struct PQNode));
    return pq;
}

// Create the world of maps.
Map *world[WORLD_SIZE][WORLD_SIZE];

bool quit = 0;
bool inBuilding = 0;
bool windowActive = 0;
int numTrainers = 10; // Default to 10 trainers
int neighbors[8][2] = {{-1, -1}, {0, -1}, {1, -1}, {-1, 0}, {1, 0}, {-1, 1}, {0, 1}, {1, 1}};

// Allowed terrains for characters and trainer types.
char trainerTypes[7] = {'@', 'h', 'r', 'p', 'w', 'e', 's'};
char allowedTerrainsO[] = {'.', ':', '#', 'M', 'C'};
char allowedTerrainsH[] = {'.', ':', '%', '#', 'M', 'C'};

struct PriorityQueue* createPriorityQueue(int capacity);

void generate_map(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell exitCells[4], char direction, Cell exitCellsPrev[4], int x, int y, Cell *characters);
void generate_borders(char mapChars[MAP_WIDTH][MAP_LENGTH], char ch, Cell exitCells[4], char direction, Cell exitCellsPrev[4]);
void swap(char *a, char *b);
void growth_algorithm(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell seedCells[], int size);
void expandRegion(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell seedCells[], int size);
void drawPath(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell exitCells[4]);
void pokemon_center_or_pokemart(char mapChars[MAP_WIDTH][MAP_LENGTH], char ch, Cell exitCells[4]);
//void traverseWorld(char ch, int *row, int *col);
void printColorMap(char mapChars[MAP_WIDTH][MAP_LENGTH]);
void create_topological(int topologicalGrid[MAP_WIDTH][MAP_LENGTH], char mapChars[MAP_WIDTH][MAP_LENGTH], int i, int j, char type);
void addCharacters(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell *characters);
void insert(struct PriorityQueue* pq, Cell data);
Cell extractMin(struct PriorityQueue* pq);
void swap2(struct PQNode *a, struct PQNode *b);
void heapifyUp(struct PriorityQueue* pq, int index);
void heapifyDown(struct PriorityQueue* pq, int index);
void moveCharacter(char mapChars[MAP_WIDTH][MAP_LENGTH], int topologicalGrid[MAP_WIDTH][MAP_LENGTH], Cell *minChar, Cell *characters, int index);
void initColorPairs();
int determineColorPair(char biomeType);

int main(int argc, char *argv[]) {
    // Ncurses initializations.
    initscr();
    cbreak();
    noecho();
    nodelay(stdscr, FALSE);
    keypad(stdscr, TRUE);
    curs_set(0);
    initColorPairs();

    srand(time(NULL)); // Seeds the random number generator.

    // Parse command-line arguments for --numtrainers
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--numtrainers") == 0 && i + 1 < argc) {
            numTrainers = atoi(argv[++i]);
            // Check for valid numTrainers range
            if (numTrainers < 1 || numTrainers > 50) {
                fprintf(stderr, "Error: --numtrainers must be between 1 and 50.\n");
                exit(EXIT_FAILURE);
            }
            break;
        }
    }

    // Fill the matrix with NULL initially.
    for (int i = 0; i < WORLD_SIZE; i++) {
        for (int j = 0; j < WORLD_SIZE; j++) {
            world[i][j] = NULL;
        }
    }

    int userRow = WORLD_SIZE / 2; // Initialize user's row position.
    int userCol = WORLD_SIZE / 2; // Initialize user's column position.
    char placeHolder = ' ';
    Cell placeHolderCell[4];

    // Dynamically allocate memory for the map at the central position
    world[userRow][userCol] = malloc(sizeof(Map));
    if (!world[userRow][userCol]) {
        fprintf(stderr, "Failed to allocate memory for world map.\n");
        exit(EXIT_FAILURE);
    }

    // Dynamically allocate memory for characters within the map
    world[userRow][userCol]->characters = malloc(sizeof(Cell) * (numTrainers + 1));

    // Creates a blank map.
    for (int i = 0; i < MAP_WIDTH; i++) {
        for (int j = 0; j < MAP_LENGTH; j++) {
            world[userRow][userCol]->mapChars[i][j] = ' ';
        }
    }

    // Sets characters for the current map randomly from trainerTypes
    int randomIndex;
    int appeared;
    for (int i = 0; i < numTrainers + 1; i++) {
        if (i == 0) {
            randomIndex = 0;
        }
        else if (i == 1) {
            randomIndex = (rand() % 2) + 1;
            appeared = randomIndex;
        }
        else if (i == 2) {
            if (appeared == 1) {
                randomIndex = 2;
            }
            else {
                randomIndex = 1;
            }
        }
        else {
            randomIndex = (rand() % 6) + 1; // Select a random trainer type
        }
        world[userRow][userCol]->characters[i].biomeType = trainerTypes[randomIndex];
        world[userRow][userCol]->characters[i].order = i;
    }

    generate_map(world[userRow][userCol]->mapChars, world[userRow][userCol]->exitCells, placeHolder, placeHolderCell, userCol, userRow, world[userRow][userCol]->characters);

    printColorMap(world[userRow][userCol]->mapChars);

    // Creates custom topological grid for hiker.
    for (int i = 0; i < MAP_WIDTH; i++) {
        for (int j = 0; j < MAP_LENGTH; j++) {
            if (world[userRow][userCol]->mapChars[i][j] == '@') {
                create_topological(world[userRow][userCol]->topologicalGridHiker, world[userRow][userCol]->mapChars, i, j, 'h');
                break;
            }
        }
    }

    for (int i = 0; i < MAP_WIDTH; i++) {
        world[userRow][userCol]->topologicalGridHiker[i][0] = 99;
        world[userRow][userCol]->topologicalGridHiker[i][MAP_LENGTH - 1] = 99;
        world[userRow][userCol]->topologicalGridOther[i][0] = 99;
        world[userRow][userCol]->topologicalGridOther[i][MAP_LENGTH - 1] = 99;
    }

    for (int j = 0; j < MAP_LENGTH; j++) {
        world[userRow][userCol]->topologicalGridHiker[0][j] = 99;
        world[userRow][userCol]->topologicalGridHiker[MAP_WIDTH - 1][j] = 99;
        world[userRow][userCol]->topologicalGridOther[0][j] = 99;
        world[userRow][userCol]->topologicalGridOther[MAP_WIDTH - 1][j] = 99;
    }

    struct PriorityQueue* pq = createPriorityQueue(100);

    // Initially insert all characters into the priority queue
    for (int i = 0; i < numTrainers + 1; i++) {
        insert(pq, world[userRow][userCol]->characters[i]);
    }

    while (!quit) {
        if (pq->size == 0) { // Check if the priority queue is empty
            // Re-insert all characters back to the queue
            for (int i = 0; i < numTrainers + 1; i++) {
                insert(pq, world[userRow][userCol]->characters[i]);
            }
        }

        Cell minChar = extractMin(pq); // Extract the character with lowest sequence number.

        moveCharacter(world[userRow][userCol]->mapChars, world[userRow][userCol]->topologicalGridHiker, &minChar, world[userRow][userCol]->characters, minChar.order);
    }

    free(pq->heap);
    free(pq);  

/*
    char ch;
    do {

        printMap(world[userRow][userCol]->mapChars);
        printf("\n");
        
*/
        /* Display user prompt and get input and Display logical coordinates.
        printf("Coordinates: (%d, %d) - Enter direction (n/s/e/w/q): ", userRow, userCol);
        scanf("%c", &ch);
        printf("\n\n");

        // Move user based on input.
        traverseWorld(ch, &userRow, &userCol);

        int neighborRow = userRow;
        int neighborCol = userCol;

        if (ch == 'n') {
            neighborRow++;
        }
        else if (ch == 's') {
            neighborRow--;
        }
        else if (ch == 'e') {
            neighborCol--;
        }
        else if (ch == 'w') {
            neighborCol++;
        }

        // Display the map at the new location.
        if (world[userRow][userCol] == NULL) {
            world[userRow][userCol] = malloc(sizeof(Map));
            
            for (int i = 0; i < MAP_WIDTH; i++) {
                for (int j = 0; j < MAP_LENGTH; j++) {
                    world[userRow][userCol]->mapChars[i][j] = ' ';
                    world[userRow][userCol]->topologicalGrid[i][j] = 0;
                }
            }
            // Sets characters for the current map.
            char biomeTypes[7] = {'@', 'h', 'r', 'p', 'w', 's', 'e'};
            for(int i = 0; i < 7; i++) {
                world[userRow][userCol]->characters[i].biomeType = biomeTypes[i];
            }
            
            // Since this is a new allocation, a new map needs to be generated.
            generate_map(world[userRow][userCol]->mapChars, world[userRow][userCol]->exitCells, ch, world[neighborRow][neighborCol]->exitCells, userCol, userRow, world[userRow][userCol]->characters);
        }

        //refresh(); // Refreshes screen.
    } while (ch != 'q'); // Repeat until user quits.
    */
    /*
    for (int i = 0; i < WORLD_SIZE; i++) {
        for (int j = 0; j < WORLD_SIZE; j++) {
            if (world[i][j] != NULL) {
                free(world[i][j]);
                world[i][j] = NULL; // Prevent use-after-free and double-free errors
            }
        }
    }
    */

    endwin(); // Ends ncurses.

    return 0;
}

// Makes a movement for a character.
void moveCharacter(char mapChars[MAP_WIDTH][MAP_LENGTH], int topologicalGrid[MAP_WIDTH][MAP_LENGTH], Cell *minChar, Cell *characters, int index) {
    if ((minChar->direction[0] == 0) && (minChar->direction[1] == 0)) {
        int randDir = rand() % 8;
        minChar->direction[0] = neighbors[randDir][0];
        minChar->direction[1] = neighbors[randDir][1];
    }
    
    if (minChar->biomeType == '@') {
        printColorMap(mapChars);
        bool moved = 0;

        while (!moved) {
            int selectedNeighbor[2];
            int selectedIndex = -1;
            int ch = getch(); // Gets the keyboard input.
        
            // Handles keyboard input.
            switch (ch) {
                case '7':
                    selectedIndex = 0;
                    break;
                case '8':
                    selectedIndex = 1;
                    break;
                case '9':
                    selectedIndex = 2;
                    break;
                case '6':
                    selectedIndex = 4;
                    break;
                case '3':
                    selectedIndex = 7;
                    break;
                case '2':
                    selectedIndex = 6;
                    break;
                case '1':
                    selectedIndex = 5;
                    break;
                case '4':
                    selectedIndex = 3;
                    break;
                default:
                    break;
            }

            // Keyboard actions.
            if (inBuilding && (ch == '<')) {
                mapChars[minChar->y][minChar->x] = minChar->biomeType;
                char *building;

                if (minChar->placeHolder == 'C') {
                    building = "Pokemon Center";
                }
                else {
                    building = "Pokemart";
                }

                mvprintw(0, 0, "Exiting %s..", building);
                refresh();
                napms(1000);
                inBuilding = 0;
                moved = 1;
            }
            else if (!inBuilding && (selectedIndex > -1)) {
                selectedNeighbor[0] = neighbors[selectedIndex][0];
                selectedNeighbor[1] = neighbors[selectedIndex][1];

                char terrain = mapChars[minChar->y + selectedNeighbor[1]][minChar->x + selectedNeighbor[0]];
                int cost;

                // Confirms that the movement is to a valid terrain.
                switch (terrain) {
                    case '#':
                    case 'M':
                    case 'C':
                    case '.':
                        cost = 10;
                        break;
                    case ':':
                        cost = 20;
                        break;
                    default:
                        cost = INT_MAX;
                        break;
                }
                
                // Apply movement.
                if ((cost != INT_MAX) && (minChar->x + selectedNeighbor[0] != 0) && (minChar->x + selectedNeighbor[0] != MAP_LENGTH - 1) &&
                    (minChar->y + selectedNeighbor[1] != 0) && (minChar->y + selectedNeighbor[1] != MAP_WIDTH - 1)) {
                    int fromX = minChar->x;
                    int fromY = minChar->y;
                    minChar->x += selectedNeighbor[0];
                    minChar->y += selectedNeighbor[1];

                    char temp = minChar->placeHolder;
                    minChar->placeHolder = mapChars[minChar->y][minChar->x];
                    mapChars[minChar->y][minChar->x] = minChar->biomeType;
                    mapChars[fromY][fromX] = temp;
                    minChar->sequenceNumber += cost; 
                    moved = 1;
                }
            }
            else if ((ch == '>') && ((minChar->placeHolder == 'C') || (minChar->placeHolder == 'M'))) {
                mapChars[minChar->y][minChar->x] = minChar->placeHolder;
                char *building;

                if (minChar->placeHolder == 'C') {
                    building = "Pokemon Center";
                }
                else {
                    building = "Pokemart";
                }

                mvprintw(0, 0, "Entering %s..", building);
                refresh();
                napms(1000);
                inBuilding = 1;
                moved = 1;
            }
            else if (ch == ' ') {
                moved = 1;
            }
            else if (ch == 't') {
                // Creates a window for the character list display.
                int listHeight = numTrainers + 2;
                int listWidth = 50;
                WINDOW *window = newwin(listHeight, listWidth, 1, MAP_LENGTH + 1);
                int currentLine = 1;

                // Draws a border and adds a title.
                box(window, 0, 0);
                mvwprintw(window, 0, 1, " Trainers ");

                for (int i = 1; i <= numTrainers; ++i) {
                    int xDis = minChar->x - characters[i].x;
                    int yDis = minChar->y - characters[i].y;
                    char *dirX = "";
                    char *dirY = "";

                    if (xDis < 0) {
                        dirX = "east";
                    }
                    else if (xDis > 0) {
                        dirX = "west";
                    }

                    if (yDis < 0) {
                        dirY = "south";
                    }
                    else if (yDis > 0) {
                        dirY = "north";
                    }

                    mvwprintw(window, i, 1, "Trainer %d:  Type: %c, x: %d %s, y: %d %s",
                            i,
                            characters[i].biomeType,
                            abs(xDis),
                            dirX,
                            abs(yDis),
                            dirY,
                            characters[i].y);
                }
                wrefresh(window); // Refresh the window to display the list.
                
                int key;
                keypad(window, TRUE); // Enable keypad for window.
                key = wgetch(window);

                // 27 is the ASCII code for the escape key.
                while (key != 27) {
                    if ((key == KEY_UP) || (key == KEY_DOWN)) {
                        // Clear the window and redraw the border and title.
                        werase(window);
                        box(window, 0, 0);
                        mvwprintw(window, 0, 1, " Trainers ");

                        for (int i = 1; i <= numTrainers; ++i) {
                            if (i == currentLine) {
                                wattron(window, A_REVERSE); // Highlight the selected line
                            }

                            int xDis = minChar->x - characters[i].x;
                            int yDis = minChar->y - characters[i].y;
                            char *dirX = "";
                            char *dirY = "";

                            if (xDis < 0) {
                                dirX = "east";
                            }
                            else if (xDis > 0) {
                                dirX = "west";
                            }

                            if (yDis < 0) {
                                dirY = "south";
                            }
                            else if (yDis > 0) {
                                dirY = "north";
                            }

                            mvwprintw(window, i, 1, "Trainer %d:  Type: %c, x: %d %s, y: %d %s",
                                    i,
                                    characters[i].biomeType,
                                    abs(xDis),
                                    dirX,
                                    abs(yDis),
                                    dirY,
                                    characters[i].y);
                            
                            if (i == currentLine) {
                                wattroff(window, A_REVERSE); // Remove the highlight
                            }
                        }
                        wrefresh(window);
                    }
                    key = wgetch(window);

                    // Navigate up or down the list
                    if ((key == KEY_UP) && (currentLine > 1)) {
                        currentLine--;
                    }
                    else if ((key == KEY_DOWN) && (currentLine < numTrainers)) {
                        currentLine++;
                    }
                }
                
                if (key == 27) {
                    mvprintw(0, 0, "Exiting trainer list..");
                    refresh();
                    napms(1000);
                    refresh();
                    delwin(window);
                    printColorMap(mapChars);
                    refresh();
                }
            }
            else if (ch == 'Q') {
                moved = 1;
                quit = 1;
            }
        }
        fflush(stdout);
    }
    else if ((minChar->biomeType == 'h') || (minChar->biomeType == 'r')) {
        int smallestIndex = 0; // Assume the first neighbor is the smallest initially
        int smallestValue = topologicalGrid[minChar->y + neighbors[0][1]][minChar->x + neighbors[0][0]]; // Initial smallest value

        // Loop to find the smallest neighbor
        for (int i = 1; i < 8; i++) {
            int y = minChar->y + neighbors[i][1];
            int x = minChar->x + neighbors[i][0];
            char terrain = mapChars[minChar->y + neighbors[i][1]][minChar->x + neighbors[i][0]];
            bool isValidTerrain = false;

            // Check if the current terrain is valid for the given biomeType
            if (minChar->biomeType == 'r') {
                for (int j = 0; j < sizeof(allowedTerrainsO) / sizeof(allowedTerrainsO[0]); j++) {
                    if (terrain == allowedTerrainsO[j]) {
                        isValidTerrain = true;
                        break;
                    }
                }
            } 
            else if (minChar->biomeType == 'h') {
                for (int j = 0; j < sizeof(allowedTerrainsH) / sizeof(allowedTerrainsH[0]); j++) {
                    if (terrain == allowedTerrainsH[j]) {
                        isValidTerrain = true;
                        break;
                    }
                }
            }

            if (isValidTerrain) {
                int currentVal = topologicalGrid[y][x];

                if (currentVal < smallestValue) {
                    smallestValue = currentVal;
                    smallestIndex = i;
                }
            }
        }

        // Apply movement based on the smallest neighbor found
        int fromX = minChar->x;
        int fromY = minChar->y;
        minChar->x += neighbors[smallestIndex][0];
        minChar->y += neighbors[smallestIndex][1];

        topologicalGrid[fromY][fromX] = 95;

        // Update the placeHolder and sequenceNumber.
        char temp = minChar->placeHolder;
        minChar->placeHolder = mapChars[minChar->y][minChar->x];
        mapChars[minChar->y][minChar->x] = minChar->biomeType;
        mapChars[fromY][fromX] = temp;
        minChar->sequenceNumber += smallestValue; 
    }
    else if (minChar->biomeType == 'p') {
        char terrain = mapChars[minChar->y + minChar->direction[1]][minChar->x + minChar->direction[0]];
        bool isValidTerrain = false;

        // Check if the current terrain is valid for the given biomeType
        for (int j = 0; j < sizeof(allowedTerrainsO) / sizeof(allowedTerrainsO[0]); j++) {
            if (terrain == allowedTerrainsO[j]) {
                isValidTerrain = true;
                break;
            }
        }
        
        if (isValidTerrain) {
            char temp = minChar->placeHolder;
            minChar->y += minChar->direction[1];
            minChar->x += minChar->direction[0];
            minChar->placeHolder = mapChars[minChar->y][minChar->x];
            mapChars[minChar->y][minChar->x] = minChar->biomeType;
            mapChars[minChar->y - minChar->direction[1]][minChar->x - minChar->direction[0]] = temp;
            minChar->sequenceNumber += topologicalGrid[minChar->y][minChar->x]; 
        } 
        else {
            // Change direction if the terrain ahead is not valid
            minChar->direction[0] *= -1;
            minChar->direction[1] *= -1;
        }
    }
    else if (minChar->biomeType == 'w') {
        char terrain = mapChars[minChar->y + minChar->direction[1]][minChar->x + minChar->direction[0]];
        bool isValidTerrain = false;

        if (terrain == minChar->placeHolder) {
            isValidTerrain = true;
        }

        if (isValidTerrain) {
            char temp = minChar->placeHolder;
            minChar->y += minChar->direction[1];
            minChar->x += minChar->direction[0];
            minChar->placeHolder = mapChars[minChar->y][minChar->x];
            mapChars[minChar->y][minChar->x] = minChar->biomeType;
            mapChars[minChar->y - minChar->direction[1]][minChar->x - minChar->direction[0]] = temp;
            minChar->sequenceNumber += topologicalGrid[minChar->y][minChar->x]; 
        }
        else {
            int randDir = rand() % 8;
            minChar->direction[0] = neighbors[randDir][0];
            minChar->direction[1] = neighbors[randDir][1];
        }
    }
    else if (minChar->biomeType == 'e') {
        char terrain = mapChars[minChar->y + minChar->direction[1]][minChar->x + minChar->direction[0]];
        bool isValidTerrain = false;

        // Check if the current terrain is valid for the given biomeType
        for (int j = 0; j < sizeof(allowedTerrainsO) / sizeof(allowedTerrainsO[0]); j++) {
            if (terrain == allowedTerrainsO[j]) {
                isValidTerrain = true;
                break;
            }
        }
        
        if (isValidTerrain) {
            char temp = minChar->placeHolder;
            minChar->y += minChar->direction[1];
            minChar->x += minChar->direction[0];
            minChar->placeHolder = mapChars[minChar->y][minChar->x];
            mapChars[minChar->y][minChar->x] = minChar->biomeType;
            mapChars[minChar->y - minChar->direction[1]][minChar->x - minChar->direction[0]] = temp;
            minChar->sequenceNumber += topologicalGrid[minChar->y][minChar->x]; 
        } 
        else {
            int randDir = rand() % 8;
            minChar->direction[0] = neighbors[randDir][0];
            minChar->direction[1] = neighbors[randDir][1];
        }
    }

    characters[index].biomeType = minChar->biomeType;
    characters[index].direction[0] = minChar->direction[0];
    characters[index].direction[1] = minChar->direction[1];
    characters[index].placeHolder = minChar->placeHolder;
    characters[index].sequenceNumber = minChar->sequenceNumber;
    characters[index].x = minChar->x;
    characters[index].y = minChar->y;
}

void create_topological(int topologicalGrid[MAP_WIDTH][MAP_LENGTH], char mapChars[MAP_WIDTH][MAP_LENGTH], int i, int j, char type) {
    int tGras = 0, pMart = 50, path = 10, pCntr = 50, sGras = 10, mtn = 0;
    
    if (type == 'h') {
        tGras = 15;
        mtn = 15;
    }
    else if (type == 'r') {
        tGras = 20;
    }


    // North and West.
    int sum = 0;
    char ch;
    for (int n = (i - 1); n >= 0; n--) {
        ch = mapChars[n][j];
        
        switch(ch) {
            case 'M':
                sum += pMart;
                break;
            case 'C':
                sum += pCntr;
                break;
            case '#':
                sum += path;
                break;
            case '.':
                sum += sGras;
                break;
            case ':':
                sum += tGras;
                break;
            case '%':
                sum += mtn;
            default:
                break;
        }

        topologicalGrid[n][j] = (sum % 100);
        int tempSum = sum;

        for (int m = j; m >= 0; m--) {
            ch = mapChars[n][m];
        
            switch(ch) {
                case 'M':
                    tempSum += pMart;
                    break;
                case 'C':
                    tempSum += pCntr;
                    break;
                case '#':
                    tempSum += path;
                    break;
                case '.':
                    tempSum += sGras;
                    break;
                case ':':
                    tempSum += tGras;
                    break;
                case '%':
                    sum += mtn;
                default:
                    break;
            }
            topologicalGrid[n][m] = (tempSum % 100);
        }
    }

    // East and South.
    sum = 0;
    for (int n = (j - 1); n >= 0; n--) {
        ch = mapChars[i][n];;
        
        switch(ch) {
            case 'M':
                sum += pMart;
                break;
            case 'C':
                sum += pCntr;
                break;
            case '#':
                sum += path;
                break;
            case '.':
                sum += sGras;
                break;
            case ':':
                sum += tGras;
                break;
            case '%':
                sum += mtn;
            default:
                break;
        }

        topologicalGrid[i][n] = (sum % 100);
        int tempSum = sum;

        for (int m = i; m <= MAP_WIDTH; m++) {
            ch = mapChars[m][n];
        
            switch(ch) {
                case 'M':
                    tempSum += pMart;
                    break;
                case 'C':
                    tempSum += pCntr;
                    break;
                case '#':
                    tempSum += path;
                    break;
                case '.':
                    tempSum += sGras;
                    break;
                case ':':
                    tempSum += tGras;
                    break;
                case '%':
                    sum += mtn;
                default:
                    break;
            }
            topologicalGrid[m][n] = (tempSum % 100);
        }
    }

    // South and East.
    sum = 0;
    for (int n = (i + 1); n <= MAP_WIDTH; n++) {
        ch = mapChars[n][j];
        
        switch(ch) {
            case 'M':
                sum += pMart;
                break;
            case 'C':
                sum += pCntr;
                break;
            case '#':
                sum += path;
                break;
            case '.':
                sum += sGras;
                break;
            case ':':
                sum += tGras;
                break;
            case '%':
                sum += mtn;
            default:
                break;
        }

        topologicalGrid[n][j] = (sum % 100);
        int tempSum = sum;

        for (int m = j; m <= MAP_LENGTH; m++) {
            ch = mapChars[n][m];
        
            switch(ch) {
                case 'M':
                    tempSum += pMart;
                    break;
                case 'C':
                    tempSum += pCntr;
                    break;
                case '#':
                    tempSum += path;
                    break;
                case '.':
                    tempSum += sGras;
                    break;
                case ':':
                    tempSum += tGras;
                    break;
                case '%':
                    sum += mtn;
                default:
                    break;
            }
            topologicalGrid[n][m] = (tempSum % 100);
        }
    }

    // East and North.
    sum = 0;
    for (int n = (j + 1); n <= MAP_LENGTH; n++) {
        ch = mapChars[i][n];
        
        switch(ch) {
            case 'M':
                sum += pMart;
                break;
            case 'C':
                sum += pCntr;
                break;
            case '#':
                sum += path;
                break;
            case '.':
                sum += sGras;
                break;
            case ':':
                sum += tGras;
                break;
            case '%':
                sum += mtn;
            default:
                break;
        }

        topologicalGrid[i][n] = (sum % 100);
        int tempSum = sum;

        for (int m = i; m >= 0; m--) {
            ch = mapChars[m][n];
        
            switch(ch) {
                case 'M':
                    tempSum += pMart;
                    break;
                case 'C':
                    tempSum += pCntr;
                    break;
                case '#':
                    tempSum += path;
                    break;
                case '.':
                    tempSum += sGras;
                    break;
                case ':':
                    tempSum += tGras;
                    break;
                case '%':
                    sum += mtn;
                default:
                    break;
            }
            topologicalGrid[m][n] = (tempSum % 100);
        }
    }
}

void clearInputBuffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {} // Clear input buffer
}

/* Traverses maps based on user input.
void traverseWorld(char ch, int *row, int *col) {
    int x, y;
    switch (ch) {
        case 'n':
            if (*row == 0) {
                printf("You cannot exit the world.\n\n");
                usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            }
            else {
                (*row)--;
            }
            clearInputBuffer();
            break;
        case 's':
            if (*row == 400) {
                printf("You cannot exit the world.\n\n");
                usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            }
            else {
                (*row)++;
            }
            clearInputBuffer();
            break;
        case 'e':
            if (*col == 400) {
                printf("You cannot exit the world.\n\n");
                usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            }
            else {
                (*col)++;
            }
            clearInputBuffer();
            break;
        case 'w':
            if (*col == 0) {
                printf("You cannot exit the world.\n\n");
                usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            }
            else {
                (*col)--;
            }
            clearInputBuffer();
            break;
        case 'f':
            printf("Enter new coordinates (0-400): ");
            scanf("%d %d", &y, &x);
            clearInputBuffer();
            
            // Validate coordinates
            if (x >= 0 && x <= 400 && y >= 0 && y <= 400) {
                *row = y;
                *col = x;
            } 
            else {
                printf("Invalid coordinates. Coordinates must be between 0 and 400.\n\n");
                usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            }
            break;
        case 'q':
            printf("Exiting the game...");
            //refresh();
            usleep(1000000); // Pause for 1000 milliseconds (1 second).
            //endwin(); // End ncurses.
            clearInputBuffer();
            exit(0); // Exit the program.
            break;
        default:
            // Print error message for invalid input.
            printf("Invalid input. Please enter n, s, e, w, or q.\n\n");
            //refresh();
            usleep(2000000); // Pause for 2000 milliseconds (2 seconds).
            clearInputBuffer();
            break;
    }
    // Clear the entire screen.
    //clear();
}
*/

// Generates the map.
void generate_map(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell exitCells[4], char direction, Cell exitCellsPrev[4], int x, int y, Cell *characters) { 
    generate_borders(mapChars, '%', exitCells, direction, exitCellsPrev);
    
    // Region seeds are 3 x 2 for total of 6 seeds.
    int seedSpacingY = MAP_WIDTH / 3;
    int seedSpacingX = MAP_LENGTH / 4;
    int seedLocations[6][2];

    // Stores seed locations in 2D array.
    int k = 0;
    for (int i = seedSpacingY; i < MAP_WIDTH; i += seedSpacingY) {
        for (int j = seedSpacingX; j < MAP_LENGTH; j += seedSpacingX) {
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
        mapChars[y][x] = biomes[randBiomeIndex];
        //mvaddch(y, x, biomes[randBiomeIndex]);

        // Stores the seed and its location.
        seedCells[i] = (Cell){x, y, biomes[randBiomeIndex]};

        // Moves used biome to the end of array and deletes it.
        swap(&biomes[randBiomeIndex], &biomes[biomesSize - 1]);   
    }

    growth_algorithm(mapChars, seedCells, size);

    // Fills in remaining spots in the map.
    int randNum;
    int randGrass = rand() % 2;
    for (int i = 0; i < MAP_WIDTH; i++) {
        for (int j = 0; j < MAP_LENGTH; j++) {
            //if (mvinch(i, j) == ' ') {
            if (mapChars[i][j] == ' ') {
                randNum = (rand() % 100) + 1;

                if ((randNum % 20) < 1) {
                    mapChars[i][j] = '^'; 
                    //mvaddch(i, j, '^');
                }
                else {
                    if (randGrass == 0) {
                        mapChars[i][j] = '.'; 
                        //mvaddch(i, j, '.');
                    }
                    else {
                        mapChars[i][j] = ':'; 
                        //mvaddch(i, j, ':');
                    }
                }
            }
            //else if ((mvinch(i, j) == '.') || (mvinch(i, j) == ':')) {
            else if ((mapChars[i][j] == '.') || (mapChars[i][j]) == ':') {
                randNum = (rand() % 100) + 1;

                if ((randNum % 20) < 1) {
                    mapChars[i][j] = '^'; 
                    //mvaddch(i, j, '^');
                }
            }
        }
    }
    drawPath(mapChars, exitCells);

    pokemon_center_or_pokemart(mapChars, 'M', exitCells);
    pokemon_center_or_pokemart(mapChars, 'C', exitCells);

    addCharacters(mapChars, characters);

    // Blocks off exits at world edges.
    if (x == (WORLD_SIZE - 1)) {
        for (int i = 0; i < MAP_WIDTH; i++) {
            if (mapChars[i][MAP_LENGTH - 1] == '#') {
                mapChars[i][MAP_LENGTH - 1] = '%';
            }
        }
    }
    if (y == (WORLD_SIZE - 1)) {
        for (int i = 0; i < MAP_LENGTH; i++) {
            if (mapChars[MAP_WIDTH - 1][i] == '#') {
                mapChars[MAP_WIDTH - 1][i] = '%';
            }
        }
    }
    if (y == 0) {
        for (int i = 0; i < MAP_LENGTH; i++) {
            if (mapChars[0][i] == '#') {
                mapChars[0][i] = '%';
            }
        }
    }
    if (x == 0) {
        for (int i = 0; i < MAP_LENGTH; i++) {
            if (mapChars[i][0] == '#') {
                mapChars[i][0] = '%';
            }
        }
    }
}

// Places characters in appropriate biomes.
void addCharacters(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell *characters) {
    for (int i = 0; i < numTrainers + 1; i++) {
        while (1) {
            int randomX = (rand() % (MAP_LENGTH - 2)) + 1;
            int randomY = (rand() % (MAP_WIDTH - 2)) + 1;

            if (characters[i].biomeType == '@') {
                if (mapChars[randomY][randomX] == '#') {
                    characters[i].x = randomX;
                    characters[i].y = randomY;
                    characters[i].sequenceNumber = 0;
                    characters[i].placeHolder = '#';
                    characters[i].direction[0] = 0;
                    characters[i].direction[1] = 0;
                    mapChars[randomY][randomX] = '@';
                    break;
                }
            }
            else if (characters[i].biomeType == 'h') {
                if ((mapChars[randomY][randomX] != '^') &&
                (mapChars[randomY][randomX] != '~')) {
                    characters[i].x = randomX;
                    characters[i].y = randomY;
                    characters[i].sequenceNumber = 0;
                    characters[i].placeHolder = mapChars[randomY][randomX];
                    characters[i].direction[0] = 0;
                    characters[i].direction[1] = 0;
                    mapChars[randomY][randomX] = characters[i].biomeType;
                    break;
                }
            }
            else {
                if ((mapChars[randomY][randomX] != '^') &&
                (mapChars[randomY][randomX] != '~') &&
                (mapChars[randomY][randomX] != '%')) {
                    characters[i].x = randomX;
                    characters[i].y = randomY;
                    characters[i].sequenceNumber = 0;
                    characters[i].placeHolder = mapChars[randomY][randomX];
                    characters[i].direction[0] = 0;
                    characters[i].direction[1] = 0;
                    mapChars[randomY][randomX] = characters[i].biomeType;
                    break;
                }
            }
        }
    }
}

// Adds the pokemon center or pokemart at the start of one of the paths.
void pokemon_center_or_pokemart(char mapChars[MAP_WIDTH][MAP_LENGTH], char ch, Cell exitCells[4]) {
    while (1) {
        int randNum = rand() % 4;
        int randSide = rand() % 2;
        if (randNum == 0) {
            if (randSide == 1) {
                //if ((mvinch(exitCells[0].y - 2, exitCells[0].x + 1) == 'M') ||
                    //(mvinch(exitCells[0].y - 2, exitCells[0].x + 1) == 'C')) {
                if ((mapChars[exitCells[0].y - 2][exitCells[0].x + 1] == 'M') ||
                    (mapChars[exitCells[0].y - 2][exitCells[0].x + 1] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[0].y - 2) - i, (exitCells[0].x + 1) + j, ch);
                            mapChars[(exitCells[0].y - 2) - i][(exitCells[0].x + 1) + j] = ch; 
                        }
                    }
                    break;
                }
            }  
            else {
                //if ((mvinch(exitCells[0].y - 2, exitCells[0].x - 1) == 'M') ||
                  //  (mvinch(exitCells[0].y - 2, exitCells[0].x - 1) == 'C')) {
                if ((mapChars[exitCells[0].y - 2][exitCells[0].x - 1] == 'M') ||
                    (mapChars[exitCells[0].y - 2][exitCells[0].x - 1] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[0].y - 2) - i, (exitCells[0].x - 1) - j, ch);
                            mapChars[(exitCells[0].y - 2) - i][(exitCells[0].x - 1) - j] = ch; 
                        }
                    }
                    break;
                }
            }
        }
        else if (randNum == 1) {
            if (randSide == 1) {
                //if ((mvinch(exitCells[1].y - 1, exitCells[1].x - 2) == 'M') ||
                  //  (mvinch(exitCells[1].y - 1, exitCells[1].x - 2) == 'C')) {
                if ((mapChars[exitCells[1].y - 1][exitCells[1].x - 2] == 'M') ||
                    (mapChars[exitCells[1].y - 1][exitCells[1].x - 2] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[1].y - 1) - j, (exitCells[1].x - 2) - i, ch);
                            mapChars[(exitCells[1].y - 1) - j][(exitCells[1].x - 2) - i] = ch; 
                        }
                    }
                    break;
                }
            }  
            else {
                //if ((mvinch(exitCells[1].y + 1, exitCells[1].x - 2) == 'M') ||
                  //  (mvinch(exitCells[1].y + 1, exitCells[1].x - 2) == 'C')) {
                if ((mapChars[exitCells[1].y + 1][exitCells[1].x - 2] == 'M') ||
                    (mapChars[exitCells[1].y + 1][exitCells[1].x - 2] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[1].y + 1) + j, (exitCells[1].x - 2) - i, ch);
                            mapChars[(exitCells[1].y + 1) + j][(exitCells[1].x - 2) - i] = ch;
                        }
                    }
                    break;
                }
            }
        }
        else if (randNum == 2) {
            if (randSide == 1) {
                //if ((mvinch(exitCells[2].y + 2, exitCells[2].x - 1) == 'M') ||
                  //  (mvinch(exitCells[2].y + 2, exitCells[2].x - 1) == 'C')) {
                if ((mapChars[exitCells[2].y + 2][exitCells[2].x - 1] == 'M') ||
                    (mapChars[exitCells[2].y + 2][exitCells[2].x - 1] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[2].y + 2) + i, (exitCells[2].x - 1) - j, ch);
                            mapChars[(exitCells[2].y + 2) + i][(exitCells[2].x - 1) - j] = ch;
                        }
                    }
                    break;
                }
            } 
            else {
                //if ((mvinch(exitCells[2].y + 2, exitCells[2].x + 1) == 'M') ||
                  //  (mvinch(exitCells[2].y + 2, exitCells[2].x + 1) == 'C')) {
                if ((mapChars[exitCells[2].y + 2][exitCells[2].x + 1] == 'M') ||
                    (mapChars[exitCells[2].y + 2][exitCells[2].x + 1] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[2].y + 2) + i, (exitCells[2].x + 1) + j, ch);
                            mapChars[(exitCells[2].y + 2) + i][(exitCells[2].x + 1) + j] = ch;
                        }
                    }
                    break;
                }
            } 
        }
        else {
            if (randSide == 1) {
                //if ((mvinch(exitCells[3].y + 1, exitCells[3].x + 2) == 'M') ||
                  //  (mvinch(exitCells[3].y + 1, exitCells[3].x + 2) == 'C')) {
                if ((mapChars[exitCells[3].y + 1][exitCells[3].x + 2] == 'M') ||
                    (mapChars[exitCells[3].y + 1][exitCells[3].x + 2] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[3].y + 1) + j, (exitCells[3].x + 2) + i, ch);
                            mapChars[(exitCells[3].y + 1) + j][(exitCells[3].x + 2) + i] = ch;
                        }
                    }
                    break;
                }
            }
            else {
                //if ((mvinch(exitCells[3].y - 1, exitCells[3].x + 2) == 'M') ||
                  //  (mvinch(exitCells[3].y - 1, exitCells[3].x + 2) == 'C')) {
                if ((mapChars[exitCells[3].y - 1][exitCells[3].x + 2] == 'M') ||
                    (mapChars[exitCells[3].y - 1][exitCells[3].x + 2] == 'C')) {
                    continue;
                }
                else {
                    for (int i = 0; i < 2; i++) {
                        for (int j = 0; j < 2; j++) {
                            //mvaddch((exitCells[3].y - 1) - j, (exitCells[3].x + 2) + i, ch);
                            mapChars[(exitCells[3].y - 1) - j][(exitCells[3].x + 2) + i] = ch;
                        }
                    }
                    break;
                }
            }  
        } 
    } 
}

// Function that draws the W-E and N-S paths.
void drawPath(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell exitCells[4]) {
    int coordY;
    int coordX;
    
    // Draws the W-E path.
    for (int i = 0; i < MAP_WIDTH; i++) {
        //if (mvinch(i, 0) == '#') {
        if (mapChars[i][0] == '#') {
            coordY = i;
            break;
        }
    }
    int randNumX = (rand() % MAP_LENGTH / 2) + 20;

    for (int i = 0; i < randNumX; i++) {
        //mvaddch(coordY, i, '#');
        mapChars[coordY][i] = '#';

        if (i == (randNumX - 1)) {
            coordX = i;
        }
    }
    
    if (exitCells[1].y > coordY) {
        for (int i = coordY; i <= exitCells[1].y; i++) {
            //mvaddch(i, coordX, '#');
            mapChars[i][coordX] = '#';

            if (i == exitCells[1].y) {
                coordY = i;
                break;
            }
        }
    }
    else if (exitCells[1].y < coordY) {
        for (int i = coordY; i >= exitCells[1].y; i--) {
            //mvaddch(i, coordX, '#');
            mapChars[i][coordX] = '#';

            if (i == exitCells[1].y) {
                coordY = i;
                break;
            }
        }
    }
    
    for (int i = coordX; i < exitCells[1].x; i++) {
        //mvaddch(coordY, i, '#');
        mapChars[coordY][i] = '#';
    }

    // Draws the N-S path.
    for (int i = 0; i < MAP_LENGTH; i++) {
        //if (mvinch(0, i) == '#') {
        if (mapChars[0][i] == '#') {
            coordX = i;
            break;
        }
    }
    int randNumY = (rand() % MAP_WIDTH / 2) + 5;

    for (int i = 0; i < randNumY; i++) {
        //mvaddch(i, coordX, '#');
        mapChars[i][coordX] = '#';

        if (i == (randNumY - 1)) {
            coordY = i;
        }
    }
    
    if (exitCells[0].x > coordX) {
        for (int i = coordX; i <= exitCells[0].x; i++) {
            //mvaddch(coordY, i, '#');
            mapChars[coordY][i] = '#';

            if (i == exitCells[0].x) {
                coordX = i;
                break;
            }
        }
    }
    else if (exitCells[0].x < coordX) {
        for (int i = coordX; i >= exitCells[0].x; i--) {
            //mvaddch(coordY, i, '#');
            mapChars[coordY][i] = '#';

            if (i == exitCells[0].x) {
                coordX = i;
                break;
            }
        }
    }
    
    for (int i = coordY; i < exitCells[0].y; i++) {
        //mvaddch(i, coordX, '#');
        mapChars[i][coordX] = '#';
    }
}

// Carries out the growth algorithm for each region.
void growth_algorithm(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell seedCells[], int size) {
    expandRegion(mapChars, seedCells, size);

    // Extrapolates region to entire map after expanding the region of each seed. 
    for (int i = 1; i < MAP_WIDTH; i++) {
        for (int j = 1; j < MAP_LENGTH; j++) {
            for (int k = 0; k < size; k++) {
                //if (mvinch(i, j) == seedCells[k].biomeType) {
                if (mapChars[i][j] == seedCells[k].biomeType) {
                    seedCells[k].x = j;
                    seedCells[k].y = i;
                    expandRegion(mapChars, seedCells, size);
                }
            }
        }
    }
}

// Implements the growth algorithm for a random region.
void expandRegion(char mapChars[MAP_WIDTH][MAP_LENGTH], Cell seedCells[], int size) {
    int num = 0;

    // Assume neighbors is defined and valid
    int neighborsSize = sizeof(neighbors) / sizeof(neighbors[0]);

    // Expands seed region for each seed.
    while (num < size) { // Use 'size' instead of hard-coded value
        for (int i = 0; i < neighborsSize; i++) {
            int randNeighborIndex = rand() % neighborsSize;
            int newX = seedCells[num].x + neighbors[randNeighborIndex][0];
            int newY = seedCells[num].y + neighbors[randNeighborIndex][1];

            // Ensure newX and newY are within the bounds of the map
            if (newX >= 0 && newX < MAP_LENGTH && newY >= 0 && newY < MAP_WIDTH) {
                if (mapChars[newY][newX] == ' ') { // Check for empty space instead of '\0'
                    mapChars[newY][newX] = seedCells[num].biomeType;

                    // Optionally, update the seed cell's position if needed
                    // seedCells[num].x = newX;
                    // seedCells[num].y = newY;
                }
                else if (mapChars[newY][newX] == seedCells[num].biomeType) {
                    continue;
                }
                else {
                    break;
                }
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
void generate_borders(char mapChars[MAP_WIDTH][MAP_LENGTH], char ch, Cell exitCells[4], char direction, Cell exitCellsPrev[4]) {
    /* Draws borders.
    mvhline(0, 0, ch, MAP_LENGTH);
    mvhline(MAP_WIDTH, 0, ch, MAP_LENGTH);
    mvvline(0, 0, ch, MAP_WIDTH);
    mvvline(0, MAP_LENGTH, ch, MAP_WIDTH);
    */

   // Store borders in the mapChars array.
    for (int i = 0; i < MAP_LENGTH; i++) {
        mapChars[0][i] = ch; // Top border
        mapChars[MAP_WIDTH - 1][i] = ch; // Bottom border
    }
    for (int i = 0; i < MAP_WIDTH; i++) {
        mapChars[i][0] = ch; // Left border
        mapChars[i][MAP_LENGTH - 1] = ch; // Right border
    }

    int exitRandN = (rand() % (MAP_LENGTH - 20)) + 10;
    int exitRandS = (rand() % (MAP_LENGTH - 20)) + 10;
    int exitRandE = (rand() % (MAP_WIDTH / 2)) + 5;
    int exitRandW = (rand() % (MAP_WIDTH / 2)) + 5;

    if (direction == 'n') {
        exitRandS = exitCellsPrev[2].x;
    }
    else if (direction == 's') {
        exitRandN = exitCellsPrev[0].x;
    }
    else if (direction == 'e') {
        exitRandW = exitCellsPrev[1].y;
    }
    else if (direction == 'w') {
        exitRandE = exitCellsPrev[3].y;
    }

    // Draws exit points at borders.
    //mvaddch(0, exitRandN, '#');
    mapChars[0][exitRandN] = '#';
    //mvaddch(MAP_WIDTH, exitRandS, '#');
    mapChars[MAP_WIDTH - 1][exitRandS] = '#';
    //mvaddch(exitRandE, MAP_LENGTH, '#');
    mapChars[exitRandE][MAP_LENGTH - 1] = '#';
    //mvaddch(exitRandW, 0, '#');
    mapChars[exitRandW][0] = '#';

    exitCells[0].x = exitRandS;     // South gate.
    exitCells[0].y = MAP_WIDTH;         
    exitCells[0].biomeType = '#';

    exitCells[1].x = MAP_LENGTH;        // East gate.
    exitCells[1].y = exitRandE;     
    exitCells[1].biomeType = '#';

    exitCells[2].x = exitRandN;     // North gate.
    exitCells[2].y = 0;     
    exitCells[2].biomeType = '#';

    exitCells[3].x = 0;              // West gate.
    exitCells[3].y = exitRandW;     
    exitCells[3].biomeType = '#';
}

void printColorMap(char mapChars[MAP_WIDTH][MAP_LENGTH]) {
    clear(); // Clears the screen

    for(int i = 0; i < MAP_WIDTH; i++) {
        for(int j = 0; j < MAP_LENGTH; j++) {
            move(i + 1, j); // Move cursor to position
            switch(mapChars[i][j]) {
                case '%': attron(COLOR_PAIR(CP_GREY)); break;
                case '~': attron(COLOR_PAIR(CP_BLUE)); break;
                case '.': attron(COLOR_PAIR(CP_GREEN)); break;
                case ':': attron(COLOR_PAIR(CP_DARK_GREEN)); break;
                case '#': attron(COLOR_PAIR(CP_BRIGHT_YELLOW)); break;
                case '^': attron(COLOR_PAIR(CP_BROWN)); break;
                case '@': attron(COLOR_PAIR(CP_RED)); break;
                case 'M': attron(COLOR_PAIR(CP_BRIGHT_BLUE)); break;
                case 'C': attron(COLOR_PAIR(CP_BRIGHT_RED)); break;
                case 'h': attron(COLOR_PAIR(CP_ORANGE)); break;
                case 'r': attron(COLOR_PAIR(CP_PURPLE)); break;
                case 'p': attron(COLOR_PAIR(CP_CREAM)); break;
                case 'w': attron(COLOR_PAIR(CP_PINK)); break;
                case 's': attron(COLOR_PAIR(CP_YELLOW)); break;
                case 'e': attron(COLOR_PAIR(CP_TURQUOISE)); break;
                default: attron(COLOR_PAIR(0)); // Default color
            }
            addch(mapChars[i][j]);
            attroff(COLOR_PAIR(0)); // Turn off the color for the default case
        }
    }

    refresh(); // Refresh the screen to show the changes
}

// Insert a new element into the priority queue
void insert(struct PriorityQueue* pq, Cell data) {
    if (pq->size == pq->capacity) {
        return;
    }
    pq->size++;
    int i = pq->size - 1;
    pq->heap[i].data = data;
    heapifyUp(pq, i);
}

// Swap two priority queue nodes
void swap2(struct PQNode *a, struct PQNode *b) {
    struct PQNode temp = *a;
    *a = *b;
    *b = temp;
}

// Maintain heap property while inserting an element
void heapifyUp(struct PriorityQueue* pq, int index) {
    int parent = (index - 1) / 2;
    while (index > 0 && pq->heap[parent].data.sequenceNumber > pq->heap[index].data.sequenceNumber) {
        swap2(&pq->heap[parent], &pq->heap[index]);
        index = parent;
        parent = (index - 1) / 2;
    }
}

// Maintain heap property while extracting an element
void heapifyDown(struct PriorityQueue* pq, int index) {
    int left = 2 * index + 1;
    int right = 2 * index + 2;
    int smallest = index;
    if (left < pq->size && pq->heap[left].data.sequenceNumber < pq->heap[index].data.sequenceNumber)
        smallest = left;
    if (right < pq->size && pq->heap[right].data.sequenceNumber < pq->heap[smallest].data.sequenceNumber)
        smallest = right;
    if (smallest != index) {
        swap2(&pq->heap[index], &pq->heap[smallest]);
        heapifyDown(pq, smallest);
    }
}

// Extract the minimum element from the priority queue
Cell extractMin(struct PriorityQueue* pq) {
    if (pq->size <= 0) {
        Cell nullChar = {0}; 
        return nullChar;
    }
    if (pq->size == 1) {
        pq->size--;
        return pq->heap[0].data;
    }
    Cell root = pq->heap[0].data;
    pq->heap[0] = pq->heap[pq->size - 1];
    pq->size--;
    heapifyDown(pq, 0);
    return root;
}

void initColorPairs() {
    start_color();

    // Initialize color pairs with 256-color codes.
    init_pair(CP_GREY, 8, COLOR_BLACK);
    init_pair(CP_BLUE, 33, COLOR_BLACK);
    init_pair(CP_GREEN, 46, COLOR_BLACK);
    init_pair(CP_DARK_GREEN, 22, COLOR_BLACK);
    init_pair(CP_BRIGHT_YELLOW, 229, COLOR_BLACK);
    init_pair(CP_BROWN, 94, COLOR_BLACK);
    init_pair(CP_RED, 196, COLOR_BLACK);
    init_pair(CP_BRIGHT_BLUE, 117, COLOR_BLACK);
    init_pair(CP_BRIGHT_RED, 203, COLOR_BLACK);
    init_pair(CP_ORANGE, 202, COLOR_BLACK);
    init_pair(CP_PURPLE, 55, COLOR_BLACK);
    init_pair(CP_PINK, 199, COLOR_BLACK);
    init_pair(CP_YELLOW, 11, COLOR_BLACK);
    init_pair(CP_CREAM, 193, COLOR_BLACK);
    init_pair(CP_TURQUOISE, 49, COLOR_BLACK);
}

int determineColorPair(char biomeType) {
    switch(biomeType) {
        case '%': return CP_GREY;
        case '~': return CP_BLUE;
        case '.': return CP_GREEN;
        case ':': return CP_DARK_GREEN;
        case '#': return CP_BRIGHT_YELLOW;
        case '^': return CP_BROWN;
        case '@': return CP_RED;
        case 'M': return CP_BRIGHT_BLUE;
        case 'C': return CP_BRIGHT_RED;
        case 'h': return CP_ORANGE;
        case 'r': return CP_PURPLE;
        case 'p': return CP_CREAM;
        case 'w': return CP_PINK;
        case 's': return CP_YELLOW;
        case 'e': return CP_TURQUOISE;
        default:  return 0; // Default color
    }
}