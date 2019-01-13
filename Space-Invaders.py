# Import libraries
import pygame
import random
# Initialise the game engine
pygame.init()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        """Initial values for the Player object (Gun) including its image"""
        super().__init__()
        self.score = 0
        self.deltaX = 0

        # Sprite Dimensions
        self.width = 46
        self.height = 26

        # Create somewhere to put the sprite
        self.surface = pygame.Surface([self.width, self.height])

        # Make the surface transparent
        self.surface.fill(WHITE)
        self.surface.set_colorkey(WHITE)

        # Image of the player's gun
        self.image = pygame.image.load("player.gif").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.surface.get_rect()

        # Set initial position to the middle for the x and one player height between the bottom of screen and player
        self.rect.x = screenWidth//2
        self.rect.y = screenHeight-2*self.height

        # Create a group for player's bullets
        self.bulletGroup = pygame.sprite.Group()

        # Set Player speeds
        self.RIGHT_SPEED = 5
        self.LEFT_SPEED = -self.RIGHT_SPEED

        #Generate a bullet object
        self.shot = Bullet()

    def fire(self):
        """Make a bullet and add it to groups"""
        # If there are no bullets in the bullet group add 1
        if len(self.bulletGroup) == 0:

            # The x position of the bullet is half of width of the player width - self.shot.width/2
            # otherwise the bullet would start at the right pixel of the "barrel" of the gun
            self.shot.rect.x = self.rect.x + self.width/2- self.shot.width/2
            self.shot.rect.y = self.rect.y - self.shot.height

            # Add it to the bulletGroup and all sprites group
            self.bulletGroup.add(self.shot)
            game.allSprites.add(self.shot)

    def movePlayer(self):
            """Adjust the position of the player by its x delta"""
            self.rect.x += self.deltaX

            # If the position is off of the screen set the x pos to the left most or right most of the screen
            if self.rect.x < 0:
                self.rect.x = 0
            else:
                # Limit x so that the player does not go off the screen
                self.rect.x = min(self.rect.x, (screenWidth-self.width))

    def addScore(self, collision):
        """Increment the score based on which alien was hit"""
        #if collision.gridY == 5:
        if collision.gridY == 5:
            self.score += 10
        else:
            self.score += (5-collision.gridY)

        # Generate the score board
        game.scoreBoard = font.render("Score:" + str(self.score), True, WHITE)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, gridX, gridY):
        """Initial values for the Enemy object (Alien) including its image"""
        super().__init__()
        # Sprite Dimensions
        self.width = 45
        self.height = 26
        self.gap = 11

        # The horizontal movement of the aliens every half second
        self.xSpeed = (self.width+self.gap)//2
        # The downward movement of the aliens every time they collide with a wall
        self.ySpeed = self.height

        # Create somewhere to put the sprite
        self.surface = pygame.Surface([self.width, self.height])

        # Make the surface transparent
        self.surface.fill(WHITE)
        self.surface.set_colorkey(WHITE)

        # Set the position of the object in the grid of Aliens
        # (0, 0) = top left Alien, (10, 4) = bottom right Alien (in this game)
        self.gridX = gridX
        self.gridY = gridY

        # Place holder variable
        self.collisions = None

        # Set the images of the alien based on its row (2 Images to animate the aliens)
        if self.gridY == 0:
            self.alienNames = ["alienA1.gif", "alienA2.gif"]
        elif gridY == 1:
            self.alienNames = ["alienB1.gif", "alienB2.gif"]
        elif gridY == 2:
            self.alienNames = ["alienB2.gif", "alienB1.gif"]
        elif gridY == 3:
            self.alienNames = ["alienC2.gif", "alienC1.gif"]
        elif gridY == 4:
            self.alienNames = ["alienC1.gif", "alienC2.gif"]
        elif gridY == 5:
            self.alienNames = ["bonusShip.gif"]

        self.image = pygame.image.load(self.alienNames[0]).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.surface.get_rect()
        self.setRect()
        self.canDropBomb = False

    def canDrop(self):
        """Calculate whether this alien can drop a bomb, depending on what other aliens are still alive"""
        self.canDropBomb = True

        # Bonus ships cannot drop bombs
        if self.gridY == 5:
            self.canDropBomb = False
        else:
            for entity in game.enemyGroup:
                # If it is not the bottom alien in its column, it cannot drop a bomb
                if self.gridX == entity.gridX and self.gridY < entity.gridY and entity.gridY != 5:
                    self.canDropBomb = False

                # If an adjacent column has an alien more than 1 row lower than this one, this alien cannot drop a bomb
                elif abs(entity.gridX-self.gridX) == 1 and (entity.gridY-self.gridY) > 1:
                    self.canDropBomb = False

        # If it can still drop a bomb add this alien to bombers list
        if self.canDropBomb:
            game.bombers.append(self)

    def setRect(self):
        """Set where the object will be put on the screen based on grid position"""
        self.rect.x = (self.width+self.gap)+self.gridX*(self.width+self.gap)
        self.rect.y = (self.height+self.gap)+self.gridY*(self.height+self.gap)

    def moveSelf(self, imageNo = 0):
        """Change image to animate and adjust the position of alien"""
        # Swap the image to animate
        self.image = pygame.image.load(self.alienNames[imageNo]).convert()

        self.image.set_colorkey(BLACK)
        # Adjust position
        self.rect.x += self.xSpeed

    def bombCoords(self):
        return (self.rect.x+self.width//2), (self.rect.y+self.height)

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        """Set all initial values for the Bullet Object"""
        super().__init__()
        # Sprite Dimensions
        self.width = 2
        self.height = 15
        self.speed = 10

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, WHITE, [0, 0, self.width, self.height])

        self.rect = self.image.get_rect()

        self.collisions = False

    def moveBullet(self):
        """Adjust the bullet position and remove it from all groups after it goes of of the top of the screen"""
        # This "Bullet" could be a player bullet or an alien bomb
        self.rect.y -= self.speed
        if self.rect.y < 0 or self.rect.y > screenHeight+self.height:
            self.kill()

        # Get a list of aliens that collide with the bullet and delete them
        self.collisions = pygame.sprite.spritecollide(self, game.enemyGroup, True)

        if self.collisions:
            # Adjust the score and remove the bullet from all groups
            self.collide()
        else:
            # Has the bullet hit the bonus spaceship?
            self.collisions = pygame.sprite.spritecollide(self, game.bonusGroup, True)

            if self.collisions:
                # Adjust the score and remove the bullet from all groups
                self.collide()
            else:
                # Has a Bomb collided with the player?
                self.collisions = pygame.sprite.spritecollide(self, game.playerGroup, True)

                if self.collisions:
                    # Refresh display to show the collision
                    pygame.display.update()
                    # Generate menu to show player lost including their score
                    gameOver = Menu([["GAME OVER!", MENU_NONE],
                                    ["Your score was:" + str(player1.score), MENU_NONE],
                                    ["", MENU_NONE],
                                    ["Restart", MENU_RESTART],
                                    ["Quit", MENU_QUIT]])

                    # Run the gameOver menu
                    game.done = gameOver.run()

        # If a bomb and bullet collide, remove both from all groups
        pygame.sprite.groupcollide(player1.bulletGroup, game.bombGroup, True, True)

    def collide(self):
        """For every sprite that the bullet collided with, adjust player score accordingly"""
        for collision in self.collisions:
            # Adjust the players score
            player1.addScore(collision)

        # Remove Bullet sprite from all Groups
        self.kill()

