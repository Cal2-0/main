import pygame
import os
import random
pygame.init()
pygame.font.init()
pygame.mixer.init()

WI, HE = 900, 500
WIN = pygame.display.set_mode((WI, HE))
pygame.display.set_caption('Shooter')
wh = (255, 255, 255)
bl = (0, 0, 0)

healthfont = pygame.font.SysFont('engravers MT', 40)
winfont = pygame.font.SysFont('engravers MT', 80)
controlfont = pygame.font.SysFont('engravers MT', 24)

yhit = pygame.USEREVENT + 1
rhit = pygame.USEREVENT + 2


x=random.choice(['1624.jpg','1700.jpg','1771.jpg','1666.jpg'])
space = pygame.transform.scale(pygame.image.load(os.path.join('Assets', x)), (WI, HE))
    
rh = 10
yh = 10

VEL = 5
BVEL = 7
FPS = 60
swi, she = 55, 40
BORDER = pygame.Rect(WI // 2 - 5, 0, 10, HE)

yel = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
ye = pygame.transform.rotate(pygame.transform.scale(yel, (swi, she)), 90)
red = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
re = pygame.transform.rotate(pygame.transform.scale(red, (swi, she)), 270)

a=pygame.mixer.Sound(os.path.join('Assets','Grenade+1.mp3'))
b=pygame.mixer.Sound(os.path.join('Assets','Gun+Silencer.mp3'))
c=pygame.mixer.Sound(os.path.join('Assets','sound.mp3'))
a.set_volume(0.125)  
b.set_volume(0.125)
c.set_volume(0.125)
def draw(red, yellow, rb, yb, rh, yh):
    WIN.blit(space, (0, 0))
    pygame.draw.rect(WIN, bl, BORDER)
    redtext = healthfont.render('Health --->' + str(rh), 1, wh)
    yetext = healthfont.render('Health --->' + str(yh), 1, wh)
    WIN.blit(redtext, (WI - redtext.get_width() - 10, 10))
    WIN.blit(yetext, (10, 10))
    WIN.blit(ye, (yellow.x, yellow.y))
    WIN.blit(re, (red.x, red.y))

    control_yellow = controlfont.render("Controls: W-A-S-D to move, R to shoot", 1, wh)
    control_red = controlfont.render("Controls: Arrow keys to move, L to shoot", 1, wh)
    WIN.blit(control_yellow, (10, HE - control_yellow.get_height() - 10))
    WIN.blit(control_red, (WI - control_red.get_width() - 10, HE - control_red.get_height() - 10))

    for bullet in rb:
        pygame.draw.rect(WIN, (255, 0, 0), bullet)
    for bullet in yb:
        pygame.draw.rect(WIN, (255, 255, 0), bullet)
    pygame.display.update()


def yem(key_pressed, yellow):
    if key_pressed[pygame.K_a] and yellow.x - VEL > 0:
        yellow.x -= VEL
    if key_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:
        yellow.x += VEL
    if key_pressed[pygame.K_w] and yellow.y - VEL > 0:
        yellow.y -= VEL
    if key_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HE - 15:
        yellow.y += VEL


def rem(key_pressed, red):
    if key_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:
        red.x -= VEL
    if key_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WI:
        red.x += VEL
    if key_pressed[pygame.K_UP] and red.y - VEL > 0:
        red.y -= VEL
    if key_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HE - 15:
        red.y += VEL


def handm(yb, rb, yellow, red):
    for bullet in yb:
        bullet.x += BVEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(rhit))
            yb.remove(bullet)
        elif bullet.x > WI:
            yb.remove(bullet)

    for bullet in rb:
        bullet.x -= BVEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(yhit))
            rb.remove(bullet)
        elif bullet.x < 0:
            rb.remove(bullet)


def drawwin(text, rh, yh):
    yy = winfont.render(text, 1, bl)
    WIN.blit(yy, (WI // 2 - yy.get_width() // 2, HE // 2 - yy.get_height() // 2))
    pygame.display.update()
    c.play()
    pygame.time.delay(5000)
    reset_game()


def reset_game():
    global rh, yh
    rh = 10
    yh = 10
    main(rh, yh)


def main(rh, yh):
    
    red = pygame.Rect(700, 250, swi, she)
    yellow = pygame.Rect(100, 250, swi, she)
    rb = []
    yb = []

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and len(yb) < 4:
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height // 2 - 2, 10, 5)
                    yb.append(bullet)
                    b.play()

                if event.key == pygame.K_l and len(rb) < 4:
                    bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                    rb.append(bullet)
                    b.play()
            if event.type == rhit:
                rh -= 1
                a.play()

            if event.type == yhit:
                yh -= 1
                a.play()
        win = ''
        if rh == 0:
            win = 'Yellow Wins!!'
        if yh == 0:
            win = 'Red Wins!!'
        if win != '':
            rb.clear()
            yb.clear()
            drawwin(win, rh, yh)
            break

        key_pressed = pygame.key.get_pressed()
        yem(key_pressed, yellow)
        rem(key_pressed, red)

        handm(yb, rb, yellow, red)
        draw(red, yellow, rb, yb, rh, yh)


if __name__ == '__main__':
    main(rh, yh)
