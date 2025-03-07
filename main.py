from time import sleep

import pygame
import classes

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.display.set_caption('Arkanoid')
pygame.init()

pygame.mixer.music.load('sounds/Soundtrack.mp3')
pygame.mixer.music.set_volume(0.075)
pygame.mixer.music.play(-1)

back = (200, 255, 255)  # background color
mw = pygame.display.set_mode((750, 500))  # main window
mw.fill(back)

# Constants
FPS = 30
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF

#Text objects
text_points = pygame.font.Font(None, 60)
text_level = pygame.font.Font(None, 60)

clock = pygame.time.Clock()

# platform coordinates
racket_x = 200
racket_y = 390
# ---------------------------------------------------------
# end game flag
game_over = False
game_pause = False
new_level = True

# create objects: ball and platform
game_table = classes.GameTable(mw, BLACK)
ball = classes.Ball('ball.png', 160, 200, 50, 50)
platform = classes.Platform('platform', racket_x, racket_y, 175, 35)
end_label = classes.Picture('end.png', 125, 125, 300, 300)
go_label = classes.Picture('go_sign.png', 0, 0, 500, 500)
ready = classes.Picture('ready.png', 0, 0, 500, 500)

gun_ability = classes.Gun('gun_button0', 'bullet', mw, 10, platform)
shield_ability = classes.Shield('shield_button0', 'platform_shield0', mw, 15, platform)
heal_ability = classes.Heal('heal_button0', mw, 20, platform)
help_button = classes.InterfaceButton('help_button0', 'help', mw, 0, platform)
pause_button = classes.InterfaceButton('pause_button0', 'pause_screen', mw, 0, platform, x_icon = 565, x = 0, y = 0, width = 500, height = 500)

# create enemies
start_x = 5  # first enemy coords
start_y = 5
enemies = []  # enemies list
level_1 = open('level_1.txt')
raws_1 = level_1.read().split('\n')

bullets = []

# start game cycle
ready.draw(mw)
pygame.display.update()
sleep(2)
mw.fill(back)
go_label.draw(mw)
pygame.display.update()
sleep(2)
mw.fill(back)
time = pygame.time.get_ticks()

while not game_over:
    if not(game_pause):
        ball.fill(mw)
        platform.fill(mw)
        platform.check_health()
        gun_ability.fill(mw)
        shield_ability.fill(mw)
        heal_ability.fill(mw)
        help_button.fill(mw)
        help_button.IsAvailable(game_table)
        pause_button.IsAvailable(game_table)
        game_table.fill(mw)
        game_table.write_score(text_points, WHITE)
        game_table.write_level(text_level, WHITE)
        
        if new_level:
            for j in range(len(raws_1)):
                y_coord = start_y + (55 * j)  # shift every next raw on 55 px by axis y
                x_coord = start_x + (27.5 * j)  # and 27.5 by x
                
                for i in range(len(raws_1[j])):
                    if raws_1[j][i] == 'E':
                        enemy = classes.Enemy('enemy.png', x_coord, y_coord, 50, 50) 
                    elif raws_1[j][i] == 'A':
                        enemy = classes.ArmoredEnemy('armored_enemy.png', x_coord, y_coord, 50, 50)
                    elif raws_1[j][i] == 'S':
                        enemy = classes.ShooterEnemy('shooter_enemy.png', 'enemy_bullet.png', x_coord, y_coord, 50, 50)
                    enemies.append(enemy)  # add to list
                    x_coord += 55  # next enemy x coordinate
            new_level = False
        
        if not(gun_ability.shot):
            gun_ability.IsAvailable(game_table)
            
        if not(platform.shield):
            shield_ability.IsAvailable(game_table)
            
        heal_ability.IsAvailable(game_table)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        # -------------------------------------------
        # Check buttons and change move flags
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    platform.moving_right = True
                if event.key == pygame.K_LEFT:
                    platform.moving_left = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    platform.moving_right = False
                if event.key == pygame.K_LEFT:
                    platform.moving_left = False      
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                gun_ability.check_pressed(mouse_x, mouse_y)
                gun_ability.shoot(platform, game_table)
                pause_button.check_pressed(mouse_x, mouse_y)
                shield_ability.check_pressed(mouse_x, mouse_y)
                heal_ability.check_pressed(mouse_x, mouse_y)
                
                if pause_button.button_pressed:
                    game_pause = not game_pause
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                help_button.check_pressed(mouse_x, mouse_y)
            # -----------------------------------------
    # Moving objects
        platform.move()
        ball.move()
        gun_ability.move()
        shield_ability.activate_shield(platform, game_table)
        heal_ability.heal(platform, game_table)
    # check minimal y_coordinate
        if ball.rect.y > 440 or platform.lives == 0:
            enemies = []
            mw.fill(back)
            end_label.fill(mw)
            end_label.draw(mw)
            pygame.display.update()
            sleep(2)
            game_over = True
        elif len(enemies) == 0:
            new_level = True
            game_table.level += 1
            ball.rect.x, ball.rect.y = 160, 200
            gun_ability.rect.y = -55
    # ----------------------------------------
    # check if ball touch the platform and change direction:
        ball.check_hit(platform)
    # ----------------------------------------
    # draw enemies from the list
        for enemy in enemies:
            enemy.draw(mw)
    # ---------------------------------------
    # check if the ball has the same coordinates as enemy and killed him
            ball.kill_enemy(enemy)
            gun_ability.kill_enemy(enemy)
            if isinstance(enemy, classes.ShooterEnemy):
                enemy.fill_fireball(mw)
                enemy.shooting()
                enemy.move_fireball()
                enemy.draw_fireball(mw)
                enemy.check_hit(platform, mw)
                enemy.check_hit(ball, mw)

            enemy.check_death(mw, enemies, game_table)
    # draw platform and ball
        platform.draw(mw)
        ball.draw(mw)
        gun_ability.draw_icon()
        gun_ability.draw()
        shield_ability.draw_icon()
        heal_ability.draw_icon()
        help_button.draw_icon()
        help_button.draw_button()
        pause_button.draw_icon()
    # renew scene
        pygame.display.update()
        clock.tick(FPS)
    else:
        mw.fill(back)
        help_button.fill(mw)
        help_button.IsAvailable(game_table)
        pause_button.IsAvailable(game_table)
        game_table.fill(mw)
        game_table.write_score(text_points, WHITE)
        game_table.write_level(text_level, WHITE)
        pause_button.draw_button()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pause_button.check_pressed(mouse_x, mouse_y)
                if pause_button.button_pressed:
                    game_pause = not game_pause
                    pause_button.fill(mw)
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                help_button.check_pressed(mouse_x, mouse_y)
                
        help_button.draw_icon()
        help_button.draw_button()
        pause_button.draw_icon()
        pygame.display.update()
        clock.tick(FPS)

pygame.quit()