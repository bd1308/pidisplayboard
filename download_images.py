import boto3
import schedule
import os
import pygame
import time
import logging
import sys
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("config.ini")
bucketLocation = config.get('main', 'aws_bucket_name')
fileLocation = config.get('main', 'tmp_file_location')
if config.get('main','log_level') == 'INFO':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)

# Based on code from Adafruit's Framebuffer Python tutorial, but slimmed down
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
        pygame.mouse.set_visible(False)

    def __del__(self):
        "Destructor"


def job():
    try:
        logging.info("[JOB] Running AWS Pi Image Download Job...")
        s3 = boto3.client(
            's3',
            aws_access_key_id=config.get('main', 'aws_access_id'),
            aws_secret_access_key=config.get('main', 'aws_secret_key')
        )
        list = s3.list_objects(Bucket=bucketLocation)['Contents']

        for s3_key in list:
            s3_object = s3_key['Key']
            if not s3_object.endswith("/"):
                s3.download_file(bucketLocation, s3_object, fileLocation + s3_object)
            else:
                import os
                if not os.path_exists(s3_object):
                    os.makedirs(s3_object)
    except:
        logging.warning("[JOB] CANNOT DOWNLOAD IMAGES! Will try next time.")
    logging.info("[JOB] AWS Pi Download Job completed")


def heartbeat():
    logging.info("[HEARTBEAT] Heartbeat Log entry.")

def prep_update_image():
    global filelist
    try:
        item = next(filelist)
    except StopIteration:
        print "caught exception...resetting"
        filelist.seek(0)
        item = next(filelist)
    update_image(item)


def update_image(file_item):
    logging.info("[UPDATE_IMAGE] Updating slideshow image")
    scope.screen.fill((0, 0, 0))
    pygame.display.update()
    itemarray = file_item.split('|')
    name = itemarray[0]
    filename = itemarray[1].rstrip('\n')
    font = pygame.font.SysFont('Arial', 14, bold=True)
    desc = font.render(name, True, pygame.Color(255, 255, 255),
                       pygame.Color('blue'))
    file_data = open(filename, 'r')
    img = pygame.image.load(file_data)
    img = pygame.transform.scale(img, (scope.screen.get_width(),scope.screen.get_height()))
    file_data.close()
    print 'name:' + name
    print scope.screen.get_height()
    print scope.screen.get_width()
    scope.screen.blit(img, (0, 0))
    scope.screen.blit(desc, (0, scope.screen.get_height()-20))
    pygame.display.update()



logging.info("Starting Pull S3 Job.")
scope = pyscope()
job()
filelist = open(fileLocation + 'file_list.txt', 'r')
filelist_iter = iter(filelist)
prep_update_image()
schedule.every(5).minutes.do(job)
schedule.every(1).minutes.do(heartbeat)
schedule.every(config.getint('slideshow', 'slideshow_update_interval')).seconds.do(prep_update_image)



running = True

while running:
    schedule.run_pending()
    time.sleep(1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                filelist.close()
                sys.exit()
filelist.close()
pygame.quit()
