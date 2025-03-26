from source import pg


class Animation:
    def __init__(self, name, sprite_sheet, frame_width, frame_height, num_frames, frame_rate=10, freeze_on_last_frame=False):
        self.name = name
        self.sprite_sheet = sprite_sheet
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_frames = num_frames
        self.frame_rate = frame_rate
        self.freeze_on_last_frame = freeze_on_last_frame


class Animator:
    def __init__(self, animation):
        self.sprite_sheet = pg.image.load(animation.sprite_sheet).convert_alpha()
        self.frame_width = animation.frame_width
        self.frame_height = animation.frame_height
        self.num_frames = animation.num_frames
        self.frame_rate = animation.frame_rate
        self.current_animation = animation
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
        """Update animation frame based on time. If freeze_on_last_frame is activated, the animation does not loop."""
        now = pg.time.get_ticks()
        if now - self.last_update > 1000 // self.frame_rate:
            self.last_update = now
            if self.current_animation.freeze_on_last_frame:
                if self.current_frame < self.num_frames - 1:
                    self.current_frame += 1
            else:
                self.current_frame = (self.current_frame + 1) % self.num_frames

    def reset_animation(self):
        self.current_frame = 0

    def get_frame(self, current_direction = 1):
        """Return the current frame to be displayed."""
        if current_direction == 1:
            return self.frames[self.current_frame]
        else:
            return pg.transform.flip(self.frames[self.current_frame], True, False)
