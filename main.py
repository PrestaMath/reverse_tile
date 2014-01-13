# -*- coding: utf8 -*-
import kivy
kivy.require('1.0.6') # replace with your current kivy version !
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from math import fabs
from copy import deepcopy
from functools import partial
from os import sep
import random


#todo : better locking, lock when it is flipping and when is computer turn
#todo : flip sound
#todo : show hint
#todo : check if resume game not faulty

#Window.size=(320,200)

TEXTURES = {}
TEXTURES['empty'] = Image(source="image%sempty.png" % sep).texture
for i in range(0,6):
    TEXTURES['black%i' % i] = Image(source="image%sblack%i.png" % (sep,i) ).texture
    TEXTURES['white%i' % i] = Image(source="image%swhite%i.png" % (sep,i) ).texture


def swap(s1, s2):
    return s2, s1

class tile(Image):
    current_flipping=0
    def __init__(self,**kwargs):
        self.rev_x = kwargs['rev_x']
        self.rev_y = kwargs['rev_y']
        self.caller_instance = kwargs['rev_caller']
        super(Image, self).__init__(**kwargs)
        self.toggle_texture(kwargs['rev_content'],' ')

    def on_touch_down(self,touch):
        if self.caller_instance.b_wait:
            return True
        
        if self.collide_point(*touch.pos):
            self.caller_instance.play(int(self.rev_x),int(self.rev_y))
            return True 

    def display_flipping(self,to_color):
        self.flip_state = 0
        if to_color == 'X':
            self.fip_seq=['white1','white2','white3','white4','white5','black5','black4','black3','black2','black1','black0']
        else:
            self.fip_seq=['black1','black2','black3','black4','black5','white5','white4','white3','white2','white1','white0']
        Clock.schedule_interval(self.my_callback, 0.05)
        tile.current_flipping +=1

    def my_callback(self,dt):
        if len(self.fip_seq) == self.flip_state:
            self.flip_state -=1
        self.texture = TEXTURES[self.fip_seq[self.flip_state]]

        self.flip_state += 1
        if len(self.fip_seq) == self.flip_state:
            tile.current_flipping -=1
            return False        #end the scheduling
        
            
    def toggle_texture(self,s_texture,s_previous_texture):
        if s_previous_texture == ' ':
            if s_texture == 'O':
                self.texture = TEXTURES['white0']
            elif s_texture =='X':
                self.texture = TEXTURES['black0']
            else:
                self.texture = TEXTURES['empty']
        else:                
            self.display_flipping(s_texture)

def divide_screen():
    x = Window.width
    y = Window.height
    
    if x>y:
        x,y = swap(x,y)

    grid_width = x
    menu_width = y-x
    return grid_width,menu_width


