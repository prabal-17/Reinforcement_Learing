import pygame

class Paddle:
    def __init__(self, x, y, width, height, color, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed

    def move(self, direction, screen_height):
        if direction == "up" and self.y > 0:
            self.y -= self.speed
        elif direction == "down" and self.y + self.height < screen_height:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
