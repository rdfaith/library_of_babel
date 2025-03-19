import pygame
import utils


class GameObject:
    def __init__(self, position: pygame.Vector2, image: pygame.Surface) -> None:
        self.image = image
        self.rect = self.image.get_rect(topleft=position)

    def update(self, delta: float, objects: list):
        pass

    def draw(self, screen):
        """Draw object on screen."""
        screen.blit(self.image, self.rect)
        #  Draw hit box, just for debugging
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


class MovingObject(GameObject):
    def __init__(self, position: pygame.Vector2, image: pygame.Surface, gravity: bool) -> None:
        super().__init__(position, image)
        self.speed_x = 100
        self.speed_y = 600
        self.velocity = pygame.math.Vector2(0.0, 0.0)
        self.gravity = gravity

    def does_collide(self, rect, objects: list):
        """Check if hit box collides with another object."""
        for o in objects:
            if rect.colliderect(o.rect):
                return True
        return False

    def is_grounded(self, objects: list):
        """Check if element is on the floor."""
        preview_rect = self.rect.move(0, 1)
        if self.does_collide(preview_rect, objects):
            return True
        else:
            return False

    def update(self, delta: float, objects: list):
        """update hit box and position depending on collision"""
        # x axis
        preview_rect_x = self.rect.move(self.velocity.x * delta + 1 if self.velocity.x > 0 else -1, 0)
        if not self.does_collide(preview_rect_x, objects):
            self.rect.x += self.velocity.x * delta

        # y axis
        if not self.is_grounded(objects):
            self.velocity.y += 50
        preview_rect_y = self.rect.move(0, self.velocity.y * delta)
        if not self.does_collide(preview_rect_y, objects):
            self.rect.move_ip(0, self.velocity.y * delta)
        else:
            self.velocity.y = 0


class Player(MovingObject):

    def update(self, delta: float, objects: list):
        # get player movement
        keys = pygame.key.get_pressed()

        # Move the player left/right based on the keys pressed
        if keys[pygame.K_a]:
            self.velocity.x = -self.speed_x  # Move left
        elif keys[pygame.K_d]:
            self.velocity.x = self.speed_x  # Move right
        else:
            self.velocity.x = 0

        # Move the player up based on keys pressed
        if keys[pygame.K_SPACE] and self.is_grounded(objects):  # and if is_grounded
            self.velocity.y = -self.speed_y

        super().update(delta, objects)
