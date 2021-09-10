import pygame
import sys
import traceback
from pygame.locals import *
import myplane
import enemy
import bullet
import supply

from random import *


pygame.init()
pygame.mixer.init()

bg_size = width, height = 450, 700
screen = pygame.display.set_mode(bg_size)   #设置界面大小
pygame.display.set_caption("飞机大战")   #打印界面

background = pygame.image.load("images/background.png").convert()

BLACK =(0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)




#  载入背景音乐

pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)

bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
button_sound = pygame.mixer.Sound("sound/button.wav")
button_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.2)
enemy3_flying_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_flying_sound.set_volume(0.2)

get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)

def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)
    
def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)

def inc_speed(target, speed):
    for each in target:
        if each.rect.top < -5:
            each.speed += speed
    


def main():
    pygame.mixer.music.play(-1)

    #生成我方飞机
    me1 = myplane.MyPlane(bg_size)
    me2 = myplane.MyPlane(bg_size)

 

    #生成敌方飞机

    
    enemies = pygame.sprite.Group()    #汇总，所有的敌机都放到组里边区

    #生成敌方小型飞机
    small_enemies = pygame.sprite.Group()  #
    add_small_enemies(small_enemies, enemies, 15) #函数，添加飞机,添加到 small_enemies, enemies, 添加15个

    #生成中型飞机
    mid_enemies = pygame.sprite.Group()  #
    add_mid_enemies(mid_enemies, enemies, 4)

    #生成大型飞机
    big_enemies = pygame.sprite.Group()  #
    add_big_enemies(big_enemies, enemies, 2)

    #判断是否已经增加敌机的血量
    inc_energy = True

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 17
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 17
    bullet3 = []
    bullet3_index = 0
    BULLET3_NUM = 17
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me1.rect.midtop))
        bullet2.append(bullet.Bullet1(me1.rect.midtop))
        bullet3.append(bullet.Bullet1(me1.rect.midtop))
        # 这里子弹初始化时，位置参数为 me1.rect.midtop
    # 不能同时发射子弹

    #### 判断双倍子弹的次数
    double_times = 0


    #中弹图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0


    #score

    score = 0
    score_font = pygame.font.Font("font/font.ttf", 36)



    #标志是否暂停游戏
    paused = False
    
    pause_nor_image = pygame.image.load("images/pause_nor.png").convert_alpha()
    pause_pressed_image = pygame.image.load("images/pause_pressed.png").convert_alpha()
    resume_nor_image = pygame.image.load("images/resume_nor.png").convert_alpha()
    resume_pressed_image = pygame.image.load("images/resume_pressed.png").convert_alpha()

    paused_rect = pause_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
    paused_image = pause_nor_image

    

    #设置难度级别
    level = 1
    delay_level = 500

    #全屏炸弹
    bomb_image = pygame.image.load("images/bomb.png").convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font("font/font.ttf", 48)
    bomb_num = 3



###这里有代码不理解
    #每30s发放一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size)
    SUPPLY_TIMER = USEREVENT
    pygame.time.set_timer(SUPPLY_TIMER, 30 * 1000)

    #超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    #标志是否使用超级子弹
    is_double_bullet = False

    # 解除我方无敌状态计时器
    INVINCIBLE_TIME = USEREVENT + 2

    #生命数量
    life_image = pygame.image.load("images/life.png").convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3

    #用于阻止重复打开记录文件
    recorded = False

    # 游戏结束画面
    gameover_font = pygame.font.Font("font/font.ttf", 48)
    again_image = pygame.image.load("images/again.png").convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load("images/gameover.png").convert_alpha()
    gameover_rect = gameover_image.get_rect()

    
    running = True

    clock = pygame.time.Clock()

    #用于切换图片
    switch_image = True

    #用于延时
    delay = 100
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                 if event.button == 1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIMER, 0) # 取消自定义事件
                        pygame.mixer.music.pause()  # 背景音乐
                        pygame.mixer.pause()  # 音效
                    else:
                        pygame.time.set_timer(SUPPLY_TIMER, 30 * 1000) # 取消自定义事件
                        pygame.mixer.music.unpause()  # 背景音乐
                        pygame.mixer.unpause()  # 音效
                        
            elif event.type == MOUSEMOTION:   # 有任何移动
                if paused_rect.collidepoint(event.pos):      #是否在范围之内
                    if paused:
                        pause_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        pause_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image

            elif event.type == KEYDOWN:         # 检测按键，清除所有敌人
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each. active = False

            elif event.type == INVINCIBLE_TIME:
                me1.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)
