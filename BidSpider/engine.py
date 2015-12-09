"""
Engine模块

爬虫引擎，承担以下职责：
1.爬虫的启动、与停止
1.加载自定义模块
2.使用EventLoop进行驱动
3.协调各模块，控制数据流动
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from spider import Item, Spider
from pipeline import BasePipeline
from page_fetcher import PageFetcher, WDManagerWithSemaphore, SpiderLabeledRequest, Request
from util import list_subclasses_in_specific_module, import_a_name_from_a_module

# CONFIG_INFO
# -------------------------------------
DEBUG_MODE = False
LOGGING = False

REQUEST_QUEUE_SIZE = 20

CONSUME_FREQUENCY = 1
SHUTDOWN_DETECTION_FREQUENCY = 10
SHUTDOWN_DETECTION_THRESHOLD = 30

EXECUTOR_POOL_SIZE = 2
WEB_DRIVER_REDUNDANCY = 1

CUSTOM_SPIDER_SCRIPT_NAME = 'spiders'
CUSTOM_PIPELINE_SCRIPT_NAME = 'pipelines'
CUSTOM_PIPELINE_WEIGHT_NAME = 'pipelines.ITEM_PIPELINES'

WEB_DRIVER_LOG_PATH = './log/web_driver_log/'
# -------------------------------------


# EventLoop
# -------------------------------------
loop = asyncio.get_event_loop()
if DEBUG_MODE:
    loop.set_debug(True)
# -------------------------------------


# Queues
# -------------------------------------
request_queue = asyncio.Queue(REQUEST_QUEUE_SIZE)
# -------------------------------------


# Facilities
# -------------------------------------
executor = \
    ThreadPoolExecutor(EXECUTOR_POOL_SIZE)

webdriver_manager = \
    WDManagerWithSemaphore(EXECUTOR_POOL_SIZE + WEB_DRIVER_REDUNDANCY,
                           log_path=WEB_DRIVER_LOG_PATH)

page_fetcher = PageFetcher(loop, executor, webdriver_manager)
# -------------------------------------


# Task
# -------------------------------------
@asyncio.coroutine
def task(req):
    global page_fetcher
    global request_queue

    print('launching task')
    response = yield from page_fetcher.do_fetching(req)
    print('task get response')

    for obj in req.spider.parse(response.content):
        if isinstance(obj, Request):
            print('spider generate Request')
            req_with_spider = SpiderLabeledRequest(req.spider, obj)
            yield from request_queue.put(req_with_spider)
        if isinstance(obj, Item):
            print('spider generate Item')
            go_through_pipeline(obj, req.spider)
            print('task over')

    return
# -------------------------------------


# Request Producer and Consumer
# -------------------------------------
@asyncio.coroutine
def producer(spider_obj):
    global request_queue

    for url in spider_obj.start_urls:
        req = SpiderLabeledRequest(spider_obj, Request(url))
        print('produce')
        yield from request_queue.put(req)


@asyncio.coroutine
def consumer():
    global loop

    while True:
        req = yield from request_queue.get()
        print('consume')
        asyncio.async(task(req), loop=loop)
        yield from asyncio.sleep(CONSUME_FREQUENCY)


def create_and_schedule_producer():
    # 导入自定义的spider类
    spider_cls_list = \
        list_subclasses_in_specific_module(CUSTOM_SPIDER_SCRIPT_NAME, Spider)

    # 将spider类列表中的类进行实例化
    spider_inst_list = [spider_cls() for spider_cls in spider_cls_list]

    # 为每个spider创建一个producer并交给EventLoop执行
    for spider_inst in spider_inst_list:
        asyncio.async(producer(spider_inst), loop=loop)

    return


def schedule_consumer():
    global loop
    asyncio.async(consumer(), loop=loop)
# -------------------------------------


# Spider Item Pipeline
# -------------------------------------
def create_pipeline():
    # 将自定义的pipeline的子类，按照(cls_name, cls_obj)的list返回
    pipeline_cls_tuple_list = \
        list_subclasses_in_specific_module(CUSTOM_PIPELINE_SCRIPT_NAME,
                                           BasePipeline,
                                           tuple_with_cls_name=True)
    # 获取自定义的pipeline_weight
    pipeline_weight = import_a_name_from_a_module(CUSTOM_PIPELINE_WEIGHT_NAME)

    # 对pipeline_cls_tuple_list按照pipeline_weight中的权重排序
    pipeline_cls_tuple_list.sort(key=(lambda item: pipeline_weight[item[0]]))

    # 排序后按照顺序依次实例化，并按顺序组成list
    pipeline_insts = [cls_tuple[1]() for cls_tuple in pipeline_cls_tuple_list]

    return pipeline_insts


pipeline_instances = create_pipeline()


def go_through_pipeline(item, spider):
    global pipeline_instances

    # 依次调用process_item
    for pl_inst in pipeline_instances:
        pl_inst.process_item(item, spider)

    return
# -------------------------------------


# Start&Stop
# -------------------------------------
def start():
    global loop
    asyncio.async(stop_detector(), loop=loop)
    create_and_schedule_producer()
    schedule_consumer()
    loop.run_forever()
    loop.close()


def stop():
    global webdriver_manager

    loop = asyncio.get_event_loop()
    loop.stop()
    webdriver_manager.release()


@asyncio.coroutine
def stop_detector():
    global request_queue
    global SHUTDOWN_DETECTION_FREQUENCY
    global SHUTDOWN_DETECTION_THRESHOLD

    counter = 0
    counter_threshold \
        = SHUTDOWN_DETECTION_THRESHOLD/SHUTDOWN_DETECTION_FREQUENCY

    while True:
        print('STOP-DETECT')
        if request_queue.qsize():
            counter = 0
        else:
            counter += 1
            if counter == counter_threshold:
                break

        yield from asyncio.sleep(SHUTDOWN_DETECTION_FREQUENCY)

    stop()


if __name__ == '__main__':
    start()
