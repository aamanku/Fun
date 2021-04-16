#JustForFun
# Written by Abhijeet Kulkarni @amkulk@udel.edu
import pyglet
import numpy as np
import Car_Dynamics

class CarWindow(pyglet.window.Window):
    def __init__(self):
        super(CarWindow, self).__init__(960,960)

        #Set key handler.
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.set_caption("Drifting car")
        self.display_scale = 30
        self.Car_image= pyglet.resource.image("car.png")
        self.time_label = pyglet.text.Label(text="Time = 0 sec", x=0, y=0)
        self.time = 0
        self.dt = 0.001
        self.ini_states = [5,5,0,0,0,0]
        self.CarDynamics=Car_Dynamics.CarDynamics(self.ini_states,self.dt)

        #self.center_image(self.Car_image)
        self.Car_image.anchor_x=self.Car_image.width//2
        self.Car_image.anchor_y=self.Car_image.height*self.CarDynamics.a2/(self.CarDynamics.a1+self.CarDynamics.a2)
        
        self.Car = pyglet.sprite.Sprite(img=self.Car_image, x=0, y=0)
        self.Car.scale = (self.CarDynamics.a1+self.CarDynamics.a2)/self.Car_image.height*self.display_scale
        self.Car.rotation = 90

        
        
        
        self.Fx2 = 0
        self.Fx1 = 0
        self.delta = 0
        self.input_label = pyglet.text.Label(text="delta = 0 degs, RearF = 0 N, FrontF = 0 N", x=10, y=30)
        pyglet.clock.schedule_interval(self.game_tick, self.dt)

        #sounds buildup
        self.buildupplayer = pyglet.media.Player()
        source = pyglet.media.load("buildup.wav")
        self.buildupplayer.queue(source)
        self.buildupplayer.loop=True
        self.buildupplayer.volume = 0.5
        #dejavu
        self.dejavutime = -3
        self.dejavuplayer = pyglet.media.Player()
        source = pyglet.media.load("dejavu.wav")
        self.dejavuplayer.queue(source)
        self.dejavu_text = pyglet.text.Label(text="DEJAVU", x=960//2, y=930)
    def game_tick(self, dt):
        self.draw_elements()

        if ((self.time-self.dejavutime)>2):
            if self.CarDynamics.SLIPPING:
                self.dejavuplayer.play()
                self.buildupplayer.seek(0)
                self.buildupplayer.pause()
                self.dejavutime = self.time
                
            else:
                self.dejavuplayer.seek(0)
                self.dejavuplayer.pause()
                self.buildupplayer.play()
        for _ in range(1,int((dt/self.dt))):
            self.update_Car()
        self.time+=dt

    def draw_elements(self):
        self.clear()
        self.Car.draw()
        self.time_label.draw()
        self.input_label.draw()
        if self.CarDynamics.SLIPPING:
            self.dejavu_text.draw()

    def update_Car(self):
        #update input
        self.Fx1 += (5*int(self.keys[pyglet.window.key.UP])-5*int(self.keys[pyglet.window.key.DOWN]))*int(np.abs(self.Fx1) <5000)
        self.Fx2 = -5000*int(self.keys[pyglet.window.key.SPACE])
        self.delta +=(-np.deg2rad(0.1)*self.keys[pyglet.window.key.LEFT]+np.deg2rad(0.1)*self.keys[pyglet.window.key.RIGHT]) *(np.abs(self.delta) <=np.deg2rad(60))
        if not(self.keys[pyglet.window.key.UP] or self.keys[pyglet.window.key.DOWN]) :
            self.Fx1 =0
        if not(self.keys[pyglet.window.key.LEFT] or self.keys[pyglet.window.key.RIGHT]):
            self.delta =0

        
        #simulate for one step
        self.CarDynamics.sim_step([self.delta,self.Fx1,self.Fx2])
        
        #update graphics
        self.Car.y = self.CarDynamics.states[0]*self.display_scale
        self.Car.x = self.CarDynamics.states[1]*self.display_scale
        self.Car.rotation = np.rad2deg(self.CarDynamics.states[2])
        self.time_label.text = "Time: %0.2f X: %0.3f Y: %0.3f" % (self.CarDynamics.time,self.CarDynamics.states[0],self.CarDynamics.states[1])
        self.input_label.text = "delta = %0.1f degs, RearF = %0.1f N, FrontF = %0.1f N" %(self.delta,self.Fx2,self.Fx1)
        
        if self.keys[pyglet.window.key.R]:
            self.CarDynamics.reset()
        
    
    def center_image(self, image):
        image.anchor_x = image.width/2
        image.anchor_y = image.height/2

    
_= CarWindow()
pyglet.app.run()