######这里代码不太好理解
            elif event.type == SUPPLY_TIMER:            ######这里代码不太好理解
                supply_sound.play()
                if choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            #响应事件
            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

        #根据用户的得分增加难度

        
        
        if level == 1 and score> 100000:
            level = 2
            upgrade_sound.play()
            
            #增加三架小型敌机、两家中型敌机、一架大型敌机
            add_small_enemies(small_enemies, enemies, 10)
            add_mid_enemies(mid_enemies, enemies, 5)
            add_big_enemies(big_enemies, enemies, 1)
            #提升小型敌机的速度，即修改类中speed
            inc_speed(small_enemies, 1)
        elif level == 2 and score > 300000:
            level = 3
            upgrade_sound.play()
            #增加三架小型敌机、两家中型敌机、一架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            #提升小型敌机的速度，即修改类中speed
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            upgrade_sound.play()
            #增加三架小型敌机、两家中型敌机、一架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            #提升小型敌机的速度，即修改类中speed
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            upgrade_sound.play()
            #增加三架小型敌机、两家中型敌机、一架大型敌机
            add_small_enemies(small_enemies, enemies, 10)
            add_mid_enemies(mid_enemies, enemies, 5)
            add_big_enemies(big_enemies, enemies, 2)
            #提升小型敌机的速度，即修改类中speed
            inc_speed(small_enemies, 2)
            inc_speed(mid_enemies, 1)
            inc_speed(big_enemies, 1)

        
        

            
        #这里背景一定要先写，不然背景会覆盖在飞机上面
        screen.blit(background,(0,0))
        #screen.blit(paused_image, paused_rect)
        
        if life_num and not paused:
            
            #键盘输入有两种方法，一种是keydown，一种是key模块
            #偶然触发的一般用第一种,多次连续出发的一般第二种

            #检测用户的键盘操作
            key_pressed = pygame.key.get_pressed()

            if key_pressed[K_w] or key_pressed[K_UP]:
                me1.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me1.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me1.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me1.moveRight()

            # 绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me1):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    else:
                        life_num += 1  # 把导弹换成生命
                    bomb_supply.active = False




            #绘制超级子弹补给
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me1):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000)
                    if double_times < 3:
                        double_times += 1
                    bullet_supply.active = False




            #发射子弹   注：不能让子弹同时发射出来，设定每5帧发射
            
            if not(delay % 5):               ##这里可能能加快子弹的发射速度，可作弊。
                                             ##注意，这里如果贸然加快的话，子弹的路径会变短
                bullet_sound.play()
                if double_times >= 5 and is_double_bullet:
                    bullet1[i].speed = 30
                    bullet2[i].speed = 30
                    bullet3[i].speed = 30
                    
                if double_times < 3 and level < 4:
                    if is_double_bullet:
                        bullet1[bullet1_index].reset((me1.rect.left + 15, me1.rect.top))
                        bullet1_index = (bullet1_index + 1) % BULLET1_NUM
                        bullet2[bullet2_index].reset((me1.rect.right - 15, me1.rect.top))
                        bullet2_index = (bullet2_index + 1) % BULLET2_NUM
                    else:
                        bullet1[bullet1_index].reset(me1.rect.midtop)
                        bullet1_index = (bullet1_index + 1) % BULLET1_NUM
                elif double_times == 3 and level < 4:
                    bullet1[bullet1_index].reset((me1.rect.left + 15, me1.rect.top))
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM
                    bullet2[bullet2_index].reset((me1.rect.right - 15, me1.rect.top))
                    bullet2_index = (bullet2_index + 1) % BULLET2_NUM
                elif level >= 4:
                    bullet1[bullet1_index].reset((me1.rect.left + 15, me1.rect.top))
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM
                    bullet2[bullet2_index].reset((me1.rect.right - 15, me1.rect.top))
                    bullet2_index = (bullet2_index + 1) % BULLET2_NUM
                    bullet1[bullet1_index].reset(me1.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM
                    if inc_energy:
                        for each in big_enemies:
                            each.energy = 30
                            enemy.BigEnemy.energy = 30
                        for each in mid_enemies:
                            each.energy = 15
                            enemy.MidEnemy.energy = 15
                        inc_energy = False
                        
                if level == 5:
                    if is_double_bullet:
                        bullet1[i].speed = 60
                        bullet2[i].speed = 60
                        bullet3[i].speed = 60
                    for i in range(BULLET1_NUM):
                        bullet1[i].speed = 30
                        bullet2[i].speed = 30
                        bullet3[i].speed = 30

            #检测子弹是否击中敌机

            for b in bullet1:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemy_hit:
                        b.active = False

                        # 其实这个地方可以省去if ， 给smallenermy 也加一个energy， 
                        for e in enemy_hit:    
                            if e in mid_enemies or e in big_enemies:   # 有血的飞机
                                e.energy -= 1
                                e.hit = True
                                if e.energy == 0:
                                    e.active = False
                            else:                    #小型飞机
                                e.active = False
            for b in bullet2:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemy_hit:
                        b.active = False

                        # 其实这个地方可以省去if ， 给smallenermy 也加一个energy， 
                        for e in enemy_hit:    
                            if e in mid_enemies or e in big_enemies:   # 有血的飞机
                                e.energy -= 1
                                e.hit = True
                                if e.energy == 0:
                                    e.active = False
                            else:                    #小型飞机
                                e.active = False
            


        

            #绘制大型敌机，这里要注意，要先绘制大型机，再小型机
            #不然小型机被盖在大型机下边

            
            #绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()
                    if each.hit == True:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:    
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)

                    #绘制血槽
                    pygame.draw.line(screen, BLACK,\
                                     (each.rect.left, each.rect.top - 5),\
                                     (each.rect.right, each.rect.top - 5),\
                                     2)
                    #当生命值大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                        
                    pygame.draw.line(screen, energy_color,\
                                     (each.rect.left, each.rect.top - 5),\
                                     (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),\
                                     2)

                        
                    #即将出现在画面中，播放音效
                    if each.rect.bottom == -50:
                        enemy3_flying_sound.play(-1)  #-1表示循环音效
                else:
                    #毁灭
                    if not(delay % 3):
                        if e3_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            enemy3_flying_sound.stop()
                            score += 10000
                            
                            each.reset()
                            
            #绘制中型敌机
            for each in mid_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)

                #绘制血槽
                    pygame.draw.line(screen, BLACK,\
                                     (each.rect.left, each.rect.top - 5),\
                                     (each.rect.right, each.rect.top - 5),\
                                     2)
                    #当生命值大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.MidEnemy.energy
                    enery_color = GREEN
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                        
                    pygame.draw.line(screen, energy_color,\
                                     (each.rect.left, each.rect.top - 5),\
                                     (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5),\
                                     2)
                else:
                    #毁灭
                    
                    if not(delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6000
                            each.reset()

            #绘制小型敌机

            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    #毁灭
                    
                    if not(delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 1000
                            each.reset()

            #检测我方飞机是否被撞,这个函数的方法在3里边
            enemies_down = pygame.sprite.spritecollide(me1, enemies, False, pygame.sprite.collide_mask)
            # 默认情况下以矩形区域作为检测
            if enemies_down and not me1.invincible:
                me1.active = False
                for e in enemies_down:
                    e.active = False



            #绘制我方飞机,还需要增加一个延时

            if me1.active:
                
                if switch_image:
                    
                    screen.blit(me1.image1, me1.rect)
                else:
                    screen.blit(me1.image2, me1.rect)
            else:
                #毁灭
                    
                    if not(delay % 3):
                        if me_destroy_index == 0:
                            me_down_sound.play()
                        screen.blit(me1.destroy_images[me_destroy_index], me1.rect)
                        me_destroy_index = (me_destroy_index + 1) % 4
                        if me_destroy_index == 0:
                            life_num -= 1
                            me1.reset()
                            pygame.time.set_timer(INVINCIBLE_TIME, 5 * 1000)



            # 绘制炸弹数量
            bomb_text = bomb_font.render(" *% d" % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (10 + bomb_rect.width, height - 10 - bomb_rect.height))


            # 绘制生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image,(width-100-((i)%3-1)*life_rect.width, height-10-(i//3+1) *life_rect.height))
        # 绘制游戏结束画面
        elif life_num == 0:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.time.set_timer(SUPPLY_TIMER,0)
            if not recorded:
                recorded = True
                # 读取历史最高得分
                with open("record.txt",'r') as f:
                    record_score = int(f.read())
                    
                if score > record_score:
                    with open("record.txt","w") as f:
                        f.write(str(score))
                

                
            # 绘制结束画面
            record_score_text = score_font.render("Best: %d" % record_score, True, WHITE)
            screen.blit(record_score_text, (50, 50))

            gameover_text1 = gameover_font.render("Your Score: ", True, WHITE)
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = \
                (width - gameover_text1_rect.width) // 2, height // 2
            screen.blit(gameover_text1, gameover_text1_rect)

            gameover_text2 = gameover_font.render(str(score), True, WHITE)
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = \
                (width - gameover_text2_rect.width) // 2, \
                gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect.left, again_rect.top = \
                (width - again_rect.width) // 2, \
                gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)

            gameover_rect.left, gameover_rect.top = \
                (width - again_rect.width) // 2, \
                again_rect.bottom + 10
            screen.blit(gameover_image, gameover_rect)

            # 检测用户的鼠标操作
            # 如果用户按下鼠标左键
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if again_rect.left < pos[0] < again_rect.right and \
                        again_rect.top < pos[1] < again_rect.bottom:
                    main()
                elif gameover_rect.left < pos[0] < gameover_rect.right and \
                        gameover_rect.top < pos[1] < gameover_rect.bottom:
                    pygame.quit()
                    sys.exit()


        #绘制等级
        if level == 1 and delay_level > 400:
            level_text = score_font.render("LEVEL 1", True, WHITE)
            screen.blit(level_text, (50, 50))
            delay_level -= 1
        elif level == 2 and delay_level > 300:
            level_text = score_font.render("LEVEL 2", True, WHITE)
            screen.blit(level_text, (50, 50))
            delay_level -= 1
        elif level == 3 and delay_level > 200:
            level_text = score_font.render("LEVEL 3", True, WHITE)
            screen.blit(level_text, (50, 50))
            delay_level -= 1
        elif level == 4 and delay_level > 100:
            level_text = score_font.render("LEVEL 4", True, WHITE)
            screen.blit(level_text, (50, 50))
            delay_level -= 1
        elif level == 5 and delay_level > 0:
            level_text = score_font.render("LEVEL 5", True, WHITE)
            screen.blit(level_text, (50, 50))
            delay_level -= 1
        
        score_text = score_font.render("Score : %s" % str(score), False, WHITE)
        screen.blit(score_text,(10, 5))

        #绘制暂停
                                
        screen.blit(paused_image, paused_rect)
        
        #切换图片
        # 这里delay  使飞机图片的切换得到延时
        if not(delay % 5):
            switch_image = not switch_image
        
        delay -= 1   # 每一次循环，delay会 -1
        
        if not delay: 
            delay = 100        # 如果delay 变为0 ，重新初始化
        pygame.display.flip()
        
        clock.tick(60)

    
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
