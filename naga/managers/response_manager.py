import threading
import time

class SenderResponse(threading.Thread):
    def __init__(self,naga_game,client_id,name=''):
        super().__init__()
        self.naga_game =naga_game
        self.response_queue= []
        self.client_id = client_id
        self.time = 0
        self.avg_time= 0
        self.counter = 0
        self.status = False
        self.name = name

    def run(self):
        client_id = self.client_id
        naga_game = self.naga_game
        while self.status:
            if self.response_queue:
                try:
                    response = self.response_queue.pop()
                    start = time.time()
                    self.naga_game.game_controller.response(response,client_id,naga_game)
                    end = time.time()
                    self.time += (end-start)
                    #print(len(self.response_queue))
                    self.counter += 1
                    self.avg_time =self.time/self.counter
                except IndexError as e:
                    print(e)
            time.sleep(0.001)

    def print_time_avg(self):
        print('{0} Average: {1}'.format(self.name,self.avg_time))

    def ready(self):
        self.status =True

    def stop(self):
        self.status =False

    def add_response(self,response):
        self.response_queue.insert(0,response)

class ResponseManager(threading.Thread):
    def __init__(self,naga_game):
        super().__init__()
        self.naga_game = naga_game
        self.status = False

        self.sender_list = []
        self.response_queue = []
        pass

    def run(self):
        naga_game = self.naga_game
        i = 1
        for p in naga_game.players:
            sender = SenderResponse(naga_game,p.client_id,'Response thread{}'.format(i))
            self.sender_list.append(sender)
            sender.ready()
            sender.start()
            i+=1

        while self.status:
            if self.response_queue:
#                print(len(self.response_queue))
                response = self.response_queue.pop()
                for sender in self.sender_list:
                    sender.add_response(response)
                #time.sleep(0.0001)
            time.sleep(0.01)

    def add_response(self,response):
        #print(response)
        self.response_queue.insert(0,response)
        #print(self.response_queue)

    def ready(self):
        self.status = True

    def stop(self):
        self.status = False
        for s in self.sender_list:
            s.print_time_avg()
            s.stop()
            s.join()
        self.join()
