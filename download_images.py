import boto3
import schedule
import os
import pygame
import time
import logging

bucketLocation = 'home-displayboard'
fileLocation = '/tmp/'
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

#Based on code from Adafruit's Framebuffer Python tutorial, but slimmed down
class pyscope:
    screen = None

    def __init__(self):
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
        if not found:
            raise Exception('No suitable driver found!')

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        print "Framebuffer size: %d x %d" % (size[0], size[1])
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()



def job():
    logging.info("[JOB] Running AWS Pi Image Download Job...")
    s3 = boto3.client('s3')
    list = s3.list_objects(Bucket=bucketLocation)['Contents']

    for s3_key in list:
        s3_object = s3_key['Key']
        if not s3_object.endswith("/"):
            s3.download_file(bucketLocation, s3_object, fileLocation+s3_object)
        else:
            import os
            if not os.path_exists(s3_object):
                os.makedirs(s3_object)
    logging.info("[JOB] AWS Pi Download Job completed")

def heartbeat():
    logging.info("[HEARTBEAT] Heartbeat Log entry.")

logging.info("Starting Pull S3 Job.")
job()
schedule.every(5).minutes.do(job)
schedule.every(1).minutes.do(heartbeat)
scope = pyscope()




while 1:
    schedule.run_pending()
    time.sleep(1)
    scope.screen.fill(0,0,0)
    scope.screen.update()
    filelist = open(fileLocation + 'file_list.txt', 'r')
    for item in filelist:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        itemarray = item.split('|')
        name = itemarray[0]
        filename = itemarray[1].rstrip('\n')
        img = pygame.image.load(filename)
        scope.screen.blit(img, (0, 0))
        pygame.display.update()
        time.sleep(5)
    filelist.close()







