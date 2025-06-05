# card_game.py
Card game created in PyGame, complete with real-time hand comparison and shuffling

## Basic Rules
At the beginning of the game, each player receives 5 columns of cards.</br>
One by one, players draw a card from the deck and place it into one of their 5 columns, with the goal being to create the highest poker hand.</br>
Each player must ensure they have placed a card into each column before placing a further card in the column.</br>
Once all columns have 5 cards, each column is compared to the opponent's column and the player with the most amount of individual column wins is the victor.

## Features
### Card and Deck Creation
Each deck is created of 52 cards from a card class and shuffled. Each card is given an area of a larger image to be their card face.</br>
Pressing "Shuffle" recreates the deck every time and deals out the initial columns to the players.

### Hover Effects and Game Logic
The player's card is able to be dragged into their desired row with hover effects to help indicate which row is being chosen.</br>
Internal logic to check whether the card is allowed to be placed in the chosen row, and the card is returned if not.</br>
A real time comparison of all the rows is displayed on the left side of the game screen.</br>

### Final State and Winner Comparions
Game checks when all columns have been filled in and performs the final calculation to declare the winner
