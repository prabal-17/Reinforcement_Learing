import pygame
import neat
from ball import Ball
from paddle import Paddle
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Create ball and paddles
ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 10, WHITE, 5, 5)
paddle_left = Paddle(20, SCREEN_HEIGHT // 2 - 60, 10, 120, WHITE, 7)
paddle_right = Paddle(SCREEN_WIDTH - 30, SCREEN_HEIGHT // 2 - 60, 10, 120, WHITE, 7)

# Score variables
left_score = 0
right_score = 0

# Fonts for displaying score and AI label
font = pygame.font.Font(None, 74)
ai_font = pygame.font.Font(None, 30)

# Initialize the population and create the configuration
config_path = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

# Initialize generation counter
gen = 0  # Generation counter

# Define the fitness function for NEAT
def eval_genomes(genomes, config):
    global gen
    gen += 1
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        left_score = 0
        right_score = 0
        ball.x, ball.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        ball.speed_x, ball.speed_y = 5, 5

        # Run the game for a set time (simulation steps per genome)
        for _ in range(1000):
            screen.fill(BLACK)

            # Process events to ensure key inputs are handled
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # Handle user input for the left paddle (Player-controlled)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] and paddle_left.y > 0:  # W key for up
                paddle_left.move("up", SCREEN_HEIGHT)
            if keys[pygame.K_s] and paddle_left.y < SCREEN_HEIGHT - paddle_left.height:  # S key for down
                paddle_left.move("down", SCREEN_HEIGHT)

            # Handle paddle movement using the neural network for the right paddle (AI-controlled)
            output = net.activate((ball.x, ball.y, paddle_right.y))  # Ball position and right paddle position as inputs

            # The output controls right paddle's movement (up or down)
            if output[0] > 0:
                paddle_right.move("down", SCREEN_HEIGHT)
            else:
                paddle_right.move("up", SCREEN_HEIGHT)

            # Move the ball and check for collisions
            ball.move(SCREEN_WIDTH, SCREEN_HEIGHT)
            ball.check_collision(paddle_left)
            ball.check_collision(paddle_right)

            # Check for scoring
            if ball.x < 0:  # Left player scores
                right_score += 1
                ball.x, ball.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                ball.speed_x *= -1  # Reset ball direction

            if ball.x > SCREEN_WIDTH:  # Right player scores
                left_score += 1
                ball.x, ball.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                ball.speed_x *= -1  # Reset ball direction

            # Draw everything
            ball.draw(screen)
            paddle_left.draw(screen)
            paddle_right.draw(screen)

            # Display the scores
            left_score_text = font.render(str(left_score), True, WHITE)
            right_score_text = font.render(str(right_score), True, WHITE)
            screen.blit(left_score_text, (SCREEN_WIDTH // 4 - left_score_text.get_width() // 2, 20))
            screen.blit(right_score_text, (SCREEN_WIDTH * 3 // 4 - right_score_text.get_width() // 2, 20))

            # Display "AI" label below right score
            ai_text = ai_font.render("AI", True, WHITE)
            screen.blit(ai_text, (SCREEN_WIDTH * 3 // 4 - ai_text.get_width() // 2, 100))

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)

        # The fitness is how well the AI did (right player score)
        genome.fitness = right_score

# Initialize the population
population = neat.Population(config)

# Run the NEAT algorithm
winner = population.run(eval_genomes, 50)  # Run for 50 generations

pygame.quit()
