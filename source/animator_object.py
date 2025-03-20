import pygame as pg


class Animator:
    def __init__(self, sprite_sheet, frame_width, frame_height, num_frames, frame_rate):
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_rate = frame_rate  # How many frames per second
        self.current_frame = 0
        self.frames = self.load_frames()
        self.last_update = pg.time.get_ticks()

    def load_frames(self):
        """Extract frames from a sprite sheet."""
        frames = []
        for i in range(self.num_frames):
            frame = self.sprite_sheet.subsurface(pg.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            frames.append(frame)
        return frames

    def update(self):
        """Update animation frame based on time."""
        now = pg.time.get_ticks()
        if now - self.last_update > 1000 // self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % self.num_frames

    def get_frame(self, current_direction):
        """Return the current frame to be displayed."""
        if current_direction == 1:
            return self.frames[self.current_frame]
        else:
            return pg.transform.flip(self.frames[self.current_frame], True, False)