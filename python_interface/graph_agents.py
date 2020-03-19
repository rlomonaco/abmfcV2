import numpy as np
from dominant_region import dom_reg_grid
from bresenham import bresenham
from graph import Graph
import cv2


class Graph_Agents:

    def __init__(self, region):

        self.graph = Graph()
        self.row = 14
        self.col = 20
        self.team_n = 11
        self.pixel_n = self.row * self.col
        self.region = cv2.resize(region, dsize=(self.col, self.row), interpolation=cv2.INTER_CUBIC).astype(int)

        # self.pixels = [f'p{i}' for i in range(self.pixel_n)]
        self.teammates = [f't{j}' for j in range(self.team_n)]

        for r in range(self.row):
            for c in range(self.col):
                self.graph.add_vertex(f'p({r},{c})')

        for t in self.teammates:
            self.graph.add_vertex(t)

        # dest = [-1,+1,-21,-20,-19,+19,+20,+21]
        # initialise graph link between connections
        # for k in range(self.pixel_n):
        #     for l in range(8):
        #         pixel = k+dest[l]
        #         if -1 <= k%self.col-1 and k%self.col+1 <= self.col and k%self.col-1<= pixel%self.col <= k%self.col+1 and 0 <= pixel < self.pixel_n:
        #             self.graph.add_edge(f'p{k}', f'p{pixel}', 1)

        for v in self.graph:
            for w in v.get_connections():
                vid = v.get_id()
                wid = w.get_id()
                print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w)))

        # a = self.graph.find_path('p1', 'p279')
        for v in self.graph:
            print( 'g.vert_dict[%s]=%s' %(v.get_id(), self.graph.vert_dict[v.get_id()]))

if __name__ == '__main__':
    regions = np.load('/home/godfrey/abm-fc/python_interface/saved_heatmaps/regions_0.npy')
    region = regions[:,:,15]
    g = Graph_Agents(region)