class Bomb(Bullet):
    def __init__(self, x, y):
        """Set initial values for a Bomb based on the Bullet's values
           x, y are the centre bottom coordinates of the alien that is dropping the bomb"""
        super().__init__()

        # Set the new size for the sprite
        self.width = 5
        # Bombs move down the screen 1/4 the speed of a bullet
        self.speed = -self.speed//4

        # Re-size and change the colour of the Bomb so that it can be distinguished from the bullets
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        pygame.draw.rect(self.image, RED, [0, 0, self.width, self.height])

        self.rect = self.image.get_rect()

        # Calculate the top left coord of the bomb sprite
        # so that the centre of the bomb lines up with the centre of the alien
        self.rect.x = x-(self.width//2)
        self.rect.y = y

        # Add self to its required groups
        game.allSprites.add(self)
        game.bombGroup.add(self)

class Spaceship(Enemy):
    """Set initial values for the bonus ship based on Enemy for bonus points"""
    def __init__(self):
        super().__init__(0, 5)
        self.xSpeed = 2
        self.rect.x = -self.width
        self.rect.y = self.gap

class Wall(pygame.sprite.Sprite):
    """Wall that is used to detect when any enemy is at the edge of the screen"""
    def __init__(self):
        super().__init__()
        # Sprite dimensions
        self.width = 1
        self.height = screenHeight

        self.image = pygame.Surface([self.width, self.height])
        # The green is made transparent and the wall is never put on screen
        self.image.fill(GREEN)
        self.image.set_colorkey(GREEN)
        self.rect = self.image.get_rect()
        self.rect.y = 0

class Text():
    def __init__(self, text, centreX, y):
        """Initial values"""
        # RATIO is the width of each character divided by the height of the character so 1 would be a square.
        # For Courier font, this is approx. 1515/2500
        self.RATIO = 0.606
        self.label = text
        self.colour = WHITE
        self.height = fontSize
        self.labelLength = len(self.label)
        self.width = self.RATIO*self.height*self.labelLength

        # Calculate the X and Y positions of the top left of the text
        self.yPos = y
        self.xPos = centreX - self.width//2

        self.render()

    def render(self):
        """Render the text for display"""
        self.text = font.render(self.label, True, self.colour)

    def getXPos(self):
        return self.xPos

    def getYPos(self):
        return self.yPos

    def draw(self):
        """Place the text on the screen"""
        screen.blit(self.text, [self.xPos, self.yPos])

    def setColour(self, colour):
        """Change the text colour"""
        self.colour = colour
        # Text needs to be re-rendered so that the colour change takes effect
        self.render()

class Button(Text):
    def __init__(self, text, centreX, y):
        super().__init__(text, centreX, y)

    def onSelf(self, x, y):
        """Return True if the passed (x, y) is on the button"""
        return (x >= self.xPos and x <= (self.xPos+self.width) and y >= self.yPos and y <= (self.yPos+self.height))

    def colourChange(self, x, y):
        """Change the colour to blue if the (x, y) is on the button"""
        if self.onSelf(x, y):
            self.colour = BLUE
            self.render()
        else:
            self.colour = WHITE
            self.render()

class Menu():
    """Set a class for all possible menus by a 2d array "options" that contains the label an actions of the button"""
    def __init__(self, options):
        # Initialise lists
        self.pause = False
        # Text or button text seen by the user
        self.labels = []
        # Function of the menu item (MENU_NONE = nothing)
        self.actions = []
        # The y coordinate of the top of the menu item
        self.y = []
        # List of all text and button objects
        self.items = []

        # blockY = the top Y co-ordinate of the "block" of options
        self.blockY = (screenHeight//2-(len(options)*(fontSize+5))//2)

        for i in range(len(options)):
            # Add text or button text of item
            self.labels.append(options[i][0])
            # Add action of item (MENU_NONE = no actions)
            self.actions.append(options[i][1])
            # Calculate the y coordinate for the top of item (allow 5 pixels between items)
            self.y.append(self.blockY+(fontSize+5)*i)

            if self.actions[i] == MENU_NONE:
                # If no action related to item, create Text object for item
                self.items.append(Text(self.labels[i], screenWidth//2, self.y[i]))
                self.items[i].setColour(RED)
            else:
                # Else, create Button object for item
                self.items.append(Button(self.labels[i], screenWidth//2, self.y[i]))

    def drawAll(self, x, y):
        """Draw all menu items"""
        minX = screenWidth
        # Set minX to the lowest x value of all Menu items
        for i in range(len(self.items)):
            minX = min(minX, self.items[i].getXPos())

        pygame.draw.rect(screen, BLACK, [minX-10, self.blockY, (screenWidth-2*minX)+20, screenHeight-2*(self.blockY)])
        for i in range(len(self.items)):
            # If the object has an Action, it is a button so has a colourChange method
            if self.actions[i] != MENU_NONE:
                self.items[i].colourChange(x, y)

            self.items[i].draw()

    def run(self):
        """Program loop for Menu objects needed for menu interaction"""
        self.pause = True
        while self.pause:
            # Get mouse coordinates
            mousePos = pygame.mouse.get_pos()
            mouseX = mousePos[0]
            mouseY = mousePos[1]

            for event in pygame.event.get():
                # If User Clicked Close
                if event.type == pygame.QUIT:
                    # State we want to leave the game
                    self.pause = False
                    returnValue = True

                # If the user pressed the mouse button down
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    menuAction = self.whichButton(mouseX, mouseY)

                    # If the item that has been clicked has the action MENU_RESTART
                    if menuAction == MENU_RESTART:
                        game.resetGame()
                        self.pause = False
                        returnValue = False

                    # If the item that has been clicked has the action MENU_QUIT
                    elif menuAction == MENU_QUIT:
                        self.pause = False
                        returnValue = True

                    # If the item that has been clicked has the action MENU_RESUME
                    elif menuAction == MENU_RESUME:
                        self.pause = False
                        returnValue = False

            self.drawAll(mouseX, mouseY)

            pygame.display.update()
            clock.tick(FPS)

        #Return True of False to dictate whether to exit the game or not
        return returnValue

    def whichButton(self, x, y):
        """Calculate which button was pressed and return the action that needs to run"""
        # Set returnValue for when (x, y) is not on any button
        returnValue = MENU_NONE
        for i in range(len(self.items)):
            # If the item has a MENU_NONE action it is text so
            if self.actions[i] != MENU_NONE:
                if self.items[i].onSelf(x, y):
                    returnValue = self.actions[i]

        return returnValue

class GameLoop():
    """Main program Loop"""
    def __init__(self):
        # Start a frame counter
        self.frame = 1
        # Create an empty list to contain Enemy objects (aliens)
        self.enemyObjects = []

        # Create all Group objects
        self.allSprites = pygame.sprite.Group()
        self.enemyGroup = pygame.sprite.Group()
        self.playerGroup = pygame.sprite.Group()
        self.wallGroup = pygame.sprite.Group()
        self.bonusGroup = pygame.sprite.Group()
        self.bombGroup = pygame.sprite.Group()

        # Create Wall objects and set their x positions to be the edges of the screen
        self.rightWall = Wall()
        self.rightWall.rect.x = screenWidth
        self.leftWall = Wall()
        self.leftWall.rect.x = 0

        # Add Wall objects to their group
        # But not to allSprites so that they are never drawn
        self.wallGroup.add(self.leftWall)
        self.wallGroup.add(self.rightWall)

        # Make object of the ship for bonus points
        self.bonusShip = Spaceship()

        # First bomb will be 2 seconds after the start of the game
        self.bombTimer = 2

        # Set place holder variables
        self.scoreBoard = font.render("Score:" + "0", True, WHITE)
        self.done = None
        self.lowestAlienY = 0
        self.wallCollisions = None

        # Place holders for alien objects that can bomb, bombs and the x, y positions of the bomber
        self.bombers = []
        self.bombs = []
        self.bomberX, self.bomberY = 0, 0

    def resetGame(self):
        """Reinitialise the game by rebuilding Groups"""
        # Empty all of the groups and lists
        self.enemyGroup.empty()
        self.allSprites.empty()
        self.playerGroup.empty()
        self.bombGroup.empty()
        player1.bulletGroup.empty()
        self.bombs = []

        # Reset the scoreBoard
        self.scoreBoard = font.render("Score:" + "0", True, WHITE)

        # Re-initialise the player (resets the score and position) and add it to its groups
        player1.__init__()
        self.allSprites.add(player1)
        self.playerGroup.add(player1)

        # Re-initialise all aliens (reset their position) and put them into their groups
        for i in range(55):
            self.enemyObjects[i].__init__(i%11, i//11)
            self.enemyGroup.add(self.enemyObjects[i])
            self.allSprites.add(self.enemyObjects[i])

        # Reset the bonus ship object so that it is just off of the screen
        self.bonusShip.rect.x = -self.bonusShip.width

        # Reset counters
        self.frame = 1
        self.second = 0
        self.bombTimer = 2

    def checkWallCollision(self):
        """Find enemies that have collided with a wall"""
        self.wallCollisions = pygame.sprite.groupcollide(game.wallGroup, game.enemyGroup, False ,False)

        # If there were any collisions
        if self.wallCollisions:
            # Find the lowest alien on the screen (highest y coordinate)
            # lowestAlienY will store the y coordinate of the bottom of the lowest alien (highest y) on the screen
            self.lowestAlienY = 0
            # For each remaining alien
            for enemy in self.enemyGroup:
                if enemy.gridY != 5:
                    # Move the alien down
                    enemy.rect.y += enemy.ySpeed
                    # Reverse the horizontal direction
                    enemy.xSpeed *= -1
                    # Undo previous horizontal movement which caused collision with wall
                    enemy.rect.x += enemy.xSpeed

                    # If current alien is lower than previous lowest, record its bottom y position
                    self.lowestAlienY = max(self.lowestAlienY, enemy.rect.y+enemy.height)

            # If lowest alien has reached the player
            if self.lowestAlienY >= player1.rect.y:
                # Re-draw all sprites before displaying menu
                screen.fill(BLACK)
                self.allSprites.draw(screen)

                # Generate menu to show player lost including their score
                gameOver = Menu([["GAME OVER!", MENU_NONE],
                                 ["Your score was:" + str(player1.score), MENU_NONE],
                                 ["", MENU_NONE],
                                 ["Restart", MENU_RESTART],
                                 ["Quit", MENU_QUIT]])

                # Run the gameOver menu
                self.done = gameOver.run()

    def run(self):
        self.done = startMenu.run()

        while not self.done:
            """Main Event Loop"""
            # User Did Something
            for event in pygame.event.get():
                # If User Clicked Close
                if event.type == pygame.QUIT:
                    # State we want to leave the game
                    self.done = True

                # If user pressed a key Down
                elif event.type == pygame.KEYDOWN:
                    # If the key was the right arrow key set player move right
                    if event.key == pygame.K_RIGHT:
                        player1.deltaX = player1.RIGHT_SPEED

                    # If the key was the left arrow key set player move left
                    elif event.key == pygame.K_LEFT:
                        player1.deltaX = player1.LEFT_SPEED

                    # If the key was a space, fire!
                    elif event.key == pygame.K_SPACE:
                        player1.fire()

                    # If the key was escape run the pause menu
                    elif event.key == pygame.K_ESCAPE:
                        self.done = pauseMenu.run()

                # If user released a key
                elif event.type == pygame.KEYUP:
                    # If the key was the right arrow (when the player is moving right) stop the player from moving
                    if event.key == pygame.K_RIGHT and player1.deltaX == player1.RIGHT_SPEED:
                        player1.deltaX = 0

                    # If the key was the left arrow (when the player is moving left) stop the player from moving
                    elif event.key == pygame.K_LEFT and player1.deltaX == player1.LEFT_SPEED:
                        player1.deltaX = 0

            # Game Logic should go here
            # Increment frame counter every frame
            self.frame += 1
            if self.frame > FPS:
                """Every second reset the frame counter, increment second counter and decrement the bomb counter"""
                self.frame = 1
                self.second += 1
                self.bombTimer -= 1

                # If it is time to drop a bomb
                if self.bombTimer == 0:
                    # Check which enemies are allowed to drop bombs
                    # This will build the self.bombers list
                    for a in self.enemyGroup:
                        a.canDrop()

                    # Get the bottom centre x, y Pos of a random alien from self.bombers
                    self.bomberX, self.bomberY = self.bombers[random.randrange(len(self.bombers))].bombCoords()

                    # add a Bomb object to the self.bombs list
                    self.bombs.append(Bomb(self.bomberX, self.bomberY))
                    # Next bomb in 1 second
                    self.bombTimer = 1

            if self.second%20 == 5:
                """Send a bonus ship every 20 seconds starting 5 seconds into the game"""
                # Reset the position of the spaceship and add it to its groups.
                self.bonusShip.rect.x = -self.bonusShip.width
                self.bonusGroup.add(self.bonusShip)
                self.allSprites.add(self.bonusShip)

            # Adjust the position of all players
            for player in game.playerGroup:
                player.movePlayer()

            # Adjust the position of all bullets
            for bullet in player1.bulletGroup:
                bullet.moveBullet()

            # Move every frame to make smoother animation than the aliens
            self.bonusShip.moveSelf()

            # Adjust the position of all aliens every half second
            if self.frame == FPS//2: # Will be true on 0.5s, 1.5s, 2.5s etc.
                self.bombers = []
                for enemy in game.enemyGroup:
                    # Move alien and display its first image
                    enemy.moveSelf()

                # Check if aliens have collided with the wall
                self.checkWallCollision()

            elif self.frame == FPS: # Will be true on 1s, 2s, 3s etc.
                self.bombers = []
                for enemy in game.enemyGroup:
                    # Move alien and display its second image
                    enemy.moveSelf(1)

                # Check if aliens have collided with the wall
                self.checkWallCollision()

            # Update position off all bombs every frame for smooth motion
            for bomb in self.bombGroup:
                bomb.moveBullet()

            # Set the background of scene
            screen.fill(BLACK)

            # Other drawing code goes here
            # Draw everything
            self.allSprites.draw(screen)
            screen.blit(self.scoreBoard, [0, screenHeight-fontSize])

            # If there is nothing in the enemy group display the you win menu
            if not game.enemyGroup:
                win = Menu([["Congratulations, YOU WIN!!!!", MENU_NONE],
                        ["Your score was: " + str(player1.score), MENU_NONE],
                        ["", MENU_NONE],
                        ["Play Again", MENU_RESTART],
                        ["Quit", MENU_QUIT]])
                self.done = win.run()

            # Update the screen with what has been drawn
            pygame.display.update()
            # Limit to FPS refreshes per second
            clock.tick(FPS)

        # Shut down the game engine
        pygame.quit()

# Used to manage how fast the screen refreshes
clock = pygame.time.Clock()
FPS = 60

# Set the font of all text to Courier 25pt, Bold
fontSize = 25
font = pygame.font.SysFont("Courier", fontSize, True, False)

# Set the screen size
screenWidth = 800
screenHeight = 600
size = (screenWidth, screenHeight) # TODO Remove this line as size is not used
screen = pygame.display.set_mode((screenWidth, screenHeight))
# Set title bar
pygame.display.set_caption("Space Invaders")

# Define some colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define constants for menu operations
MENU_NONE = 0
MENU_QUIT = 1
MENU_RESTART = 2
MENU_RESUME = 3

# Make the GameLoop object
game = GameLoop()

# Make static Menu objects
# Menus containing variables (score) are defined directly before use
pauseMenu = Menu([["Pause Menu", MENU_NONE],
                  ["", MENU_NONE],
                  ["Resume", MENU_RESUME],
                  ["Restart", MENU_RESTART],
                  ["Quit", MENU_QUIT]])

startMenu = Menu([["Space Invaders", MENU_NONE],
                  ["", MENU_NONE],
                  ["Play", MENU_RESTART],
                  ["Quit", MENU_QUIT]])

# Create sprite group objects
game.enemyGroup = pygame.sprite.Group()

# Create player object
game.playerGroup = pygame.sprite.Group()
player1 = Player()

game.playerGroup.add(player1)
# Add player1 to allSprites list
game.allSprites.add(player1)

# Create Enemy objects
game.enemyObjects = []
# At the start of the game there are 5 rows of 11 aliens so 55 objects
for i in range(55):
    # i%11 will return a value from 0-10 to state the x coordinate in the grid of aliens ((0, 0) = top left)
    # i//11 will return the value of i/11 rounded down so will get the results 0-4
    # to get the y coordinate in the grid of aliens
    game.enemyObjects.append(Enemy(i%11, i//11))
    game.enemyGroup.add(game.enemyObjects[i])
    game.allSprites.add(game.enemyObjects[i])

# Running the game
game.run()
