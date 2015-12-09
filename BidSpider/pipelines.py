from pipeline.pipeline import BasePipeline


ITEM_PIPELINES = {
    'PrintPipeline': 2,
    'TestPipeline': 1
}


class PrintPipeline(BasePipeline):
    def process_item(self, item, spider):
        print('PrintPipeline')
        print('receive ' + spider.name + ':::', item)


class TestPipeline(BasePipeline):
    def process_item(self, item, spider):
        print('TestPipeline')
