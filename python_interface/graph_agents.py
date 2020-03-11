import numpy as np
from dominant_region import dom_reg_grid
from bresenham import bresenham
from graph import Graph
import cv2

class Graph_Agents:

    def __init__(self):

        self.graph = Graph()
        self.row = 14
        self.col = 20
        self.team_n = 11
        self.pixel_n = self.row * self.col
        # self.region = cv2.resize(region, dsize=(self.col, self.row), interpolation=cv2.INTER_CUBIC).astype(int)

        self.pixels = [f'p{i}' for i in range(self.pixel_n)]
        self.teammates = [f't{j}' for j in range(self.team_n)]

        for p in self.pixels:
            self.graph.add_vertex(p)

        for t in self.teammates:
            self.graph.add_vertex(t)

        for k in range(50):
            self.graph.add_edge(f't{np.random.randint(0,10)}', f'p{np.random.randint(0,280)}', np.random.uniform()*1000)

        for v in self.graph:
            for w in v.get_connections():
                vid = v.get_id()
                wid = w.get_id()
                print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w)))

        for v in self.graph:
            print( 'g.vert_dict[%s]=%s' %(v.get_id(), self.graph.vert_dict[v.get_id()]))

if __name__ == '__main__':

    g = Graph_Agents()


