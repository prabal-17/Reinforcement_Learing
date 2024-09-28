import pygame
import random
import os
import neat
pygame.font.init()
WIN_WIDTH = 600
WIN_HEIGHT = 800

# Initialize Pygame and the display
pygame.init()
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Load images after display is initialized
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird" + str(x) + ".png"))) for x in range(1, 4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")).convert_alpha())
stat_font = pygame.font.SysFont("comicsans",50)
gen = 0

class Bird:
    """ Bird class """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5  # Animation time

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 0.5 * 3 * self.tick_count ** 2  # s=ut + 1/2 at^2

        # Terminal velocity
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # So when bird is nose diving, it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class Pipe():
    """
    represents a pipe object
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    """
    Represents the moving floor of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        Move floor so it looks like it is scrolling
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds,pipes, base,score):
    win.blit(bg_img, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = stat_font.render("Score"+str(score),1,(255,255,255))
    win.blit(text, (WIN_WIDTH -10 - text.get_width(), 10))

    
    for bird in birds:
        bird.draw(win)
    base.draw(win)  # Draw the moving base
    pygame.display.update()

def main(genomes, config):
    """
    The main game loop that evolves birds using the NEAT algorithm.
    :param genomes: list of genomes from NEAT algorithm
    :param config: NEAT configuration file
    :return: None
    """
    global win, gen
    gen += 1

    # Lists to store birds, neural networks, and genomes
    nets = []
    ge = []
    birds = []

    # Initialize birds, neural networks, and genomes for each genome passed
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))  # Starting position of the birds
        g.fitness = 0
        ge.append(g)

    base = Base(730)  # Position the base
    pipes = [Pipe(700)]  # Start with one pipe
    score = 0
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(30)  # Limit the frame rate to 30 fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Determine which pipe to use for neural network inputs
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            # No birds left, stop running
            run = False
            break

        # Move each bird, calculate fitness, and decide whether it should jump
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # Give each bird a small fitness boost for staying alive

            # Activate the neural network and pass relevant bird and pipe data
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # If the neural network output suggests a jump, make the bird jump
            if output[0] > 0.5:
                bird.jump()

        # Move the base
        base.move()

        # Create list to track pipes to remove
        rem = []
        add_pipe = False  # Initialize add_pipe to False before the loop

        # Move pipes and handle collision detection
        for pipe in pipes:
            for x in reversed(range(len(birds))):  # Loop in reverse
                bird = birds[x]
                if pipe.collide(bird, win):
                    ge[x].fitness -= 1  # Penalize fitness for a collision
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    continue  # Skip further processing for this bird since it has been removed

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True  # Set add_pipe to True when the bird passes a pipe

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)  # Mark pipe for removal if it goes off the screen

            pipe.move()  # Move the pipe

        # Add new pipe and increase score when a bird passes a pipe
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5  # Reward fitness for passing a pipe
            pipes.append(Pipe(600))  # Add a new pipe

        # Remove pipes that are off the screen
        for r in rem:
            pipes.remove(r)

        # Remove birds that hit the ground or fly too high
        for x in reversed(range(len(birds))):  # Loop in reverse
            bird = birds[x]
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Draw the current game state
        draw_window(win, birds, pipes, base, score)

    # pygame.quit()  # Quit the game when done

    # pygame.quit()
    

# main()

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
