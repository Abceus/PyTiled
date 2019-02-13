class Animation:
    def __init__(self, frames=None):
        self.frames = frames if frames else []
        self.image = frames[-2]
        self.dt = 0
        # self.repeat = (len(times) == len(images))

    def scale(self, time_):
        s = sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        for fi in range(len(self.frames)):
            if fi % 2 == 1:
                self.frames[fi] = self.frames[fi]/s*time_

    def update_image(self, dt):
        self.dt += dt
        self.dt %= sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        tmp = 0
        i = 1
        while self.dt > tmp and i < len(self.frames):
            tmp += self.frames[i]
            i += 2
        self.image = self.frames[i-3]
