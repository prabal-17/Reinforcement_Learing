import pygame

class Ball:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, screen_width, screen_height):
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off the top and bottom walls
        if self.y - self.radius <= 0 or self.y + self.radius >= screen_height:
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def check_collision(self, paddle):
        if (
            paddle.x < self.x < paddle.x + paddle.width and
            paddle.y < self.y < paddle.y + paddle.height
        ):
            # Ball hits the paddle
            self.speed_x *= -1  # Reverse horizontal direction

            # Determine hit position on paddle
            paddle_mid = paddle.y + paddle.height / 2
            distance_from_center = abs(self.y - paddle_mid)
            corner_zone = paddle.height / 3  # Upper and lower third as corners

            if distance_from_center > corner_zone:
                # Ball hit the corner: increase speed
                self.speed_y *= 1.2
                self.speed_x *= 1.1
            else:
                # Ball hit near the center: reset vertical alignment
                self.y = paddle_mid
