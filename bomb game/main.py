from random import randint
import pygame

pygame.init()
pygame.font.init()

window = pygame.display.set_mode((800, 800))

events = {
    "mouse": {
        "c": False,
        "h": False,
        "p": {
            "x": 0,
            "y": 0
        }
    }
}

fps = 60

class Bomb:
    radius = 100
    def __init__(self):
        self.x = events['mouse']['p']['x']-30
        if events['mouse']['p']['y']-30 < window.get_height()/2:
            self.y = events['mouse']['p']['y']-30
        else:
            self.y = window.get_height()/2
        self.vel = 1
        self.img = [pygame.image.load("bomb.png"), pygame.image.load("explode.png")]
        self.radius = Bomb.radius
        self.explode = False
        self.exploded = False
        self.exploding = False
        self.explode_time = 1
        self.explode_timer = 0
    def draw(self):
        if self.explode:
            if self.y > window.get_height()-50:
                self.exploding = True
            if self.exploding:
                window.blit(pygame.transform.scale(self.img[1], (self.radius, self.radius)), (self.x, self.y))
                self.exploded = True
            else:
                window.blit(pygame.transform.scale(self.img[0], (50, 50)), (self.x, self.y))
                self.y += self.vel
                if not self.vel > 20:
                    self.vel += 0.5
        else:
            window.blit(pygame.transform.scale(self.img[0], (50, 50)), (self.x, self.y))
            self.x = events['mouse']['p']['x']-30
            if events['mouse']['p']['y']-30 < window.get_height()/2:
                self.y = events['mouse']['p']['y']-30
            
            if events['mouse']['c']:
                self.explode = True
    def get_pos(self):
        return [self.x, self.y]
    def is_exploded(self):
        return self.exploded
    def delete(self, index):
        self.explode_timer += 1
        if self.explode_time*10 < self.explode_timer:
            bombs.pop(index)
    def force_explode(self):
        self.exploding = True


class Box:
    scroll = window.get_height()/50-1
    layer_time = 1
    layer_timer = 0
    layer_time_increase_speed = 1
    layer = 0
    def __init__(self, x, layer):
        self.x = x
        self.img = pygame.image.load("box.png")
        self.layer = layer*50
        self.explode = False
        self.exploded = False
    def draw(self):
        window.blit(pygame.transform.scale(self.img, (50, 50)), (self.x*50, self.layer+(Box.scroll*50)))
    def should_explode(self, bomb_pos, bomb_exploded):
        if bomb_pos[0] < self.x*50+Bomb.radius and bomb_pos[0] > self.x*50 - Bomb.radius and bomb_pos[1] < self.layer+(Box.scroll*50+Bomb.radius) and bomb_pos[1] > self.layer+(Box.scroll*50) - Bomb.radius and not bomb_exploded:
            return True
        
bombs = []
boxes = []
generate_new_box_layer = True


def rnndia(min, max, iterations):
    array = []
    iteration = 0
    while iteration < iterations:
        n = randint(min, max)
        if not n in array:
            array.append(n)
            iteration += 1
    return array


def generate_box_layer(layer):
    ignored = rnndia(0, 16, 5)
    for i in range(16):
        if not i in ignored:
            boxes.append(Box(i, layer))


def draw():
    global bomb_index
    global bombs
    global generate_new_box_layer
    
    window.fill("white")
    if events['mouse']['c']:
        bombs.append(Bomb())
    
    if Box.layer_timer > Box.layer_time*150:
        generate_new_box_layer = True

    if generate_new_box_layer:
        Box.scroll -= 1
        generate_box_layer(Box.layer+1)
        generate_new_box_layer = False
        Box.layer_timer = 0
        Box.layer += 1
    
    bomb_index = 0
    
    for bomb in bombs:
        bomb.draw()
        if bomb.is_exploded():
            bomb.delete(bomb_index)

        bomb_index += 1
    
    bomb_index = 0
    box_index = 0
    
    for box in boxes:
        box.draw()
        bomb_index = 0
        for bomb in bombs:
            if box.should_explode(bomb.get_pos(), bomb.is_exploded()):
                boxes.pop(box_index)
                bombs[bomb_index].force_explode()
                
            bomb_index += 1
        box_index += 1
    
    Box.layer_timer += 1
    Box.layer_time -= Box.layer_time_increase_speed/(10**3.5)
    Bomb.radius += Box.layer_time_increase_speed/5

def main():
    global events
    
    run = True
    clock = pygame.time.Clock()
    while run:
        if events['mouse']['c']:
            events['mouse']['c'] = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEMOTION:
                events['mouse']['p']['x'] = pygame.mouse.get_pos()[0]
                events['mouse']['p']['y'] = pygame.mouse.get_pos()[1]
            if event.type == pygame.MOUSEBUTTONDOWN:
                events['mouse']['h'] = True
                events['mouse']['c'] = True
            if event.type == pygame.MOUSEBUTTONUP:
                events['mouse']['h'] = False
        
        draw()
        clock.tick(fps)
        pygame.display.flip()
                

main()
    
pygame.quit()