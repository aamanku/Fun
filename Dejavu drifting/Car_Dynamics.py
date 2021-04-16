# Written by Abhijeet Kulkarni @amkulk@udel.edu
import numpy as np

# importing saved dynamics functions
import dill
dill.settings['recurse'] = True
# fF_lateral=dill.load(open("F_contact.dill", "rb"))
fode=dill.load(open("eta_dot.dill", "rb"))

def fF_lateral(states,inputs,a1,a2,C1,C2):
    X,Y,theta,dX,dY,dtheta=states
    delta,Fx1,Fx2=inputs
    vx = (dX*np.cos(theta)+dY*np.sin(theta))
    vy = (-dX*np.sin(theta)+dY*np.cos(theta))
    if np.abs(vx)>0:
        if vx>0:
            Fy1=-C1*(-delta+np.arctan((vy+dtheta*a1)/vx))
            Fy2=-C2*(np.arctan((vy-dtheta*a2)/vx))
        else:
            Fy1=C1*(-delta+np.arctan((vy+dtheta*a1)/vx))
            Fy2=C2*(np.arctan((vy-dtheta*a2)/vx))

    else:
        Fy1 = C1*delta
        Fy2 = 0
    return np.array([Fy1,Fy2])


class CarDynamics():
    def __init__(self,states,dt):
        self.M  = 1000
        self.I  = 1650
        self.a1 = 1.0
        self.a2 = 0.5
        self.C1 = 60000
        self.C2 = 60000
        self.dt = dt
        self.ini_states = states
        self.states = states
        self.time = 0
        self.mu = 0.7
        self.Cf = 10
        self.Cr = 100
        self.SLIPPING = False
    def reset(self):
        self.states = self.ini_states
    
    def friction_forces(self,F_lateral):
        dist = [self.a2/(self.a1+self.a2),self.a1/(self.a1+self.a2)]
        Fy1,Fy2 = F_lateral
        Fy1f = np.min([np.abs(Fy1),self.mu*self.M*9.81*dist[0]])*np.sign(Fy1)
        Fy2f = np.min([np.abs(Fy2),self.mu*self.M*9.81*dist[1]])*np.sign(Fy2)
        if (np.abs(Fy2) !=np.abs(Fy2f)):
            self.SLIPPING = True
        else:
            self.SLIPPING = False
        return [Fy1f,Fy2f]
    
    def damping_forces(self,inputs):
        X,Y,theta,dX,dY,dtheta=self.states
        vx = (dX*np.cos(theta)+dY*np.sin(theta))
        Fx1 = -vx*self.Cf
        Fx2 = -vx*self.Cr
        return [inputs[0],inputs[1]+Fx1,inputs[2]+Fx2]

    def sim_step(self,inputs): #input = [delta,Fx1,Fx2]
        #Damping
        dampedinput = self.damping_forces(inputs)
        #contact force
        F_lateral=fF_lateral(self.states,dampedinput,self.a1,self.a2,self.C1,self.C2).flatten() 
        F_lateral = self.friction_forces(F_lateral)
        #deta
        #adding damping to input in Fx1 and Fx2
        # input[0]
        deta = fode(self.states,dampedinput,F_lateral,self.M,self.I,self.a1,self.a2).flatten()
        self.states = [i*self.dt+s for i,s in zip(deta,self.states)]
        self.time +=self.dt