class Play_ground(Widget):
    b_wait = False
    
    end_of_impact =[]
    
    def __init__(self, **kwargs):
        super(Play_ground, self).__init__(**kwargs) #constructeur du parent
        self.caller_instance = kwargs['caller_instance']
        resume = self.caller_instance.config.get('section1', 'resume')
        if len(resume) == 64:
            self.resume = resume.replace('_',' ')
        else:
            self.resume = ''
        
        self.new_grid()
        
    def new_game(self,instance):
        self.resume = ''
        self.new_grid()

    def on_resize(width,height):
        pass

    def new_grid(self):
        grid_width,menu_width = divide_screen()
        
        # logic grid
        self.player_turn=0
        self.player0= 'O'
        self.player0_type='human'
        self.player1= 'X'
        self.player1_type='computer'
        
        self.player ='O'
        self.adversary ='X'
        
        self.grid = [[' ' for x in xrange(8)] for x in xrange(8)]

        if self.resume == '':
            self.grid[3][3]='O'
            self.grid[4][4]='O'
            self.grid[3][4]='X'
            self.grid[4][3]='X'
        else:
            idx = 0
            for y in range(0,8):
                for x in range(0,8):
                    self.grid[y][x]=self.resume[idx]
                    idx += 1
        self.previous_grid = deepcopy(self.grid)
        
        self.label_score = Label()
        self.display_score()
        
        
        # graphic grid
        self.clear_widgets()
        self.graphical_grid = GridLayout(cols=8,size=(grid_width,grid_width))  
        for y in range(0,8):
            for x in range(0,8):
                tiloun = tile(rev_x = x, rev_y =y, rev_caller = self,
                              rev_content = self.grid[x][y])
                self.graphical_grid.add_widget(tiloun)
        
        self.add_widget(self.graphical_grid)
        #control panel
        layout = BoxLayout(orientation='vertical',
                  x=grid_width,y=Window.height/2,width = menu_width            
                           ) #,width=40,pos_hint={'left':0.9})
        
        btn1 = Button(text='New')
        btn1.bind(on_press=self.new_game)
        

        self.difficulty = self.caller_instance.config.get('section1', 'difficulty')
        
        btn3 = Button(text=self.difficulty)
        
        btn3.bind(on_press=self.toggle_difficulty)

        layout.add_widget(Label(text='Powered by Kivy'))
        layout.add_widget(btn1)
        layout.add_widget(btn3)
        layout.add_widget(self.label_score)
        self.add_widget(layout)

        
    def toggle_difficulty(self,instance):
        if self.difficulty == 'easy':
            self.difficulty = 'hard'
            instance.text = 'hard'
        else:
            self.difficulty = 'easy'
            instance.text = 'easy'
        self.caller_instance.config.set('section1', 'difficulty', self.difficulty)
        self.caller_instance.config.write()                  
    def display(self):
        for child in self.graphical_grid.children:
            if self.grid[int(child.rev_x)][int(child.rev_y)] != self.previous_grid[int(child.rev_x)][int(child.rev_y)]:
                child.toggle_texture(self.grid[int(child.rev_x)][int(child.rev_y)],self.previous_grid[int(child.rev_x)][int(child.rev_y)])

    def possible_move(self,xm,ym,player,adversary):
        self.end_of_impact=[]
        '''
        array = [(x-1,y-1),(x,y-1),(x+1,y-1),
            (x-1,y),(x+1,y),
         (x-1,y+1),(x,y+1),(x+1,y+1),
         ]
         # then remove out of boundary
         '''

        for y in range(ym-1,ym+2):
            for x in range(xm-1,xm+2):
                if self.in_grid_boundary(x,y) == False:
                    continue
                if y==ym and x==xm:
                    continue
                #search for other player tile between new and old
                if self.grid[x][y]== adversary:
                    #test line
                    
                    vx=x-xm # get coef for x mauvais coef direct -1 -1
                    vy=y-ym # same for y
                    '''
                        vx = (y-ym)/(x-xm)
                        vy = ym - vx*xm
                    '''
                    if self.in_grid_boundary(x+vx,y+vy) == False:
                        #bad move
                        continue
                    
                        
                    if self.grid[x+vx][y+vy] == player:
                        #move is ok
                        self.end_of_impact.append((x+vx,y+vy,1))    #add impacted tiles number
                        continue
                    if self.grid[x+vx][y+vy] == ' ':
                         #bad move
                        continue
                    if self.grid[x+vx][y+vy] == adversary:
                        #search end of line
                        v=2
                        
                        while self.in_grid_boundary(x+vx*v,y+vy*v) and self.grid[x+vx*v][y+vy*v] == adversary :
                            v += 1
                        if self.in_grid_boundary(x+vx*v,y+vy*v) and self.grid[x+vx*v][y+vy*v] == player :
                            #move is ok
                            self.end_of_impact.append((x+vx*v,y+vy*v,v))
                            continue
        if not self.end_of_impact:
            return False
        return True

    def hint_grid(self):
        for y in range(0,8):
            for x in range(0,8):
                if self.grid[x][y] <>' ':
                    continue
                
    
    def in_grid_boundary(self,x,y):
        if x<0 or x>7 or y<0 or y>7:
            return False
        return True

    def reverse(self,x,y):
        
        self.previous_grid = deepcopy(self.grid)
        self.grid[x][y] = self.player
        
        for coord in self.end_of_impact:
            xe = coord[0]
            ye = coord[1]
            vx = x - xe
            vy = y - ye

            if vx <> 0 :
                vx = int(vx/fabs(vx))
            if vy <> 0 :
                vy = int(vy/fabs(vy))

            for n in range(0,8):
                xn = xe +n*vx
                yn = ye +n*vy
                if xn == x and yn ==y :
                    break
                self.grid[xn][yn] = self.player

        

        
    def display_score(self):
        score = {'O':0,'X':0,' ':0}
        for y in range(0,8):
            for x in range(0,8):
                score[self.grid[x][y]] += 1
        
        self.label_score.text='Score %i-%i' % ( score['O'],score['X'])
        
    # self.end_of_impact contains all impacts for currently tested move
    # self.end_of_impact is cleared for each tested move
    def calcul_impact_sum(self):
        impact_sum = 0 
        for coord in self.end_of_impact:
            impact_sum += coord[2]
        return impact_sum
    
    def get_possible_moves(self,player,adversary):       #may be use for hint, pass and end of game
        self.impact_depth = []
        moves = []
        for y in range(0,8):
            for x in range(0,8):
                if self.grid[x][y] <> ' ':
                    continue
                if self.possible_move(x,y,player,adversary):
                    impact = self.calcul_impact_sum()
                    moves.append((x,y))
                    self.impact_depth.append((x,y,impact))
        return moves

    def do_not_offer_corner(self,moves):
        # probleme position identique existant plusieurs fois
        # parcours et suppression en cours dans le meme tableau
        move_cop = deepcopy(moves)
        badpos = [(1,0),(1,1),(0,1),(6,0),(6,1),(7,1),(0,6),(1,6),(1,7),(6,6),(7,6),(6,7)]
        for move in moves:
            if move in badpos:
                move_cop.remove(move)
                
        if len(move_cop) == 0:      #if no choices left
            return moves
        
        return move_cop
    
        
    def ai_play(self):
        #get all possibles moves
        moves = self.get_possible_moves(self.player,self.adversary)
        
        move=False
        
        #select randomly what to play (easy mode)
        #move = random.sample(moves,1)
        
        if self.difficulty == 'easy':
            move = random.choice(moves)
        else:
            if (0,0) in moves:      #select corner first (difficult mode)   0_0,7_7,0_7,7_0
                move = (0,0)
            if (7,7) in moves:
                move = (7,7)
            if (7,0) in moves:
                move = (7,0)
            if (0,7) in moves:
                move = (0,7)

            #Do not move in position to offer corner
            moves = self.do_not_offer_corner(moves)    
            #get biggest impact move
            if not move:
                best = 0
                for poss in self.impact_depth:
                    if poss[2]>best and (poss[0],poss[1]) in moves :
                        best = poss[2]
                        move = poss
            
        return move[0],move[1]
            
    def end_of_game(self):
        btn_ok = Button(text='Ok')

        self.popup = Popup(title='End of game',content=btn_ok, auto_dismiss=False,
                       size_hint=(None, None), size=(Window.width/2,Window.height/2))
        btn_ok.bind(on_press=self.closeback)
        
        self.popup.open()

    def popup_pass_turn(self):
        btn_ok = Button(text='Ok')
        popup = Popup(title='You have to pass your turn' ,content=btn_ok, auto_dismiss=False,
                      size_hint=(None, None), size=(Window.width/2,Window.height/2))

        if self.player == 'X':
            popup.title = 'Computer has to pass turn'
            Clock.schedule_once(popup.dismiss, 3)
            
        btn_ok.bind(on_press=popup.dismiss)
        popup.open()
    
    def closeback(self,btn_instance):
        self.popup.dismiss()
        
    def play(self,x,y):
    
        if  self.in_grid_boundary(x,y) == False or self.grid[x][y] <>' ':
            return False

        if self.possible_move(x,y,self.player,self.adversary) == False:
            return False

        #update logical grid
        self.reverse(x,y)

        #display logical grid
        self.display()

        #swap current player
        moves = self.get_possible_moves(self.adversary,self.player)
        if len(moves)>0:
            self.player, self.adversary = swap(self.player, self.adversary) 
        else:
            moves = self.get_possible_moves(self.player,self.adversary)
            if len(moves)>0:
                self.popup_pass_turn()                #pass, current player has a new turn
            else:
                self.end_of_game()

        self.display_score()

        #trigger timer to wait until display is refreshed
        self.wait_for_display()

    def continue_game(self,dt):
        #anim en cours ?
        if tile.current_flipping == 0:
            
            
            moves = self.get_possible_moves(self.player,self.adversary)
            if len(moves)>0 and self.player == 'X': #if it is computer turn to play
                x,y = self.ai_play()
                self.play(x,y)
            self.b_wait= False  #lock touch for human player              
            return False        #end the scheduling
        
    def wait_for_display(self):
        self.b_wait = True
        Clock.schedule_interval(self.continue_game, 0.1)
        

class MyApp(App):
    def build_config(self, config):
        config.setdefaults('section1', {'difficulty': 'easy','resume':''})

    def on_stop(self):
        resume = ''
        for y in range(0,8):
            for x in range(0,8):
                resume += self.game.grid[y][x]
        resume = resume.replace(' ','_')
        self.config.set('section1', 'resume', resume)
        self.config.write()                  

        
        
    def build(self):
        config = self.config        #config voir config parser
        self.game = Play_ground(caller_instance= self)
        return self.game
		
if __name__ in ( '__main__','__android__'): # au lieu de == '__main__'  nécessite pour fonctionner avec le kivy launcher !!!
    MyApp().run()
