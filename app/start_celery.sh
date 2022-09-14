celery "-A" "crawler.crawler_instance.genbot_service.genbot_controller" "worker" "--concurrency=1" "--pool=gevent" "--loglevel=info" "-Q" "genbot_queue"
